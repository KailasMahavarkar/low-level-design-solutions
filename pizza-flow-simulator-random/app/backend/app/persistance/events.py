from typing import List
import datetime
from sqlmodel import Field, SQLModel, select, Relationship
from models.pizzas import Pizza
from .database import get_db
from pydantic import field_serializer
import uuid

class Event(SQLModel, table=True):
    ''' Event model. Represents an event in the application '''
    __tablename__: str = 'events'
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4, index=True)
    actor_email: str | None = Field(default=None)
    pizza_id: uuid.UUID | None = Field(default=None, foreign_key="pizzas.id")
    pizza: Pizza | None = Relationship(back_populates="events")
    time: datetime.datetime = Field(default_factory=datetime.datetime.now)
    event_type: str
    description: str | None = None

    @field_serializer("id", "pizza_id")
    def serialize_uuid(self, value):
        ''' Serialize UUID '''
        if value is None:
            return None
        return str(value)
    
    @field_serializer("time")
    def serialize_time(self, value):
        ''' Serialize the time fields '''
        if value is None:
            return None
        return value.isoformat()

def load_persisted_event(id: str) -> Event:
    ''' Load a persisted event '''
    with get_db() as db:
        return db.get(Event, id)

def persist_event(event: Event) -> Event:
    ''' Persist a event '''
    with get_db() as db:
        db.add(event)
        db.commit()
        db.refresh(event)
    return event

async def list_persisted_events(limit: int = None, offset: int = 0, status: List[str] = None) -> List[Event]:
    ''' List persisted pizzas '''
    with get_db() as db:
        return db.exec(select(Event).order_by(Event.time.desc()).offset(offset).limit(limit)).all()
