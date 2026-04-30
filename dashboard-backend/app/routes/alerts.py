from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, desc, select

from ..auth import get_current_user
from ..database import get_session
from ..models import Alert

router = APIRouter(prefix="/api/alerts", tags=["alerts"], dependencies=[Depends(get_current_user)])


@router.get("")
def list_alerts(
    resolved: bool | None = Query(default=None),
    severity: str | None = None,
    session: Session = Depends(get_session),
) -> list[Alert]:
    query = select(Alert)
    if resolved is not None:
        query = query.where(Alert.resolved == resolved)
    if severity:
        query = query.where(Alert.severity == severity)
    return session.exec(query.order_by(desc(Alert.created_at)).limit(500)).all()


@router.post("/{alert_id}/resolve")
def resolve_alert(alert_id: int, session: Session = Depends(get_session)) -> dict:
    alert = session.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.resolved = True
    alert.resolved_at = datetime.now(timezone.utc)
    session.add(alert)
    session.commit()
    return {"status": "resolved"}

