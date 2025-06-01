from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .auth import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

def create_worker_token(pop_id: str):
    data = {
        "sub": "worker",
        "pop": pop_id,
    }
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def validate_worker_token(token: str):
    ''' Validates a worker token '''
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("sub") != 'worker':
            raise credentials_exception
        return payload.get("pop")
    except JWTError:
        raise credentials_exception

async def authenticate_worker(token: str = Depends(oauth2_scheme)) -> str:
    ''' Authenticates a worker and returns the PoP ID '''
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("sub") != 'worker':
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return payload.get("pop")
