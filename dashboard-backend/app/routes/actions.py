from __future__ import annotations

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from ..agent_client import AgentClient
from ..auth import get_current_user
from ..database import get_session
from ..encryption import decrypt_text
from ..models import ActionLog, Server

router = APIRouter(prefix="/api/actions", tags=["actions"], dependencies=[Depends(get_current_user)])


class PullImagePayload(BaseModel):
    image: str


def _client_for_action(server: Server) -> AgentClient:
    action_key = decrypt_text(server.action_key_encrypted)
    if not action_key:
        raise HTTPException(status_code=400, detail="Server action key is not configured")
    return AgentClient(server.url, decrypt_text(server.api_key_encrypted), action_key=action_key)


@router.post("/servers/{server_id}/containers/{container_id}/{action}")
async def container_action(server_id: int, container_id: str, action: str, session: Session = Depends(get_session)) -> dict:
    if action not in {"restart", "start", "stop"}:
        raise HTTPException(status_code=400, detail="Unsupported action")
    server = session.get(Server, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    try:
        result = await _client_for_action(server).post(f"/api/actions/containers/{container_id}/{action}", include_action_key=True)
        session.add(ActionLog(server_id=server_id, container_id=container_id, action=action, status="accepted", message=str(result)))
        session.commit()
        return result
    except httpx.HTTPError as exc:
        session.add(ActionLog(server_id=server_id, container_id=container_id, action=action, status="failed", message=str(exc)))
        session.commit()
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/servers/{server_id}/images/pull")
async def pull_image(server_id: int, payload: PullImagePayload, session: Session = Depends(get_session)) -> dict:
    server = session.get(Server, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    try:
        result = await _client_for_action(server).post("/api/actions/images/pull", json={"image": payload.image}, include_action_key=True)
        session.add(ActionLog(server_id=server_id, action="image.pull", status="accepted", message=payload.image))
        session.commit()
        return result
    except httpx.HTTPError as exc:
        session.add(ActionLog(server_id=server_id, action="image.pull", status="failed", message=str(exc)))
        session.commit()
        raise HTTPException(status_code=502, detail=str(exc)) from exc

