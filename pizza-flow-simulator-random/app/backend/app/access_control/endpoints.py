''' Endpoints for access control '''
from fastapi import Depends, APIRouter
from models.users import User
from .auth import active_user
from typing import List, Dict

api_app = APIRouter()

@api_app.get("/auth_methods", tags=["auth"], summary="Get available authentication methods")
async def get_auth_methods() -> Dict[str, List[str]]:
    ''' Returns the list of available authentication methods '''
    methods = ["basic"]
    return {"methods": methods}

@api_app.get("/users/me", tags=["auth"], summary="Get current user")
async def read_users_me(current_user: User = Depends(active_user)) -> User:
    ''' Get the details of the user performing the request'''
    return current_user.model_dump(exclude={'hashed_password', 'disabled'}, exclude_none=True)
