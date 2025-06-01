''' Task Retriever HTTP module '''
from typing import List, Any
import requests
from .task_retriever_abs import TaskRetrieverProvider
from models.tasks import Task
from models.task_execution import TaskExecution
from logs import logger


class TaskRetrieverHTTP(TaskRetrieverProvider):
    ''' Task Retriever HTTP class '''
    server_url = 'http://localhost:8080'
    registry = None

    def __init__(self, server_url: str, auth_token: str, registry: Any):
        self.server_url = server_url
        self.registry = registry
        self.auth_token = auth_token

    def pull_tasks(self) -> List[TaskExecution]:
        ''' Pull tasks from the provider '''
        logger.debug("Pulling remote tasks")
        try:
            auth_headers = {'Authorization': f'Bearer {self.auth_token}'}
            sr = requests.get(f"{self.server_url}/api/worker/tasks", headers=auth_headers)
            if sr.status_code != 200:
                logger.error(f"Error pulling tasks: {sr.status_code}")
                return []
            response = sr.json()
            tasks = [TaskExecution(**task) for task in response['tasks']]
            return tasks
        except Exception as e:
            logger.error(f"Error pulling tasks: {e}")
            return []

    def get_tasks(self) -> List[Task]:
        ''' Get tasks from the provider '''
        logger.debug("Getting remote tasks")
        requests = self.pull_tasks()
        rd = []
        for request in requests:
            try:
                task_class = self.registry.get_task_with_id(request.task_id)
                task = task_class(request)
                rd.append(task)
            except NotImplementedError as e:
                logger.error(f"No task handler found with id {request.task_id}")
        return rd
