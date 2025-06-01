''' Websockets management '''
import os
from logs import logger
import socketio

from access_control import auth
from access_control.worker import validate_worker_token
from persistance.redis import WSAuthPersistorRedis

# Websockets
ws_client_manager = None
if os.getenv("REDIS_HOST", ""):
    logger.info(f"Using Redis for Websockets")
    redis_url = f"redis://{os.getenv('REDIS_HOST')}"
    ws_client_manager = socketio.AsyncRedisManager(redis_url)
ws = socketio.AsyncServer(async_mode='asgi', client_manager=ws_client_manager)
ws_sessions = WSAuthPersistorRedis()

@ws.event
async def connect(sid, environ, authorization):
    token = authorization.get('token')
    try:
        user = await auth.get_current_user(token)
    except Exception as e:
        print(f'[WS] Error connecting user with token {token}: {e}')
        return False
    if not user:
        print(f'[WS] Connected user Unauthorized')
        return False
    print(f'[WS] Connected user {user.email} with sid {sid}')
    
@ws.on('join')
async def join(sid, room):
    logger.info(f'[WS] Joining room {room}')
    await ws.enter_room(sid, room)

@ws.event
def disconnect(sid):
    logger.info(f'[WS] Disconnect {sid}')
    try:
        ws_sessions.delete(sid)
    except Exception as e:
        logger.error(f'[WS] Error deleting session {sid}: {e}')

@ws.on('connect', namespace='/worker')
async def connect_worker(sid, environ, authorization):
    token = authorization.get('token')
    try:
        worker = validate_worker_token(token)
        print(f'[WS] Connected worker {worker} with sid {sid}')
        ws_sessions.persist(sid, worker)
        return True
    except Exception as e:
        print(f'[WS] Error connecting worker with token {token}: {e}')
        return False
