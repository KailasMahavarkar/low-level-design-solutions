''' Endpoints for access control '''
from fastapi import Depends, HTTPException, APIRouter
from models.users import User
from access_control.auth import active_user
from pydantic import BaseModel
from persistance.pizzas import list_persisted_pizzas, load_persisted_pizza
from persistance.rfa import RFA, persist_rfa
from controllers.rfa import RFAController
from controllers.events import EventsController
from models.pizzas import PizzaTier
import traceback
from logs import logger

api_app = APIRouter()
@api_app.get("/pizzas", tags=["pizzas"])
async def api_list_pizzas(
    current_user: User = Depends(active_user),
    limit: int = 100, offset: int = 0, status: str = None
    ):
    ''' Returns the list of pizzas '''
    statuses = status.split(',') if status else []
    pizzas_list = [x.model_dump() for x in await list_persisted_pizzas(limit, offset, statuses)]
    return {"pizzas": pizzas_list}

class CreatePizzaRequest(BaseModel):
    name: str
    version: str
    region: str
    tier: PizzaTier
    extra_params: dict | None = {}
    channel: str | None = 'api'

def create_pizza_rfa(user: User, request: CreatePizzaRequest) -> RFA:
    params = {
        "name": request.name,
        "region": request.region,
        "tier": request.tier,
        "extra_params": request.extra_params or {}
    }
    rfa = RFA(requester=user.email, operation="create_pizza", parameters=params, request_channel=request.channel)
    return rfa

@api_app.post('/pizza/create', tags=["pizza"])
async def api_create_pizza(request: CreatePizzaRequest, current_user: User = Depends(active_user)):
    try:
        rfa_model = create_pizza_rfa(current_user, request)
        rfa = persist_rfa(rfa_model)
        await EventsController.create_event(current_user, "rfa_created", {'rfa_id': str(rfa.id), 'operation': rfa.operation})
        await RFAController.ws_notify(rfa)
        return {"status": "waiting_for_approval", 'rfa_id': str(rfa.id)}
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=403, detail=str(e))


@api_app.get('/pizza/{pizza_id}', tags=["pizzas"])
async def api_get_pizza(pizza_id: str, current_user: User = Depends(active_user)):
    pizza = load_persisted_pizza(pizza_id)
    return {"pizza": pizza.model_dump()}

