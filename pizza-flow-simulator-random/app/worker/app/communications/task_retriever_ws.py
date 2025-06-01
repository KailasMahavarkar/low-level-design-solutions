''' Task Retriever HTTP module '''
from typing import List, Any
from .task_retriever_abs import TaskRetrieverProvider
from config import AWS_DEFAULT_REGION
from models.tasks import Task
from models.task_execution import TaskExecution
from logs import logger

class TaskRetrieverWS(TaskRetrieverProvider):
    ''' Task Retriever HTTP class '''
    registry = None
    pending_tasks = []
    task_callback = None
    ws = None

    def __init__(self, sio: Any, registry: Any):
        self.registry = registry
        sio.on('task', self.on_task, namespace='/worker')
        self.ws = sio

    def get_tasks(self):
        ''' Get tasks from the provider '''
        self.ws.emit('get_tasks', namespace='/worker')

    def on_task(self, task):
        logger.debug(f"[WS] Received task from the server: {task}")
        try:
            task_execution = TaskExecution(**task)
            if task_execution.region != AWS_DEFAULT_REGION:
                logger.debug(f"Task {task_execution.task_id} is not for this region, discarded")
                return
                
            # Map task_id values to task identifiers
            task_id_to_name = {
                '1': 'make_dough',
                '2': 'add_toppings',
                '3': 'bake_pizza',
                '4': 'deliver_pizza'
            }
            
            # Get the task name from the mapping
            task_name = task_id_to_name.get(task_execution.task_id)
            if not task_name:
                logger.error(f"Unknown task_id: {task_execution.task_id}")
                return
            
            # Get the task from registry using the name
            task_class = self.registry.get_task_with_id(task_name)
            rt = task_class(task_execution)
            
            if self.task_callback:
                self.task_callback(rt)
            else:
                self.pending_tasks.append(rt)
        except Exception as e:
            logger.error(f"Error processing task: {e}, discarded")

    def set_callback(self, callback):
        self.task_callback = callback