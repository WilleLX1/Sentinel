from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from ..auth import get_current_user
from ..database import get_session
from ..models import NotificationChannel
from ..notifications import send_test_notification

router = APIRouter(prefix="/api/notifications", tags=["notifications"], dependencies=[Depends(get_current_user)])


class NotificationPayload(BaseModel):
    type: str
    name: str
    enabled: bool = True
    config: dict = {}


def channel_read(channel: NotificationChannel) -> dict:
    config = json.loads(channel.config_json or "{}")
    masked = {key: ("[CONFIGURED]" if "password" in key.lower() or "webhook" in key.lower() else value) for key, value in config.items()}
    return {
        "id": channel.id,
        "type": channel.type,
        "name": channel.name,
        "enabled": channel.enabled,
        "config": masked,
        "created_at": channel.created_at,
    }


@router.get("")
def list_channels(session: Session = Depends(get_session)) -> list[dict]:
    return [channel_read(c) for c in session.exec(select(NotificationChannel).order_by(NotificationChannel.name)).all()]


@router.post("")
def create_channel(payload: NotificationPayload, session: Session = Depends(get_session)) -> dict:
    channel = NotificationChannel(
        type=payload.type,
        name=payload.name,
        enabled=payload.enabled,
        config_json=json.dumps(payload.config),
    )
    session.add(channel)
    session.commit()
    session.refresh(channel)
    return channel_read(channel)


@router.put("/{channel_id}")
def update_channel(channel_id: int, payload: NotificationPayload, session: Session = Depends(get_session)) -> dict:
    channel = session.get(NotificationChannel, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Notification channel not found")
    channel.type = payload.type
    channel.name = payload.name
    channel.enabled = payload.enabled
    channel.config_json = json.dumps(payload.config)
    session.add(channel)
    session.commit()
    session.refresh(channel)
    return channel_read(channel)


@router.delete("/{channel_id}")
def delete_channel(channel_id: int, session: Session = Depends(get_session)) -> dict:
    channel = session.get(NotificationChannel, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Notification channel not found")
    session.delete(channel)
    session.commit()
    return {"status": "deleted"}


@router.post("/{channel_id}/test")
async def test_channel(channel_id: int, session: Session = Depends(get_session)) -> dict:
    channel = session.get(NotificationChannel, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Notification channel not found")
    return await send_test_notification(channel)

