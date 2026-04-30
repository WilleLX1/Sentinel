from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from ..auth import get_current_user
from ..database import get_session
from ..models import ContainerSnapshot, Server, SystemSnapshot

router = APIRouter(prefix="/api", tags=["metrics"], dependencies=[Depends(get_current_user)])


@router.get("/servers/{server_id}/metrics/system")
def system_metrics(server_id: int, hours: int = Query(default=24, ge=1, le=720), session: Session = Depends(get_session)) -> list[SystemSnapshot]:
    if not session.get(Server, server_id):
        raise HTTPException(status_code=404, detail="Server not found")
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    return session.exec(
        select(SystemSnapshot)
        .where(SystemSnapshot.server_id == server_id, SystemSnapshot.created_at >= cutoff)
        .order_by(SystemSnapshot.created_at)
    ).all()


@router.get("/servers/{server_id}/metrics/containers")
def container_metrics(server_id: int, hours: int = Query(default=24, ge=1, le=720), session: Session = Depends(get_session)) -> list[ContainerSnapshot]:
    if not session.get(Server, server_id):
        raise HTTPException(status_code=404, detail="Server not found")
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    return session.exec(
        select(ContainerSnapshot)
        .where(ContainerSnapshot.server_id == server_id, ContainerSnapshot.created_at >= cutoff)
        .order_by(ContainerSnapshot.created_at)
    ).all()

