from sqlmodel import Field, SQLModel, Relationship
from typing import List

class User(SQLModel, table=True):
    __tablename__ = 'users'
    email: str = Field(default=None, primary_key=True)
    full_name: str | None = None
    disabled: bool | None = None
    organization: str | None = None


