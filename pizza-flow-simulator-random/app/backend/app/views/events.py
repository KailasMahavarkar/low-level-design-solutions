''' Endpoints for access control '''
from fastapi import Depends, HTTPException, APIRouter
from models.users import User
from access_control.auth import active_user
from pydantic import BaseModel
from persistance.events import list_persisted_events
from controllers.events import EventsController

api_app = APIRouter()
@api_app.get("/events", tags=["events"])
async def api_list_events(
    current_user: User = Depends(active_user),
    limit: int = 10, offset: int = 0
    ):
    ''' Returns a list of events for the current user '''
    event_list = [x.model_dump() for x in await list_persisted_events(limit, offset)]
    return {"events": event_list}
