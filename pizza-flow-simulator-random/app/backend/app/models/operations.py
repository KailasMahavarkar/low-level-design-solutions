from typing import List, Dict
from pydantic import Field, field_serializer
from uuid import uuid4
from enum import StrEnum
import datetime
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy.dialects.postgresql import JSONB

class OperationStatus(StrEnum):
    ''' Possible Operation statuses '''
    running = 'running'
    completed = 'completed'
    errored = 'errored'
    paused = 'paused'
    pending = 'pending'
    cancelled = 'cancelled'

class Operation(SQLModel, table=True):
    ''' Operation model '''
    __tablename__: str = 'operations'
    uuid: str = Field(primary_key=True, default_factory=lambda: str(uuid4()), index=True) # Unique identifier for the operation
    operation: str # Name of the operation, ie create_pizza
    parameters: Dict = Field(default_factory=dict, sa_type=JSONB)
    rfa_id: str | None = None
    status: OperationStatus = OperationStatus.pending
    result: Dict | None = Field(sa_type=JSONB, default_factory=dict)
    start_date: datetime.datetime = Field(default_factory=datetime.datetime.now)
    end_date: datetime.datetime | None = None
    tasks: List["Task"] = Relationship(back_populates="operation")

    @field_serializer('start_date', 'end_date')
    def serialize_time(self, value):
        ''' Serialize the time fields '''
        if value is None:
            return None
        if isinstance(value, datetime.datetime):
            return value.isoformat()
        return value
    
    @field_serializer('parameters', 'result')
    def serialize_dicts(self, value):
        ''' Serialize the time fields '''
        if value is None:
            return None
        return clear_decimals(value)

from decimal import Decimal
def clear_decimals(x: dict) -> dict:
    for k,v in x.items():
        if isinstance(v,Decimal):
            x[k] = int(v)
        if isinstance(v,dict):
            x[k] = clear_decimals(v)
    return x