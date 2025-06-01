''' Events Controller '''
from models.users import User
from logs import logger
from persistance.events import Event, load_persisted_event, persist_event
from typing import Union
import json
from ws import ws

class EventsController():
    ''' Events Controller Class '''
    @staticmethod
    async def create_event(actor: Union[User, str], event_type: str, description: Union[str, dict, None] = None, pizza_id: str = None) -> Event:
        ''' Create an event '''
        if isinstance(description, dict):
            description = json.dumps(description)
        try:
            actor_email = actor.email
        except AttributeError:
            actor_email = actor
        event = Event(
            actor_email=actor_email,
            event_type=event_type,
            description=description,
            pizza_id=pizza_id
        )
        
        persisted = persist_event(event)
        await ws.emit('events', persisted.model_dump())
        return persisted
    