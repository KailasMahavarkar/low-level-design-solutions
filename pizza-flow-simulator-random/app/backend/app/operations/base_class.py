from models.operations import Operation, OperationStatus
from models.tasks import Task, TaskStatus
from persistance.tasks import persist_task, load_tasks_for_operation, delete_persisted_task
from persistance.operations import load_persisted_operation, persist_operation, delete_persisted_operation
from typing import Any
from uuid import uuid4
import datetime
import requests
from logs import logger
from ws import ws

class OperationBase:
    ''' Base class for operations '''
    identifier: str
    all_tasks: list[str]

    def __init__(self, op_uuid: str):
        ''' Initialize the operation '''
        self.uuid = op_uuid

    async def start(self, parameters: dict, rfa_id: str = None) -> Operation:
        ''' Start the operation '''
        raise NotImplementedError('Start method not implemented')
    
    async def cancel(self, operation: Operation):
        ''' Cancel the operation '''
        if operation.status not in [OperationStatus.pending, OperationStatus.paused, OperationStatus.errored]:
            raise Exception(f'Operation {operation.uuid} is not pending')
        operation.status = OperationStatus.cancelled
        self.save_operation(operation)
        await self.cancel_tasks(operation.parameters, operation.uuid)

    async def pause(self, operation: Operation):
        ''' Cancel the operation '''
        if operation.status not in [OperationStatus.running]:
            raise Exception(f'Operation {operation.uuid} is not running')
        operation.status = OperationStatus.paused
        self.save_operation(operation)
        await self.pause_tasks(operation.parameters, operation.uuid)

    def delete_operation(self, operation: Operation, force: bool = False):
        ''' Delete the operation '''
        if operation.status not in [OperationStatus.cancelled, OperationStatus.completed, OperationStatus.errored] and not force:
            raise Exception(f'Operation {operation.uuid} is not cancelled')
        self.delete_tasks(operation.uuid)
        delete_persisted_operation(operation.uuid)
    
    async def on_task_complete(self, task: Task):
        ''' Task completed, schedule next task '''
        operation = self.get_operation(task.operation_id)
        
        # Update self status
        if operation.status is OperationStatus.pending:
            operation.status = OperationStatus.running
        logger.info(f'Operation {operation.uuid} running')
        # Get information to schedule next tasks
        db_tasks = self.get_operation_tasks(task.operation_id)
        completed_tasks_ids = [t.task for t in db_tasks if t.status == 'completed']
        pending_tasks = [t for t in self.all_tasks if t not in [t.task for t in db_tasks]]
        
        # Schedule the next tasks
        for task_id in pending_tasks:
            dependencies = self.dependencies_for(task_id)
            if all([dependency_name in completed_tasks_ids for dependency_name in dependencies]): # All dependencies are completed
                next_task = Task(
                    task_id=len(db_tasks) + 1,  # Increment task ID
                    operation_id=task.operation_id,
                    region=task.region,  # Use the same region as the completed task
                    status=TaskStatus.pending,
                    task=task_id,
                    parameters=operation.parameters
                )
                await self.save_task(next_task)
        # Check if all tasks are completed
        db_tasks = self.get_operation_tasks(task.operation_id) # Refresh the tasks with the new generated ones
        if all([t.status == 'completed' for t in db_tasks]):
            operation.status = OperationStatus.completed
            operation.end_date = datetime.datetime.now()
            logger.info(f'Operation {operation.operation} completed')
            await self.on_all_task_completed(operation)
        self.save_operation(operation)
        await self.send_ws_update(operation)

    async def on_all_task_completed(self, operation: Operation) -> None:
        ''' All tasks completed '''
        return
    
    async def on_task_error(self, task: Task):
        ''' Task errored '''
        operation = self.get_operation(task.operation_id)
        operation.status = OperationStatus.errored
        print(f'Operation {operation.operation} errored')
        self.save_operation(operation)
        return task

    def dependencies_for(self, task_id: str):
        '''
        Get the dependencies for a task.
        Given a task name, return the name of the tasks that need to be completed before it can start
        ie {'task1': ['task2', 'task3']} -> Task1 has to be executed after task2 and task3
        '''
        deps = {}
        return deps.get(task_id, [])
    
    async def cancel_tasks(self, parameters: Any, operation_uuid: str):
        ''' Cancel the tasks '''
        tasks = self.get_operation_tasks(operation_uuid)
        for task in tasks:
            if task.status == 'pending':
                task.status = 'cancelled'
                await self.save_task(task)

    async def pause_tasks(self, parameters: Any, operation_uuid: str):
        ''' Cancel the tasks '''
        tasks = self.get_operation_tasks(operation_uuid)
        for task in tasks:
            if task.status == 'pending':
                task.status = 'paused'
                await self.save_task(task)
    
    def delete_tasks(self, operation_uuid: str):
        ''' Delete the tasks '''
        tasks = self.get_operation_tasks(operation_uuid)
        for task in tasks:
            delete_persisted_task(task.uuid)
    
    def save_operation(self, operation: Operation) -> Operation:
        ''' Save the operation '''
        return persist_operation(operation)

    def get_operation(self, uuid: str) -> Operation:
        ''' Get the operation '''
        return load_persisted_operation(uuid)

    def get_operation_tasks(self, operation_uuid: str) -> list[Task]:
        ''' Get the operation tasks '''
        return load_tasks_for_operation(operation_uuid)

    async def save_task(self, task: Task) -> Task:
        ''' Save the task '''
        persisted_task = persist_task(task)
        if persisted_task.status == TaskStatus.pending:
           await ws.emit('task', persisted_task.model_dump(), namespace='/worker')
        await ws.emit('task_update', persisted_task.model_dump())
        return persisted_task
    
    def gen_operation_uuid(self):
        ''' Generate a UUID for an operation '''
        return str(uuid4())
        
    async def send_ws_update(self, operation: Operation) -> None:
        ''' Send a slack notification '''
        try:
            if not operation:
                return
            payload = {"operation": operation.model_dump()}
            await ws.emit('operation_update', payload)

        except Exception as e:
            logger.error(f'Could not send ws update for Operation: {e}')
            return
