import os
from fastapi import FastAPI, APIRouter
import socketio
from logs import logger, LogMiddleware
from starlette.middleware.sessions import SessionMiddleware

api_app = APIRouter(prefix="/api")
SECRET_KEY = os.getenv("SECRET_KEY", "b423d5741f142a07621502e45f761ee97779e74d4b80c4d8194cf2f1e02c1f7e")
app = FastAPI(title="SaaS App")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.add_middleware(LogMiddleware)

from ws import ws
ws_app = socketio.ASGIApp(socketio_server=ws, socketio_path='/ws/socket.io')
app.mount("/ws", ws_app)

from access_control import endpoints
from views import pizzas, rfa
from views.events import api_app as events_api_app
from views.operations_view import api_app as operations_api_app

app.include_router(endpoints.api_app, prefix="/api")
app.include_router(pizzas.api_app, prefix="/api")
app.include_router(rfa.api_app, prefix="/api")
app.include_router(events_api_app, prefix="/api")
app.include_router(operations_api_app, prefix="/api")

from views.worker import api_app as worker_api_app
app.include_router(worker_api_app, prefix="/api")

if os.getenv("FRONTEND_SERVER", "static") == "static":
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    from fastapi import Request
    FRONTEND_DIR = '/app/frontend'
    app.mount("/static", StaticFiles(directory=f"{FRONTEND_DIR}/static"), name="ui")
    
    @app.options("/{path:path}")
    @app.get("/{path:path}")
    async def _serve_ui(path: str | None, request: Request):
        if os.path.isfile(f"{FRONTEND_DIR}/{path}"):
            return FileResponse(f"{FRONTEND_DIR}/{path}")
        return FileResponse(f"{FRONTEND_DIR}/index.html")
else:
    from starlette.requests import Request
    from starlette.responses import StreamingResponse
    from starlette.background import BackgroundTask
    import httpx
    client = httpx.AsyncClient(base_url=os.getenv("FRONTEND_SERVER"))

    async def _reverse_proxy(request: Request):
        url = httpx.URL(path=request.url.path,
                        query=request.url.query.encode("utf-8"))
        rp_req = client.build_request(request.method, url,
                                    headers=request.headers.raw,
                                    content=await request.body())
        rp_resp = await client.send(rp_req, stream=True)
        return StreamingResponse(
            rp_resp.aiter_raw(),
            status_code=rp_resp.status_code,
            headers=rp_resp.headers,
            background=BackgroundTask(rp_resp.aclose),
        )

    app.add_route("/{path:path}",
                _reverse_proxy, ["GET", "POST"])

@app.get("/health")
async def health():
    return {"status": "ok"}
