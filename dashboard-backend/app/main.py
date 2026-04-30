from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session

from . import models  # noqa: F401
from .auth import ensure_admin_user
from .config import get_settings
from .database import create_db_and_tables, engine
from .polling import start_scheduler, stop_scheduler
from .routes import actions, alerts, auth, backups, containers, health_checks, metrics, notifications, overview, servers, settings
from .websocket import manager

settings_obj = get_settings()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

app = FastAPI(title="Sentinel Dashboard Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings_obj.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(servers.router)
app.include_router(overview.router)
app.include_router(containers.router)
app.include_router(metrics.router)
app.include_router(alerts.router)
app.include_router(health_checks.router)
app.include_router(notifications.router)
app.include_router(actions.router)
app.include_router(settings.router)
app.include_router(backups.router)


@app.on_event("startup")
def startup() -> None:
    create_db_and_tables()
    with Session(engine) as session:
        ensure_admin_user(session)
    start_scheduler()


@app.on_event("shutdown")
def shutdown() -> None:
    stop_scheduler()


@app.websocket("/ws/events")
async def websocket_events(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/api/status")
def status() -> dict:
    return {"status": "ok", "service": "sentinel-dashboard-backend"}


dist = Path(settings_obj.frontend_dist_path)
if dist.exists():
    app.mount("/", StaticFiles(directory=dist, html=True), name="frontend")

