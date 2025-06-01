''' PoP Controller'''
import datetime
from typing import List
from functools import cmp_to_key
from persistance.tasks import load_persisted_task, persist_task, load_pending_tasks_for_region, delete_persisted_task
from persistance.operations import load_persisted_operation
from models.tasks import Task, TaskStatus
from operations import get_operation_controller
from logs import logger
from ws import ws
import traceback

class AlreadyRunningException(Exception):
    ''' Task already running '''
class OperationNotFoundException(Exception):
    ''' Operation not found '''

def sort_tasks_by_priority(task1: Task, task2: Task) -> int:
    ''' Compare tasks '''
    # Prioritize non-pending tasks
    if task1.status != task2.status:
        if task1.status in (TaskStatus.pending):
            return -1 # Task 2 wins
        if task2.status in (TaskStatus.pending):
            return 1  # Task 1 wins
        return 0
    # Prioritize tasks with older last_refresh
    now = datetime.datetime.now()
    t1_time = task1.last_refresh or now
    t2_time = task2.last_refresh or now
    if t1_time < t2_time:
        return 1
    if t1_time > t2_time:
        return -1
    # Prioritize older tasks
    t1_time = task1.started_at or now
    t2_time = task2.started_at or now
    if t1_time < t2_time:
        return 1
    if t1_time > t2_time:
        return -1
    return 0

def prioritize_tasks(tasks: List[Task]) -> List[Task]:
    ''' Prioritize tasks '''
    logger.debug(f'Prioritizing tasks: {tasks}')
    prioritized_tasks = []
    for i, task in enumerate(tasks):
        is_waiting = task.status is TaskStatus.pending_wait
        wait_time = task.wait_time or 30
        wait_timedelta = datetime.datetime.now() - datetime.timedelta(seconds=wait_time)
        is_recent = (task.last_refresh or datetime.datetime.now()) > wait_timedelta
        if is_waiting and (task.last_refresh is not None) and is_recent:
            continue
        else:
            prioritized_tasks.append(task)

    sorted_tasks = sorted(prioritized_tasks, key=cmp_to_key(sort_tasks_by_priority))
    logger.debug(f'Sorted tasks: {sorted_tasks}')
    return sorted_tasks

async def get_tasks_for_region(region: str) -> List[Task]:
    ''' Get tasks for a region worker '''
    tasks = load_pending_tasks_for_region(region)
    if tasks:
        return prioritize_tasks(tasks)
    return []

async def send_task_update(task: Task):
    ''' Send task update '''
    try:
        payload = {}
        if task:
            payload["task"] = task.model_dump()
        await ws.emit('task_update', payload)

    except Exception as e:
        logger.error(f'Could not send ws update for task: {e}')
        return

async def on_task_errored(task: Task):
    ''' Task errored '''
    operation = load_persisted_operation(task.operation_id)
    ctl = get_operation_controller(operation.operation)
    if not ctl:
        raise OperationNotFoundException('Operation not found')
    await ctl.on_task_error(task)
    
async def on_task_complete(task: Task):
    ''' Task completed '''
    if not task.operation_id:
        return delete_persisted_task(task.uuid)
    operation = load_persisted_operation(task.operation_id)
    ctl = get_operation_controller(operation.operation)
    if not ctl:
        raise OperationNotFoundException('Operation not found')
    try:
        await ctl.on_task_complete(task)
    except Exception as e:
        logger.error(f'Error in managing task completion: {e}')        
        logger.exception(traceback.print_exc())

async def on_task_notify(execution: Task):
    ''' Task notification from worker '''
    task = load_persisted_task(execution.uuid)
    if not task:
        logger.error(f'Task {execution.uuid} not found in DB')
        raise OperationNotFoundException('Task not found')
    if execution.status is TaskStatus.running and execution.started_at != task.started_at:
        if task.status is not TaskStatus.pending:
            logger.error(f'Task {execution.uuid} already running')
            raise AlreadyRunningException('Task already running')
        task.started_at = execution.started_at
        task.status = TaskStatus.running
    else:
        task.started_at = execution.started_at or datetime.datetime.now()
        task.completed_at = execution.completed_at
        task.result = execution.result
        task.error = execution.error
        if isinstance(execution.status, str):
            task.status = TaskStatus(execution.status)
        else:
            task.status = execution.status
        task.wait_time = execution.wait_time
        task.max_wait_time = execution.max_wait_time
        if execution.last_refresh:
            task.last_refresh = execution.last_refresh
    logger.info(f'Task {task.uuid} updated with status {task.status}, persisting')
    persist_task(task)
    await send_task_update(task)
    if execution.status == TaskStatus.completed:
        await on_task_complete(task)
    if execution.status == TaskStatus.errored:
        await on_task_errored(task)
    return {"status": "ok"}
