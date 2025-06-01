''' Task model '''
from communications.task_notifier_abs import TaskStatusNotifierProvider
from communications.task_notifier_http import send_task_result_http
from .task_execution import TaskExecution, TaskStatus
import datetime
import traceback
from logs import logger

class Task:
    ''' Base Task class '''
    identifier: str
    parameters: dict | None = {}
    max_retries: int | None = None
    notifier: TaskStatusNotifierProvider | None = None

    def __init__(self, execution: TaskExecution = None):
        ''' Initialize the task '''
        if execution:
            self.execution = execution
            self.parameters = execution.parameters
            
    def execute(self, notifier: TaskStatusNotifierProvider = None) -> TaskExecution:
        ''' Execute the task '''
        self.notifier = notifier
        logger.info(f'Executing task {self.identifier}. Parameters: {self.execution.parameters}')
        logger.info(f'Current status: {self.execution.status}')
        logger.info(f'Result: {self.execution.result}')
        # If the task is pending, check if it can be executed
        if self.execution.status == TaskStatus.pending:
            self.execution.status = TaskStatus.running
            self.execution.started_at = datetime.datetime.now()
            result = send_task_result_http(self.execution)
            try:
                if result['status'] != 'ok':
                    raise Exception(f"Assigning task in progress: {result['status']}")
            except Exception as e:
                return self.execution
        try:
            if self.execution.status in (TaskStatus.waiting, TaskStatus.pending_wait):
                self.execution = self.on_wait(self.execution)
                self.execution.last_refresh = datetime.datetime.now()
            else:
                if not self.execution.started_at:
                    self.execution.started_at = datetime.datetime.now()
                self.execution = self.run(self.execution)
        except Exception as e:
            self.execution.error = str(e)
            self.execution.status = TaskStatus.errored
            logger.error(f'Error executing task {self.identifier}: {traceback.format_exc()}')
        finally:
            if self.execution.status == TaskStatus.completed or self.execution.status == TaskStatus.errored:
                self.execution.completed_at = datetime.datetime.now()
            self.notify()
        return self.execution
    
    def notify(self, execution: TaskExecution = None):
        ''' Send the task update to the server '''
        if not execution:
            execution = self.execution
        if self.notifier:
            self.notifier.notify_status(execution)

    # To be overriden
    def run(self, execution: TaskExecution) -> TaskExecution:
        ''' Run the task '''
        raise NotImplementedError('Run method not implemented')
    def on_wait(self, execution: TaskExecution) -> TaskExecution:
        ''' Check a task in waiting status '''
        return execution
