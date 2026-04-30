from __future__ import annotations

from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

from .config import get_settings

settings = get_settings()

connect_args = {"check_same_thread": False} if settings.dashboard_database_url.startswith("sqlite") else {}
engine = create_engine(settings.dashboard_database_url, connect_args=connect_args)


def _ensure_sqlite_parent() -> None:
    url = settings.dashboard_database_url
    if not url.startswith("sqlite:///") or url == "sqlite:///:memory:":
        return
    db_path = Path(url.replace("sqlite:///", "", 1))
    if not db_path.is_absolute():
        db_path = Path.cwd() / db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)


def create_db_and_tables() -> None:
    _ensure_sqlite_parent()
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

