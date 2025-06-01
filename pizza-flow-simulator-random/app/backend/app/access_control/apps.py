''' Authentication functions '''
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from models.users import AppToken
from .auth import SECRET_KEY, ALGORITHM, oauth2_scheme
from uuid import uuid4


def create_app_token(app_id: str, can_impersonate: bool = False, can_resolve_rfas: bool = False) -> str:
    data = {
        "sub": str(uuid4()),
        "app_id": app_id,
        "type": "app",
        "can_impersonate": can_impersonate,
        "can_resolve_rfas": can_resolve_rfas
    }
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def authenticate_app(token: str = Depends(oauth2_scheme)) -> AppToken:
    ''' Authenticates an app and returns the data '''
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != 'app':
            raise credentials_exception
        app = AppToken(
            token=token,
            app_id=payload.get("app_id"),
            can_impersonate=payload.get("can_impersonate", False),
            can_resolve_rfas=payload.get("can_resolve_rfas", False)
        )
        return app
    except JWTError:
        raise credentials_exception
