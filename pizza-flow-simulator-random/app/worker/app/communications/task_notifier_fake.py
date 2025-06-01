''' Fake task notififcation provider '''
from communications.task_notifier_abs import TaskStatusNotifierProvider
from models.task_execution import TaskExecution
from logs import logger
import json

class TaskStatusNotifierFake(TaskStatusNotifierProvider):
    ''' Fake task notififcation provider '''
    def notify_status(self, execution: TaskExecution) -> None:
        ''' Notify the task status '''
        logger.info(f'Notifying task {execution.task_id} with status {execution.status}')
        logger.debug(f'Execution details: {json.dumps(execution.model_dump(), indent=4)}')
        