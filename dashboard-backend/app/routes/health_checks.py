from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, desc, select

from ..auth import get_current_user
from ..database import get_session
from ..health_checks import run_health_check
from ..models import HealthCheck, HealthCheckResult, Server

router = APIRouter(prefix="/api/health-checks", tags=["health-checks"], dependencies=[Depends(get_current_user)])


class HealthCheckPayload(BaseModel):
    server_id: int
    name: str
    type: str
    target: str
    expected_status: int | None = 200
    timeout_seconds: int = 5
    enabled: bool = True


@router.get("")
def list_checks(session: Session = Depends(get_session)) -> list[HealthCheck]:
    return session.exec(select(HealthCheck).order_by(HealthCheck.name)).all()


@router.post("")
def create_check(payload: HealthCheckPayload, session: Session = Depends(get_session)) -> HealthCheck:
    if not session.get(Server, payload.server_id):
        raise HTTPException(status_code=404, detail="Server not found")
    check = HealthCheck(**payload.model_dump())
    session.add(check)
    session.commit()
    session.refresh(check)
    return check


@router.put("/{check_id}")
def update_check(check_id: int, payload: HealthCheckPayload, session: Session = Depends(get_session)) -> HealthCheck:
    check = session.get(HealthCheck, check_id)
    if not check:
        raise HTTPException(status_code=404, detail="Health check not found")
    for key, value in payload.model_dump().items():
        setattr(check, key, value)
    session.add(check)
    session.commit()
    session.refresh(check)
    return check


@router.delete("/{check_id}")
def delete_check(check_id: int, session: Session = Depends(get_session)) -> dict:
    check = session.get(HealthCheck, check_id)
    if not check:
        raise HTTPException(status_code=404, detail="Health check not found")
    session.delete(check)
    session.commit()
    return {"status": "deleted"}


@router.post("/{check_id}/run")
async def run_check(check_id: int, session: Session = Depends(get_session)) -> dict:
    check = session.get(HealthCheck, check_id)
    if not check:
        raise HTTPException(status_code=404, detail="Health check not found")
    result = await run_health_check(check)
    row = HealthCheckResult(
        health_check_id=check.id or 0,
        success=bool(result.get("success")),
        status_code=result.get("status_code"),
        response_time_ms=result.get("response_time_ms"),
        message=result.get("message") or "",
    )
    session.add(row)
    session.commit()
    return result


@router.get("/{check_id}/results")
def check_results(check_id: int, session: Session = Depends(get_session)) -> list[HealthCheckResult]:
    return session.exec(
        select(HealthCheckResult)
        .where(HealthCheckResult.health_check_id == check_id)
        .order_by(desc(HealthCheckResult.created_at))
        .limit(100)
    ).all()

