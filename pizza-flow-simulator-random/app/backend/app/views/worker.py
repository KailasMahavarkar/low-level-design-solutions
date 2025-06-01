''' Endpoints for workers '''
from fastapi import Depends, HTTPException, Request, APIRouter
from models.tasks import Task
from access_control.worker import authenticate_worker
from controllers.worker import AlreadyRunningException, OperationNotFoundException, on_task_notify, get_tasks_for_region
from logs import logger

api_app = APIRouter()

@api_app.post("/worker/identify", tags=["worker"])
async def worker_identify(body: Request, worker_pop = Depends(authenticate_worker)):
    ''' Identify the worker '''
    info = await body.json()
    #pop_controller.on_worker_update(info)
    return {"status": "ok"}

@api_app.get("/worker/tasks", tags=["worker"])
async def list_worker_tasks(worker_pop = Depends(authenticate_worker)):
    ''' Returns the list of tasks for the worker '''
    tasks_list = await get_tasks_for_region(worker_pop)
    return {"tasks": tasks_list}

@api_app.post("/worker/task/{task_id}", tags=["worker"])
async def worker_task_feedback(task_id: str, execution: Task, worker = Depends(authenticate_worker)):
    ''' Task feedback from worker '''
    try:
        response = await on_task_notify(execution)
    except AlreadyRunningException:
        raise HTTPException(status_code=409, detail="Task already running")
    except OperationNotFoundException:
        raise HTTPException(status_code=400, detail="Operation not found")
    return response

from ws import ws, ws_sessions
async def ws_worker_task_feedback(session_id, data: dict):
    ''' Callback for websocket '''
    logger.debug(f'WS Callback: {data}')
    try:
        execution = Task(**data)
        response = await on_task_notify(execution)
    except AlreadyRunningException:
        return {"status": "error", "error": "Task already running"}
    except OperationNotFoundException:
        return {"status": "error", "error": "Operation not found"}
    return response

async def ws_worker_task_pull(sid):
    ''' Callback for websocket to pull pending tasks '''
    worker_id = ws_sessions.get(sid)
    logger.debug(f'[WS] Worker {worker_id} asking for new jobs')
    tasks = await get_tasks_for_region(worker_id)
    for task in tasks:
        await ws.emit('task', task.model_dump(), room=sid, namespace='/worker')
    
ws.on('task_result', ws_worker_task_feedback, namespace='/worker')
ws.on('get_tasks', ws_worker_task_pull, namespace='/worker')