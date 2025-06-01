import redis
import os
from models.operations import Operation
from models.tasks import Task
from typing import List
import json
from redis.commands.search.query import Query

redis_client = None
if os.getenv('REDIS_HOST'):
    redis_client = redis.Redis(host=os.getenv('REDIS_HOST'), port=6379, db=0)

class OAuthPersistorRedis():
    ''' Redis DB to persist OAuth '''
    
    def persist_oauth_start(self, key: str, value: str, ttl: int) -> bool:
        ''' Save OAuth to redis '''
        redis_client.setex(f'oauth.{key}', ttl, value)
        return True
    
    def get_oauth_start(self, key: str) -> str:
        ''' Load RFA from redis '''
        return redis_client.get(f'oauth.{key}')
    
    def delete_oauth_start(self, uuid: str) -> None:
        ''' Delete RFA from dynamodb '''
        redis_client.delete(f'oauth.{uuid}')

class OperationPersistorRedis():
    ''' Redis to persist operations '''
    def save(self, operation: Operation) -> None:
        ''' Save operation to redis '''
        if not redis_client:
            return
        redis_client.json().set(f'operations.{str(operation.uuid)}', '.', operation.model_dump())
    
    def load(self, uuid: str) -> Operation:
        ''' Load operation from redis '''
        if not redis_client:
            return None
        #operation = redis_client.get(f'operations.{uuid}')
        operation = redis_client.json().get(f'operations.{uuid}')
        if not operation:
            return None
        return Operation(**operation)
    
    def load_filtering(self, limit: int = 10, status: List[str] = []) -> List[Operation]:
        ''' Load operations with filters '''
        if not redis_client:
            return []
        qs = ''
        if status:
            status_vals = '|'.join(status)
            qs += f'@status:{{{status_vals}}} '
        if not qs:
            qs = '*'
        query = Query(qs).paging(0, limit).sort_by('start_date', asc=False)
        result = redis_client.ft('ops_status').search(query)
        return [Operation(**json.loads(doc.json)) for doc in result.docs]
    
    def delete(self, uuid: str) -> None:
        ''' Delete operation from redis '''
        if not redis_client:
            return
        redis_client.delete(f'operations.{uuid}')
        redis_client.delete(f'operations.{uuid}.tasks')

class TaskPersistorRedis():
    ''' Redis to persist tasks '''
    def save(self, task: Task) -> None:
        ''' Save task to redis '''
        if not redis_client:
            return
        redis_client.json().set(f'tasks.{task.uuid}', '.', task.model_dump())
        redis_client.sadd(f'operations.{task.operation_id}.tasks', task.uuid)

    def load(self, uuid: str) -> Task:
        ''' Load task from redis '''
        if not redis_client:
            return None
        task = redis_client.json().get(f'tasks.{uuid}')
        if not task:
            return None
        return Task(**task)
    
    def load_by_operation(self, operation_id: str) -> List[Task]:
        ''' Load tasks by operation from redis '''
        if not redis_client:
            return []
        task_ids = redis_client.smembers(f'operations.{operation_id}.tasks')
        tasks = [self.load(task_id.decode()) for task_id in task_ids]
        return tasks
    
    def delete(self, uuid: str) -> None:
        ''' Delete task from redis '''
        if not redis_client:
            return
        task = self.load(uuid)
        redis_client.srem(f'operations.{task.operation_uuid}.tasks', uuid)
        redis_client.delete(f'tasks.{uuid}')

    def load_pending_for_worker(self, region: str) -> list:
        ''' Load tasks for a worker '''
        if not redis_client:
            raise Exception('Redis not configured')
        region_sanitized = region.replace('-', '\\-')
        pending = redis_client.ft('task_status').search(f'@region:{{{region_sanitized}}} @status:{{pending|waiting}}')
        return [Task(**json.loads(doc.json)) for doc in pending.docs]

    def load_filtering(self, status: List[str] = [], limit: int = 10) -> List[Task]:
        ''' Load Tasks with filters '''
        if not redis_client:
            return []
        qs = ''
        if status:
            status_vals = '|'.join(status)
            qs += f'@status:{{{status_vals}}} '
        if not qs:
            qs = '*'
        query = Query(qs).paging(0, limit).sort_by('start_date', asc=False)
        result = redis_client.ft('task_status').search(query)
        return [Task(**json.loads(doc.json)) for doc in result.docs]
    
    def delete(self, uuid: str) -> None:
        ''' Delete task from redis '''
        if not redis_client:
            return
        try:
            task = self.load(uuid)
            if task.operation_id:
                redis_client.srem(f'operations.{task.operation_id}.tasks', uuid)
            redis_client.delete(f'tasks.{uuid}')
        except Exception as e:
            pass

class WSAuthPersistorRedis():
    ''' Redis DB to persist OAuth '''
    
    def persist(self, sid: str, user_id: str) -> bool:
        ''' Save OAuth to redis '''
        redis_client.set(f'ws_user.{sid}', user_id)
        return True
    
    def get(self, key: str) -> str:
        ''' Load RFA from redis '''
        return redis_client.get(f'ws_user.{key}').decode()
    
    def delete(self, uuid: str) -> None:
        ''' Delete RFA from dynamodb '''
        redis_client.delete(f'ws_user.{uuid}')
