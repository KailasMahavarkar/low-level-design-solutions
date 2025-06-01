''' User models'''
import datetime
import uuid
from enum import StrEnum
from typing import List
from pydantic import field_serializer, Field
from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_serializer

class PizzaStatus(StrEnum):
    ''' Possible Pizza statuses '''
    ready = 'ready'
    eaten = 'eaten'
    paused = 'paused'
    pending = 'pending'
    cancelled = 'cancelled'
    expired = 'expired'
    modifying = 'modifying'
    frozen = 'frozen'
    creating = 'creating'
    eating = 'eating'

class PizzaTier(StrEnum):
    ''' Possible Pizza Tiers '''
    premium = 'premium'
    enterprise = 'enterprise'
    trial = 'trial'


class Pizza(SQLModel, table=True):
    ''' Represents a pizza order '''
    __tablename__: str = 'pizzas'
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4, index=True)
    name: str
    status: PizzaStatus = Field(default=PizzaStatus.pending, index=True)
    version: str
    region: str
    creation: datetime.datetime = Field(default_factory=datetime.datetime.now)
    tier: PizzaTier
    events: List["Event"] = Relationship(back_populates="pizza")

    @field_serializer("id")
    def serialize_uuid(self, value):
        ''' Serialize UUID '''
        if value is None:
            return None
        return str(value)
    
    @field_serializer("creation")
    def serialize_time(self, value):
        ''' Serialize the time fields '''
        if value is None:
            return None
        return value.isoformat()

    def is_active(self) -> bool:
        ''' Check if the pizza is active '''
        return self.status in (
            PizzaStatus.ready,
            PizzaStatus.paused,
            PizzaStatus.pending,
            PizzaStatus.modifying,
            PizzaStatus.creating,
            PizzaStatus.eating
        )

