''' Endpoints for access control '''
import traceback
from fastapi import Depends, HTTPException, APIRouter
from models.users import User
from models.tasks import TaskStatus
from persistance.rfa import RFA, persist_rfa
from access_control.auth import active_user
from pydantic import BaseModel
from logs import logger
from operations import (
    cancel_operation,
    delete_operation,
    pause_operation,
    schedule_next_tasks_operation
)
from controllers.rfa import RFAController
from controllers.events import EventsController

from persistance.tasks import (load_persisted_task, persist_task, load_tasks_for_operation, delete_persisted_task)
from persistance.operations import load_persisted_operation, load_persisted_operations_filtering
from ws import ws

api_app = APIRouter()
@api_app.get('/ops', tags=["operations"])
async def list_ops(limit: int=None, status: str=None, req_user: User = Depends(active_user)):
    ''' Returns the list of Operations '''
    try:
        params = {}
        if limit:
            params['limit'] = limit
        if status:
            params['status'] = status.split(',')
        ops_list =[x.model_dump() for x in load_persisted_operations_filtering(**params)]
        return {"operations": ops_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_app.get('/ops/{op_id}', tags=["operations"])
async def get_op(op_id: str, req_user: User = Depends(active_user)):
    ''' Returns the details of a specific Operation '''
    op = load_persisted_operation(op_id)
    if not op:
        raise HTTPException(status_code=404, detail="Operation not found")
    tasks = load_tasks_for_operation(op_id)
    return {"operation": op.model_dump(), "tasks": [x.model_dump(exclude={'result'}) for x in tasks]}

class OperationUpdateRequest(BaseModel):
    action: str

@api_app.post("/ops/{op_id}", tags=["operations"])
async def act_on_op(op_id: str, req: OperationUpdateRequest, req_user: User = Depends(active_user)):
    ''' Cancel an Operation '''
    op = load_persisted_operation(op_id)
    if not op:
        raise HTTPException(status_code=404, detail="Operation not found")
    try:
        if req.action == 'cancel':
            await cancel_operation(op)
        elif req.action == 'pause':
            await pause_operation(op)
        elif req.action == 'delete':
            await delete_operation(op)
        elif req.action == 'reschedule':
            await schedule_next_tasks_operation(op)
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        return op.model_dump()
    except Exception as e:
        logger.exception(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@api_app.post("/task/{task_id}", tags=["operations"])
async def act_on_task(task_id: str, req: OperationUpdateRequest, req_user: User = Depends(active_user)):
    ''' Cancel an Operation '''
    task = load_persisted_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    try:
        if req.action == 'cancel':
            task.status = TaskStatus.cancelled
            persist_task(task)
        elif req.action == 'delete':
            delete_persisted_task(task_id)
        elif req.action == 'rerun':
            task.status = TaskStatus.pending
            if not task.max_retries:
                task.max_retries = 0
            task.max_retries += 1
            task.error = None
            persist_task(task)
            await ws.emit('task', task.model_dump(), namespace='/worker')
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        return task.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_app.get('/task/{task_id}', tags=["operations"])
async def http_get_task(task_id: str, req_user: User = Depends(active_user)):
    ''' Returns the details of a specific Task '''
    task = load_persisted_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.model_dump()

## Specific operations
class PerformOperationRequest(BaseModel):
    ''' Operation Request model '''
    parameters: dict
    channel: str = 'api'

@api_app.put('/ops/{op_name}', tags=["operations"])
async def http_perform_operation(op_name: str, req: PerformOperationRequest, user: User = Depends(active_user)):
    ''' Perform an operation '''
    try:
        rfa = RFA(requester=user.email, operation=op_name, parameters=req.parameters, request_channel=req.channel)
        rfa_db = persist_rfa(rfa)
        await EventsController.create_event(user, "rfa_created", {'rfa_id': str(rfa.id), 'operation': rfa.operation})
        await RFAController.ws_notify(rfa)
        return {"status": "waiting_for_approval", 'rfa': rfa_db.model_dump()}
    except Exception as e:
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
