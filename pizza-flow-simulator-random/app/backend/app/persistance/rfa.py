from typing import List
import datetime
from sqlmodel import Field, SQLModel, select
from models.rfa import RFAStatus
from .database import get_db
from logs import logger
from pydantic import field_serializer
from sqlalchemy.dialects.postgresql import JSONB
import uuid

class RFA(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4, index=True)
    requester: str
    operation: str
    status: RFAStatus | None = Field(default=RFAStatus.pending, index=True)
    parameters: dict | None = Field(default={}, sa_type=JSONB)
    approver: str | None = None
    notes: str | None = None
    approval_channel: str | None = None
    request_channel: str | None = None
    expiration: datetime.datetime | None = None
    creation: datetime.datetime | None = Field(default_factory=datetime.datetime.now)
    approval_time: datetime.datetime | None = None

    @field_serializer("id")
    def serialize_uuid(self, value):
        ''' Serialize UUID '''
        if value is None:
            return None
        return str(value)
    
    @field_serializer("creation", "expiration", "approval_time")
    def serialize_creation(self, value):
        ''' Serialize the creation time '''
        if value is None:
            return None
        return value.isoformat()

def load_persisted_rfa(id: str) -> RFA:
    ''' Load a persisted RFA '''
    with get_db() as db:
        return db.get(RFA, id)

def persist_rfa(item: RFA) -> RFA:
    ''' Persist a item '''
    with get_db() as db:
        db.add(item)
        db.commit()
        db.refresh(item)
    return item

async def delete_persisted_rfa(id: str) -> None:
    ''' Delete a persisted RFA '''
    with get_db() as db:
        db.delete(RFA, id)

async def list_persisted_rfas(limit: int = None, offset: int = 0, status: List[str] = None) -> List[RFA]:
    ''' List persisted rfas '''
    with get_db() as db:
        return db.exec(select(RFA).offset(offset).limit(limit)).all()
