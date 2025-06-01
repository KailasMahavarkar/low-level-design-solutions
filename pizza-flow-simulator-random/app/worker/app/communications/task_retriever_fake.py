''' Fake Task Retriever module, to be used in development '''
from typing import List, Any
from .task_retriever_abs import TaskRetrieverProvider
from models.tasks import Task
from logs import logger

def gen_create_ns():
    ''' Generate a database create task '''
    identifier = 'cluster_create.namespace'
    parameters = {'name': f'mycluster', 'labels': {'owner': 'federico'}, 'customer_group': 'cg-1'}
    return (identifier, parameters)
def gen_db_create_db():
    ''' Generate a database create task '''
    identifier = 'cluster_create.database'
    parameters = {'name': f'mycluster', 'labels': {'owner': 'federico'}, 'customer_group': 'cg-1'}
    return (identifier, parameters)
def gen_db_wait_task():
    ''' Generate a database create task '''
    identifier = 'cluster_create.database_wait_create'
    parameters = {'name': f'mycluster', 'labels': {'owner': 'federico'}, 'customer_group': 'cg-1'}
    return (identifier, parameters)
def gen_db_user_task():
    ''' Generate a database create task '''
    identifier = 'cluster_create.database_create_user'
    parameters = {'name': f'mycluster', 'labels': {'owner': 'federico'}, 'customer_group': 'cg-1'}
    return (identifier, parameters)
def gen_db_service():
    ''' Generate a database create task '''
    identifier = 'cluster_create.database_service'
    parameters = {'name': f'mycluster', 'labels': {'owner': 'federico'}, 'customer_group': 'cg-1'}
    return (identifier, parameters)
def gen_db_disk():
    ''' Generate a database create task '''
    identifier = 'cluster_create.database_disk'
    parameters = {'name': f'mycluster', 'labels': {'owner': 'federico'}, 'customer_group': 'cg-1', 'size': 1}
    return (identifier, parameters)
def gen_db_secret():
    ''' Generate a database create task '''
    identifier = 'cluster_create.database_secret'
    parameters = {'name': f'mycluster', 'labels': {'owner': 'federico'}, 'customer_group': 'cg-1'}
    return (identifier, parameters)
def gen_jwt():
    ''' Generate a database create task '''
    identifier = 'cluster_create.jwt'
    parameters = {'name': f'mycluster', 'labels': {'owner': 'federico'}, 'customer_group': 'cg-1'}
    return (identifier, parameters)
def gen_es_create_task():
    ''' Generate a database create task '''
    identifier = 'cluster_create.elasticsearch_instance'
    parameters = {'name': f'mycluster', 'labels': {'owner': 'federico'}, 'customer_group': 'cg-1'}
    return (identifier, parameters)
def gen_es_wait_task():
    ''' Generate a database create task '''
    identifier = 'cluster_create.elasticsearch_wait_create'
    parameters = {'name': f'mycluster', 'labels': {'owner': 'federico'}, 'customer_group': 'cg-1'}
    return (identifier, parameters)
def gen_es_user():
    ''' Generate a database create task '''
    identifier = 'cluster_create.elasticsearch_create_user'
    parameters = {'name': f'mycluster', 'labels': {'owner': 'federico'}, 'customer_group': 'cg-1'}
    return (identifier, parameters)
def gen_es_disk():
    ''' Generate a database create task '''
    identifier = 'cluster_create.elasticsearch_disk'
    parameters = {'name': f'mycluster', 'labels': {'owner': 'federico'}, 'customer_group': 'cg-1', 'size': 5}
    return (identifier, parameters)
def gen_app_config():
    ''' Generate a database create task '''
    identifier = 'cluster_create.app_config'
    parameters = {'name': f'mycluster', 'labels': {'owner': 'federico'}, 'customer_group': 'cg-1', 'dns': 'demo.pop-1.getcollate.cloud', 'ingestion_image': '654654563640.dkr.ecr.us-east-2.amazonaws.com/collate-ingestion-slim:1.3.2-rc1', 'admin_principals': '[admin]'}
    return (identifier, parameters)
def gen_app_deploy():
    ''' Generate a database create task '''
    identifier = 'cluster_create.app_deployment'
    parameters = {'name': f'mycluster', 'labels': {'owner': 'federico'}, 'customer_group': 'cg-1', 'dns': 'demo.pop-1.getcollate.cloud', 'image': '654654563640.dkr.ecr.us-east-2.amazonaws.com/collate-server:1.3.2-rc1', 'migrate_args': ''}
    return (identifier, parameters)
def gen_app_service():
    ''' Generate a database create task '''
    identifier = 'cluster_create.app_service'
    parameters = {'name': f'mycluster', 'labels': {'owner': 'federico'}, 'customer_group': 'cg-1', 'dns': 'demo.pop-1.getcollate.cloud'}
    return (identifier, parameters)

class TaskRetrieverFake(TaskRetrieverProvider):
    ''' Task Retriever HTTP class '''
    registry = None
    def __init__(self, registry: Any) -> None:
        self.registry = registry
    
    def get_tasks(self) -> List[Task]:
        ''' Get tasks from the provider '''
        tasks = []
        fns = [gen_create_ns, gen_db_service, gen_db_disk, gen_db_secret, gen_db_create_db, gen_db_wait_task, gen_db_user_task]
        fns += [gen_es_disk, gen_es_create_task, gen_es_wait_task, gen_es_user, gen_jwt]
        fns += [gen_app_service, gen_app_config, gen_app_deploy]
        for fn in fns:
            task_id, params = fn()
            try:
                task = self.registry.get_task_with_id(task_id)()
                task.parameters = params
                tasks.append(task)
            except NotImplementedError:
                logger.error(f'No task found with id {task_id}')
                continue
        return tasks
