''' Task models '''
import datetime
from enum import StrEnum
from uuid import uuid4
from .operations import Operation
from pydantic import Field, field_serializer
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy.dialects.postgresql import JSONB

class TaskStatus(StrEnum):
    ''' Task Status Enum '''
    running = 'running'
    completed = 'completed'
    errored = 'errored'
    pending = 'pending'
    waiting = "waiting"           # Task is in waiting locally
    pending_wait = "pending_wait" # Task is pending wait in the server
    cancelled = 'cancelled'

class Task(SQLModel, table=True):
    ''' Task Execution model '''
    __tablename__: str = 'tasks'
    uuid: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    task_id: str
    region: str
    operation_id: str | None = Field(foreign_key="operations.uuid")
    operation: Operation = Relationship(back_populates="tasks")
    parameters: dict = Field(sa_type=JSONB, default_factory=dict)
    retries: int = 0
    max_retries: int | None = None
    status: TaskStatus = TaskStatus.pending
    started_at: datetime.datetime | None = None
    completed_at: datetime.datetime | None = None
    last_refresh: datetime.datetime | None = None
    error: str | None = None
    result: dict | None = Field(sa_type=JSONB, default_factory=dict)
    wait_time: int | None = 30 # Time to wait before refreshing the task
    max_wait_time: int | None = None  # How many iterations to wait before cancelling the task

    @field_serializer('started_at', 'completed_at', 'last_refresh')
    def serialize_time(self, value):
        ''' Serialize the time fields '''
        if value is None:
            return None
        if isinstance(value, datetime.datetime):
            return value.isoformat()
        return value

    @field_serializer("result", "parameters")
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