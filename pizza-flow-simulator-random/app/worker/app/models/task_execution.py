from pydantic import BaseModel, field_serializer
from enum import StrEnum
import datetime

class TaskStatus(StrEnum):
    pending = "pending"
    running = "running"
    waiting = "waiting"           # Task is in waiting locally
    pending_wait = "pending_wait" # Task is pending wait in the server
    completed = "completed"
    errored = "errored"
    
class TaskExecution(BaseModel):
    ''' Task Execution model '''
    task_id: str
    uuid: str
    operation_id: str | None = None
    region: str
    parameters: dict | None = {}
    status: TaskStatus = TaskStatus.pending
    result: dict | None = {}
    retries: int = 0
    max_retries: int | None = None
    error: str | None = None
    started_at: datetime.datetime | None = None
    completed_at: datetime.datetime | None = None
    last_refresh: datetime.datetime | None = None
    wait_time: int | None = None
    max_wait_time: int | None = None

    @field_serializer("started_at", "completed_at", "last_refresh")
    def serialize_time(self, value):
        ''' Serialize the time fields '''
        if value is None:
            return None
        return value.isoformat()