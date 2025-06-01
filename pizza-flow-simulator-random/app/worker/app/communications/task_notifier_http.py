''' Fake task notififcation provider '''
from communications.task_notifier_abs import TaskStatusNotifierProvider
from models.task_execution import TaskExecution
from logs import logger
import json
import requests
import time
from config import SERVER_URL, WORKER_TOKEN

def send_task_result_http(task: TaskExecution) -> None:
    ''' Send task result to the server '''
    logger.debug(f"Sending task result to {SERVER_URL}")
    try:
        auth_headers = {'Authorization': f'Bearer {WORKER_TOKEN}'}
        sr = requests.post(f"{SERVER_URL}/api/worker/task/{task.uuid}", json=task.model_dump(), headers=auth_headers)
        if sr.status_code != 200:
            logger.error(f"Error sending task result: {sr.status_code}")
        return sr.json()
    except Exception as e:
        logger.error(f"Error sending task result: {e}")
        return None

class TaskStatusNotifierHTTP(TaskStatusNotifierProvider):
    ''' Fake task notififcation provider '''
    server_url = 'http://localhost:8080'
    def __init__(self, server_url: str, auth_token: str):
        self.server_url = server_url
        self.auth_token = auth_token

    def notify_status(self, execution: TaskExecution) -> None:
        ''' Notify the task status '''
        logger.info(f'Notifying task {execution.task_id}')
        logger.debug(f'Execution details: {json.dumps(execution.model_dump(), indent=4)}')
        auth_headers = {'Authorization': f'Bearer {self.auth_token}'}
        sr = requests.post(
            f"{self.server_url}/api/worker/task/{execution.uuid}",
            headers=auth_headers,
            json=execution.model_dump())
        if sr.status_code != 200:
            logger.error(f"Error notifying task: {sr.status_code} {sr.text}. Will retry in 30s")
            time.sleep(30)
            self.notify_status(execution)
        else:
            logger.debug(f"Task {execution.task_id} acknowledged by server")
