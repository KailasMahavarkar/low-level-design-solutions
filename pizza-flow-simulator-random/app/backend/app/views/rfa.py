''' Endpoints for access control '''
from fastapi import Depends, HTTPException, APIRouter
from models.users import User
from models.rfa import RFAStatus
from access_control.auth import active_user
from pydantic import BaseModel
from controllers.rfa import RFAController
from persistance.rfa import list_persisted_rfas, load_persisted_rfa
from logs import logger

api_app = APIRouter()
@api_app.get("/admin/rfas", tags=["rfa"])
async def api_list_rfas(current_user: User = Depends(active_user),
    limit: int = 100, offset: int = 0, status: str = None):
    ''' Returns the list of RFAs for the current user '''
    try:
        args = {'limit': limit, 'offset': offset}
        if status:
            args['status'] = status.split(',')
        rfa_list = [x.model_dump() for x in await list_persisted_rfas(**args)]
    except Exception as e:
        logger.error(f"Could not list RFAs because of {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    return {"rfas": rfa_list}

@api_app.get("/rfa/{rfa_id}", tags=["rfa"])
async def api_get_single_rfa(rfa_id: str, current_user: User = Depends(active_user)):
    ''' Returns the details of a specific RFA '''
    rfa = load_persisted_rfa(rfa_id)
    return rfa.model_dump()

class RFAResponseRequest(BaseModel):
    status: RFAStatus
    channel: str = 'api'

@api_app.post("/rfa/{rfa_id}", tags=["rfa"])
async def api_resolve_rfa(rfa_id: str, req: RFAResponseRequest, current_user: User = Depends(active_user)):
    ''' Resolve an RFA '''
    try:
        rfa = await RFAController.resolve_rfa(
            rfa_id=rfa_id,
            status=req.status,
            approver=current_user,
            channel=req.channel)
        await RFAController.ws_notify(rfa)
        return {"rfa": rfa.model_dump()}
    except Exception as e:
        logger.error(f"Could not resolve RFA because of {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
