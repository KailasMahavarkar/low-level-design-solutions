from typing import List
from .redis import TaskPersistorRedis
from models.tasks import Task, TaskStatus
from .database import get_db
from logs import logger

cache = TaskPersistorRedis()

def load_persisted_task(uuid: str) -> Task:
    ''' Load a persisted task '''
    task = cache.load(uuid)
    if not task:
        with get_db() as db:
            task = db.query(Task).filter(Task.uuid == uuid).first()
    return task

def persist_task(task: Task):
    ''' Persist a task '''
    cache.save(task)
    with get_db() as db:
        existing_task = db.get(Task, task.uuid)
        if not existing_task:
            db.add(task)
            db.commit()
            db.refresh(task)
            return task
        existing_task.sqlmodel_update(task.model_dump())
        db.add(existing_task)
        db.commit()
        db.refresh(existing_task)
        return existing_task

def load_tasks_for_operation(operation_id: str) -> List[Task]:
    ''' Load tasks for an operation '''
    #try:
    #    return cache.load_by_operation(operation_id)
    #except Exception as e:
    with get_db() as db:
        return db.query(Task).filter(Task.operation_id == operation_id).all()

def load_pending_tasks_for_region(region_id: str) -> List[Task]:
    ''' Load pending tasks for a region '''
    try:
        return cache.load_pending_for_region(region_id)
    except Exception as e:
        with get_db() as db:
            return db.query(Task).filter(Task.region == region_id, Task.status.in_([TaskStatus.pending, TaskStatus.waiting])).all()

def delete_persisted_task(task_id: str):
    ''' Delete a persisted task '''
    cache.delete(task_id)
    with get_db() as db:
        task = db.query(Task).filter(Task.uuid == task_id).first()
        if task:
            db.delete(task)
            db.commit()
