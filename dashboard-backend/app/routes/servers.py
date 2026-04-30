from __future__ import annotations

from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from ..agent_client import AgentClient
from ..auth import get_current_user
from ..database import get_session
from ..encryption import decrypt_text, encrypt_text
from ..models import AuditLog, Server, User

router = APIRouter(prefix="/api/servers", tags=["servers"], dependencies=[Depends(get_current_user)])


class ServerCreate(BaseModel):
    name: str
    url: str
    api_key: str
    action_key: str | None = None
    environment: str = "production"
    notes: str = ""
    group_id: int | None = None


class ServerUpdate(BaseModel):
    name: str | None = None
    url: str | None = None
    api_key: str | None = None
    action_key: str | None = None
    environment: str | None = None
    notes: str | None = None
    group_id: int | None = None


def server_read(server: Server) -> dict:
    return {
        "id": server.id,
        "name": server.name,
        "url": server.url,
        "status": server.status,
        "environment": server.environment,
        "notes": server.notes,
        "group_id": server.group_id,
        "last_seen": server.last_seen,
        "created_at": server.created_at,
        "updated_at": server.updated_at,
        "api_key_configured": bool(server.api_key_encrypted),
        "action_key_configured": bool(server.action_key_encrypted),
    }


@router.get("")
def list_servers(session: Session = Depends(get_session)) -> list[dict]:
    return [server_read(server) for server in session.exec(select(Server).order_by(Server.name)).all()]


@router.post("")
def create_server(payload: ServerCreate, session: Session = Depends(get_session), user: User = Depends(get_current_user)) -> dict:
    server = Server(
        name=payload.name,
        url=payload.url.rstrip("/"),
        api_key_encrypted=encrypt_text(payload.api_key),
        action_key_encrypted=encrypt_text(payload.action_key),
        environment=payload.environment,
        notes=payload.notes,
        group_id=payload.group_id,
    )
    session.add(server)
    session.add(AuditLog(actor=user.username, action="server.create", resource=payload.name))
    session.commit()
    session.refresh(server)
    return server_read(server)


@router.get("/{server_id}")
def get_server(server_id: int, session: Session = Depends(get_session)) -> dict:
    server = session.get(Server, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return server_read(server)


@router.put("/{server_id}")
def update_server(server_id: int, payload: ServerUpdate, session: Session = Depends(get_session), user: User = Depends(get_current_user)) -> dict:
    server = session.get(Server, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    data = payload.model_dump(exclude_unset=True)
    for field in ("name", "url", "environment", "notes", "group_id"):
        if field in data and data[field] is not None:
            setattr(server, field, data[field].rstrip("/") if field == "url" else data[field])
    if data.get("api_key"):
        server.api_key_encrypted = encrypt_text(data["api_key"])
    if "action_key" in data:
        server.action_key_encrypted = encrypt_text(data["action_key"])
    server.updated_at = datetime.now(timezone.utc)
    session.add(server)
    session.add(AuditLog(actor=user.username, action="server.update", resource=str(server_id)))
    session.commit()
    session.refresh(server)
    return server_read(server)


@router.delete("/{server_id}")
def delete_server(server_id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)) -> dict:
    server = session.get(Server, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    session.delete(server)
    session.add(AuditLog(actor=user.username, action="server.delete", resource=str(server_id)))
    session.commit()
    return {"status": "deleted"}


@router.post("/{server_id}/test")
async def test_server(server_id: int, session: Session = Depends(get_session)) -> dict:
    server = session.get(Server, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    try:
        data = await AgentClient(server.url, decrypt_text(server.api_key_encrypted)).get("/api/ping")
        return {"status": "online", "response": data}
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/{server_id}/poll")
async def poll_now(server_id: int) -> dict:
    from ..polling import poll_server

    return await poll_server(server_id)

