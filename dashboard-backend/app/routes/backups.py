from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlmodel import Session, desc, select

from ..auth import get_current_user
from ..backups import create_backup
from ..database import get_session
from ..models import Alert, BackupMetadata, ContainerSnapshot, Server, SystemSnapshot

router = APIRouter(prefix="/api", tags=["backups"], dependencies=[Depends(get_current_user)])


@router.get("/backups")
def list_backups(session: Session = Depends(get_session)) -> list[BackupMetadata]:
    return session.exec(select(BackupMetadata).order_by(desc(BackupMetadata.created_at))).all()


@router.post("/backups")
def create_database_backup(session: Session = Depends(get_session)) -> BackupMetadata:
    return create_backup(session)


@router.get("/backups/{backup_id}/download")
def download_backup(backup_id: int, session: Session = Depends(get_session)) -> FileResponse:
    backup = session.get(BackupMetadata, backup_id)
    if not backup or not Path(backup.path).exists():
        raise HTTPException(status_code=404, detail="Backup not found")
    return FileResponse(backup.path, filename=backup.filename)


@router.get("/export/report")
def export_report(session: Session = Depends(get_session)) -> dict:
    return {
        "servers": session.exec(select(Server)).all(),
        "latest_system_snapshots": session.exec(select(SystemSnapshot).order_by(desc(SystemSnapshot.created_at)).limit(100)).all(),
        "latest_container_snapshots": session.exec(select(ContainerSnapshot).order_by(desc(ContainerSnapshot.created_at)).limit(250)).all(),
        "active_alerts": session.exec(select(Alert).where(Alert.resolved == False).order_by(desc(Alert.created_at))).all(),  # noqa: E712
    }

