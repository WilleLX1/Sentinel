from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str
    is_admin: bool = True
    created_at: datetime = Field(default_factory=utcnow)


class ServerGroup(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    created_at: datetime = Field(default_factory=utcnow)


class ServerTag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    color: str = "#64748b"
    created_at: datetime = Field(default_factory=utcnow)


class ServerTagLink(SQLModel, table=True):
    server_id: Optional[int] = Field(default=None, foreign_key="server.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="servertag.id", primary_key=True)


class Server(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    url: str
    api_key_encrypted: str
    action_key_encrypted: Optional[str] = None
    status: str = Field(default="unknown", index=True)
    environment: str = "production"
    notes: str = ""
    group_id: Optional[int] = Field(default=None, foreign_key="servergroup.id")
    last_seen: Optional[datetime] = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class SystemSnapshot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    server_id: int = Field(foreign_key="server.id", index=True)
    hostname: Optional[str] = None
    os: Optional[str] = None
    uptime_seconds: Optional[int] = None
    cpu_percent: Optional[float] = None
    memory_percent: Optional[float] = None
    disk_percent: Optional[float] = None
    created_at: datetime = Field(default_factory=utcnow, index=True)


class ContainerSnapshot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    server_id: int = Field(foreign_key="server.id", index=True)
    container_id: str = Field(index=True)
    container_name: str = Field(index=True)
    image: str = ""
    status: str = "unknown"
    health: str = "none"
    cpu_percent: Optional[float] = None
    memory_mb: Optional[float] = None
    memory_percent: Optional[float] = None
    restart_count: int = 0
    ports_json: str = "[]"
    compose_project: Optional[str] = None
    compose_service: Optional[str] = None
    created_at: datetime = Field(default_factory=utcnow, index=True)


class Alert(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    server_id: int = Field(foreign_key="server.id", index=True)
    severity: str = Field(index=True)
    title: str
    message: str
    source: str = Field(default="system", index=True)
    fingerprint: str = Field(index=True)
    resolved: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=utcnow, index=True)
    resolved_at: Optional[datetime] = None


class HealthCheck(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    server_id: int = Field(foreign_key="server.id", index=True)
    name: str
    type: str
    target: str
    expected_status: Optional[int] = 200
    timeout_seconds: int = 5
    enabled: bool = True
    created_at: datetime = Field(default_factory=utcnow)


class HealthCheckResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    health_check_id: int = Field(foreign_key="healthcheck.id", index=True)
    success: bool
    status_code: Optional[int] = None
    response_time_ms: Optional[int] = None
    message: str = ""
    created_at: datetime = Field(default_factory=utcnow, index=True)


class NotificationChannel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    type: str
    name: str
    enabled: bool = True
    config_json: str = "{}"
    created_at: datetime = Field(default_factory=utcnow)


class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    actor: str = "system"
    action: str
    resource: str = ""
    details: str = "{}"
    created_at: datetime = Field(default_factory=utcnow, index=True)


class ActionLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    server_id: int = Field(foreign_key="server.id", index=True)
    container_id: Optional[str] = None
    action: str
    status: str
    message: str = ""
    created_at: datetime = Field(default_factory=utcnow, index=True)


class AppSetting(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(index=True, unique=True)
    value: str
    updated_at: datetime = Field(default_factory=utcnow)


class BackupMetadata(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    path: str
    size_bytes: int = 0
    status: str = "created"
    created_at: datetime = Field(default_factory=utcnow, index=True)

