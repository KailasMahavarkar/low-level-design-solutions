import schedule
import time
import signal, sys
from queue import Empty
from models.task_execution import TaskExecution
from models.tasks import Task
from logs import logger
from tasks import registry
import interfaces
from threads import tasks_queue, results_queue, start_threads, stop_threads

def signal_handler(sig, frame):
    logger.error(f'Received {sig}, exiting.')
    stop_threads()
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


from communications.task_retriever_ws import TaskRetrieverWS
from communications.task_notifier_ws import TaskStatusNotifierWS
from interfaces.ws import connect_ws
from config import SERVER_URL, WORKER_TOKEN
ws = connect_ws(SERVER_URL, WORKER_TOKEN)
task_notifier = TaskStatusNotifierWS(ws)
task_retriever = TaskRetrieverWS(registry=registry, sio=ws)

def on_new_ws_job(task: Task):
    tasks_queue.put(task)
    logger.debug(f"Task {task.execution.uuid} added to the queue. Queue size: {tasks_queue.qsize()}")

task_retriever.set_callback(on_new_ws_job)

def refresh_token():
    if interfaces.k8s_provider:
        logger.debug("Refreshing k8s session")
        interfaces.k8s_provider.refresh_session()

if __name__ == '__main__':
    logger.info("Starting the worker")
    start_threads()
    logger.info(f"Task capabilities: {registry.get_tasks()}")
    task_retriever.get_tasks()
    while True:
        schedule.run_pending()
        try:
            rq = results_queue.get(block=False)
            if isinstance(rq, TaskExecution):
                task_notifier.notify_status(rq)
        except Empty:
            time.sleep(0.5)