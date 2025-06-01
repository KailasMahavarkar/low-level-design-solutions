import time
from queue import Queue, ShutDown, Empty
from threading import Thread, Event
from logs import logger
from models.task_execution import TaskStatus, TaskExecution
from models.tasks import Task

# Thread safe queue
num_threads = 5
tasks_queue = Queue(maxsize=num_threads*2)
results_queue = Queue(maxsize=num_threads*2)
worker_threads = []

class TaskWorker(Thread):
    status = 'stopped'
    def __init__(self, identifier: int, tasks_queue: Queue, results_queue: Queue):
        Thread.__init__(self)
        self.tasks_queue = tasks_queue
        self.results_queue = results_queue
        self.identifier = identifier
        self.daemon = True
        self.event = Event()
        self.start()

    def run(self):
        ''' Method that runs the worker '''
        logger.info(f"[T{self.identifier}] Starting worker thread")
        while not self.event.is_set():
            if self.status != 'waiting':
                self.status = 'idle'
            try:
                task = self.tasks_queue.get()
            except ShutDown:
                self.status = 'stopped'
                break
            self.status = 'working'
            res = task.execute()
            match res.status:
                case TaskStatus.waiting:
                    logger.debug(f"[T{self.identifier}] Task {res.task_id} waiting")
                    self.results_queue.put(res)
                    self.status = 'waiting'
                    self.wait(task)
                case _:
                    logger.debug(f"[T{self.identifier}] Task {res.task_id} {res.status.value}")
                    self.results_queue.put(res)
                
            #task.execute(notifier=task_notifier)
            self.tasks_queue.task_done()
        logger.debug(f"[T{self.identifier}] Stoped worker thread")

    def wait(self, task: Task) -> None:
        ''' Trigger a task in waiting status '''
        count = 0
        while task.execution.status == TaskStatus.waiting or self.event.is_set():
            for _ in range(task.execution.wait_time):
                if self.event.is_set():
                    logger.debug(f"[T{self.identifier}] Event is set, stopping worker thread")
                    task.execution.status = TaskStatus.pending_wait
                    self.results_queue.put(task.execution)
                    return
                time.sleep(1)
            count += 1
            task.execute()
            self.results_queue.put(task.execution)
            if task.execution.max_wait_time and count > task.execution.max_wait_time:
                task.execution.status = TaskStatus.errored
                task.execution.error = "Max wait time reached"
                break
        self.status = 'idle'


def start_threads():
    for i in range(num_threads):
        worker = TaskWorker(i, tasks_queue, results_queue)
        worker_threads.append(worker)

def stop_threads():
    tasks_queue.shutdown(immediate=True)
    [x.event.set() for x in worker_threads]
    count = 0
    while len(worker_threads):
        logger.debug(f"[Shutdown {count}] Workers status: {', '.join([f'{x.identifier}: {x.status}' for x in worker_threads])}")
        for worker in [x for x in worker_threads if x.status in ('stopped', 'waiting')]:
            worker.join()
            worker_threads.remove(worker)
        count += 1
        time.sleep(0.5)
    logger.info("All workers stopped, emptying the queue")
    while not results_queue.empty():
        try:
            rq = results_queue.get(block=False)
            if isinstance(rq, TaskExecution):
                logger.debug(f"Task {rq.task_id} status: {rq.status}")
        except Empty:
            break
