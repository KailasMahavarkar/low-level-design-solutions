''' User models'''
from pydantic import BaseModel
from enum import StrEnum

class Token(BaseModel):
    access_token: str
    token_type: str

class AppToken(BaseModel):
    ''' Model for app token '''
    token: str
    app_id: str
    can_resolve_rfas: bool = False
    can_impersonate: bool = False

class User(BaseModel):
    email: str
    full_name: str | None = None
    disabled: bool = False
    groups: list[str] | None = None