''' Websockets notififcation provider '''
from .task_notifier_abs import TaskStatusNotifierProvider
from models.task_execution import TaskExecution
from typing import Any
import json
from logs import logger
import time

class TaskStatusNotifierWS(TaskStatusNotifierProvider):
    ''' Websockets notififcation provider '''
    
    def __init__(self, ws: Any):
        self.ws = ws

    def notify_status(self, execution: TaskExecution) -> None:
        ''' Notify the task status '''
        logger.info(f'Notifying task {execution.task_id}')
        logger.debug(f'Execution details: {json.dumps(execution.model_dump(), indent=4)}')
        def callback(*args):
            logger.debug(f"Task {execution.task_id} acknowledged by server with {args}")
        try:
            self.ws.emit('task_result', data=execution.model_dump(), namespace='/worker', callback=callback)
        except Exception as e:
            logger.error(f"Error notifying task: {execution.task_id} {e}. Will retry in 30s")
            time.sleep(30)
            self.notify_status(execution)
