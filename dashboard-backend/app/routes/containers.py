from __future__ import annotations

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, desc, select

from ..agent_client import AgentClient
from ..auth import get_current_user
from ..database import get_session
from ..encryption import decrypt_text
from ..models import ContainerSnapshot, Server
from ..queries import latest_container_snapshots, latest_system_snapshot

router = APIRouter(prefix="/api", tags=["containers"], dependencies=[Depends(get_current_user)])


@router.get("/containers")
def all_containers(session: Session = Depends(get_session)) -> list[dict]:
    result: list[dict] = []
    servers = session.exec(select(Server)).all()
    for server in servers:
        for container in latest_container_snapshots(session, server.id or 0):
            result.append({**container, "server_id": server.id, "server_name": server.name})
    return result


@router.post("/containers/prune-stale")
def prune_stale_container_snapshots(session: Session = Depends(get_session)) -> dict:
    removed = 0
    servers = session.exec(select(Server)).all()

    for server in servers:
        if server.id is None:
            continue
        latest_system = latest_system_snapshot(session, server.id)
        if not latest_system:
            continue

        old_rows = session.exec(
            select(ContainerSnapshot).where(
                ContainerSnapshot.server_id == server.id,
                ContainerSnapshot.created_at < latest_system.created_at,
            )
        ).all()
        for row in old_rows:
            session.delete(row)
            removed += 1

        latest_rows = session.exec(
            select(ContainerSnapshot)
            .where(
                ContainerSnapshot.server_id == server.id,
                ContainerSnapshot.created_at >= latest_system.created_at,
            )
            .order_by(desc(ContainerSnapshot.created_at))
        ).all()
        seen_names: set[str] = set()
        for row in latest_rows:
            if row.container_name in seen_names:
                session.delete(row)
                removed += 1
                continue
            seen_names.add(row.container_name)

    session.commit()
    return {"status": "ok", "removed": removed}


@router.get("/servers/{server_id}/containers")
def server_containers(server_id: int, session: Session = Depends(get_session)) -> list[dict]:
    if not session.get(Server, server_id):
        raise HTTPException(status_code=404, detail="Server not found")
    return latest_container_snapshots(session, server_id)


@router.get("/servers/{server_id}/containers/{container_id}/logs")
async def container_logs(
    server_id: int,
    container_id: str,
    lines: int = Query(default=100, ge=1, le=2000),
    filter: str | None = None,
    session: Session = Depends(get_session),
) -> dict:
    server = session.get(Server, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    try:
        return await AgentClient(server.url, decrypt_text(server.api_key_encrypted)).get(
            f"/api/docker/containers/{container_id}/logs",
            params={"lines": lines, "filter": filter},
        )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/servers/{server_id}/containers/{container_id}/stats")
async def container_stats(server_id: int, container_id: str, session: Session = Depends(get_session)) -> dict:
    server = session.get(Server, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    try:
        return await AgentClient(server.url, decrypt_text(server.api_key_encrypted)).get(
            f"/api/docker/containers/{container_id}/stats"
        )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
