from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select

from ..auth import get_current_user
from ..config import get_settings
from ..database import get_session
from ..models import AppSetting, AuditLog, User, utcnow

router = APIRouter(prefix="/api/settings", tags=["settings"], dependencies=[Depends(get_current_user)])


class SettingPayload(BaseModel):
    key: str
    value: str


@router.get("")
def read_settings(session: Session = Depends(get_session)) -> dict:
    settings = get_settings()
    rows = session.exec(select(AppSetting).order_by(AppSetting.key)).all()
    return {
        "runtime": {
            "poll_interval_seconds": settings.poll_interval_seconds,
            "metric_retention_days": settings.metric_retention_days,
            "database_url": settings.dashboard_database_url,
            "notifications": {
                "discord_env_configured": bool(settings.discord_webhook_url),
                "smtp_env_configured": bool(settings.smtp_host and settings.smtp_from and settings.smtp_to),
            },
        },
        "settings": rows,
    }


@router.put("")
def upsert_setting(payload: SettingPayload, session: Session = Depends(get_session), user: User = Depends(get_current_user)) -> AppSetting:
    row = session.exec(select(AppSetting).where(AppSetting.key == payload.key)).first()
    if row:
        row.value = payload.value
        row.updated_at = utcnow()
    else:
        row = AppSetting(key=payload.key, value=payload.value)
    session.add(row)
    session.add(AuditLog(actor=user.username, action="setting.upsert", resource=payload.key))
    session.commit()
    session.refresh(row)
    return row

