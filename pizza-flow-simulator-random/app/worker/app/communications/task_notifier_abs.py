''' Abstract class to send tasks status to serverr '''
from abc import ABC
from models.task_execution import TaskExecution

class TaskStatusNotifierProvider(ABC):
    ''' Abstract class to notify task status '''
    def notify_status(self, execution: TaskExecution) -> None:
        ''' Get tasks from the provider '''
        raise NotImplemented()
