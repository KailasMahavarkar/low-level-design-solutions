from typing import List
from .redis import OperationPersistorRedis
from models.operations import Operation
from .database import get_db

redis = OperationPersistorRedis()

def load_persisted_operation(operation_id: str) -> Operation:
    ''' Load a persisted operation '''
    operation = redis.load(operation_id)
    if not operation:
        with get_db() as db:
            operation = db.query(Operation).filter(Operation.uuid == operation_id).first()
    return operation

def persist_operation(operation: Operation) -> Operation:
    ''' Persist an operation '''
    redis.save(operation)
    with get_db() as db:
        existing_operation = db.get(Operation, operation.uuid)
        if not existing_operation:
            db.add(operation)
            db.commit()
            db.refresh(operation)
            return operation
        existing_operation.sqlmodel_update(operation.model_dump())
        db.add(existing_operation)
        db.commit()
        db.refresh(existing_operation)
    return existing_operation

def load_persisted_operations_filtering(**params) -> List[Operation]:
    ''' Load operations with filters '''
    try:
        return redis.get(**params)
    except Exception as e:
        with get_db() as db:
            base_query = db.query(Operation)
            if params.get('status'):
                base_query = base_query.filter(Operation.status.in_(params.get('status')))
            if params.get('limit'):
                base_query = base_query.limit(params.get('limit'))
            return base_query.all()
    
def delete_persisted_operation(operation_id: str):
    ''' Delete a persisted operation '''
    redis.delete(operation_id)
    with get_db() as db:
        operation = db.query(Operation).filter(Operation.uuid == operation_id).first()
        if operation:
            db.delete(operation)
            db.commit()
