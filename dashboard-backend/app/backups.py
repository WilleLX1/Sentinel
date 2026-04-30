from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import shutil

from sqlmodel import Session

from .config import get_settings
from .models import BackupMetadata


def _sqlite_path() -> Path:
    url = get_settings().dashboard_database_url
    if not url.startswith("sqlite:///") or url == "sqlite:///:memory:":
        raise RuntimeError("Backups currently support sqlite:/// database URLs")
    path = Path(url.replace("sqlite:///", "", 1))
    return path if path.is_absolute() else Path.cwd() / path


def create_backup(session: Session) -> BackupMetadata:
    source = _sqlite_path()
    backups_dir = Path(get_settings().backups_dir)
    backups_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destination = backups_dir / f"sentinel-{timestamp}.db"
    shutil.copy2(source, destination)
    metadata = BackupMetadata(
        filename=destination.name,
        path=str(destination),
        size_bytes=destination.stat().st_size,
        status="created",
    )
    session.add(metadata)
    session.commit()
    session.refresh(metadata)
    return metadata

