''' Authentication functions '''
import os
from fastapi import Depends, HTTPException
from passlib.context import CryptContext
from persistance.user import User
from jose import JWTError, jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "b423d5741f142a07621502e45f761ee97779e74d4b80c4d8194cf2f1e02c1f7e")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # one week

async def get_current_user(token=None):
    '''
    Get the current user from context in the request or from token if provided
    '''
    if token:
        try:
            # Try to decode the token to validate it
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            # If it's a worker token, treat it as a special user
            if payload.get("sub") == "worker":
                return User(email=f"worker@{payload.get('pop', 'unknown')}.internal", 
                          groups=['worker'], 
                          full_name=f"Worker {payload.get('pop', 'unknown')}")
        except JWTError:
            # If token is invalid, continue with default user
            pass
    
    # Default user for development
    return User(email='candidate@getcollate.io', groups=['admin'], full_name='Candidate')

async def active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user