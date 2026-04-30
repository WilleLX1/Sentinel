from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from httpx import HTTPError
from sqlmodel import Session, delete, select

from .agent_client import AgentClient
from .alerts import evaluate_server_alerts, mark_server_offline, mark_server_online, upsert_alert
from .config import get_settings
from .database import engine
from .encryption import decrypt_text
from .health_checks import run_health_check
from .models import (
    ContainerSnapshot,
    HealthCheck,
    HealthCheckResult,
    Server,
    SystemSnapshot,
)
from .notifications import notify_alerts
from .websocket import manager

logger = logging.getLogger("sentinel.dashboard.polling")
scheduler = AsyncIOScheduler()


def start_scheduler() -> None:
    settings = get_settings()
    if scheduler.running:
        return
    scheduler.add_job(poll_all_servers, "interval", seconds=settings.poll_interval_seconds, id="poll-all-servers", replace_existing=True)
    scheduler.start()


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)


async def poll_all_servers() -> None:
    with Session(engine) as session:
        ids = session.exec(select(Server.id)).all()
    for server_id in ids:
        if server_id is not None:
            await poll_server(server_id)


async def poll_server(server_id: int) -> dict:
    with Session(engine) as session:
        server = session.get(Server, server_id)
        if not server:
            return {"status": "missing"}
        return await _poll_server(session, server)


async def _poll_server(session: Session, server: Server) -> dict:
    if server.id is None:
        return {"status": "missing"}
    api_key = decrypt_text(server.api_key_encrypted)
    client = AgentClient(server.url, api_key)

    try:
        ping = await client.get("/api/ping")
        system_data = await client.get("/api/system")
        containers = await client.get("/api/docker/containers")
    except Exception as exc:
        server.status = "offline"
        session.add(server)
        created = mark_server_offline(session, server, f"{server.name} agent is unreachable: {exc}")
        session.commit()
        await notify_alerts(session, created)
        await manager.broadcast({"type": "server.offline", "server_id": server.id})
        return {"status": "offline", "error": str(exc)}

    server.status = "online"
    server.last_seen = datetime.now(timezone.utc)
    server.updated_at = datetime.now(timezone.utc)
    session.add(server)
    mark_server_online(session, server)

    session.add(
        SystemSnapshot(
            server_id=server.id,
            hostname=system_data.get("hostname") or ping.get("server_name"),
            os=system_data.get("os"),
            uptime_seconds=system_data.get("uptime_seconds"),
            cpu_percent=system_data.get("cpu_percent"),
            memory_percent=(system_data.get("memory") or {}).get("percent"),
            disk_percent=(system_data.get("disk") or {}).get("percent"),
        )
    )

    enriched_containers: list[dict] = []
    for container in containers:
        stats = {}
        if container.get("status") == "running":
            try:
                stats = await client.get(f"/api/docker/containers/{container['id']}/stats")
            except HTTPError:
                stats = {}
        enriched = {**container, **stats}
        enriched_containers.append(enriched)
        session.add(
            ContainerSnapshot(
                server_id=server.id,
                container_id=container.get("id") or container.get("name") or "unknown",
                container_name=container.get("name") or "unknown",
                image=container.get("image") or "",
                status=container.get("status") or "unknown",
                health=container.get("health") or "none",
                cpu_percent=stats.get("cpu_percent"),
                memory_mb=stats.get("memory_usage_mb"),
                memory_percent=stats.get("memory_percent"),
                restart_count=container.get("restart_count") or 0,
                ports_json=json.dumps(container.get("ports") or []),
                compose_project=container.get("compose_project"),
                compose_service=container.get("compose_service"),
            )
        )

    created_alerts = evaluate_server_alerts(session, server, system_data, enriched_containers)
    created_alerts.extend(await _run_health_checks(session, server))
    _cleanup_old_snapshots(session)
    session.commit()
    await notify_alerts(session, created_alerts)
    await manager.broadcast({"type": "server.updated", "server_id": server.id})
    return {"status": "online", "containers": len(containers)}


async def _run_health_checks(session: Session, server: Server) -> list:
    if server.id is None:
        return []
    checks = session.exec(
        select(HealthCheck).where(HealthCheck.server_id == server.id, HealthCheck.enabled == True)  # noqa: E712
    ).all()
    created = []
    active: set[str] = set()
    for check in checks:
        result = await run_health_check(check)
        session.add(
            HealthCheckResult(
                health_check_id=check.id or 0,
                success=bool(result.get("success")),
                status_code=result.get("status_code"),
                response_time_ms=result.get("response_time_ms"),
                message=result.get("message") or "",
            )
        )
        if not result.get("success"):
            fp = f"health:{check.id}:failed"
            active.add(fp)
            alert = upsert_alert(
                session,
                server.id,
                "critical",
                "Health check failed",
                f'{check.name} failed: {result.get("message")}',
                "health",
                fp,
            )
            if alert:
                created.append(alert)
    from .alerts import resolve_missing

    resolve_missing(session, server.id, active, {"health"})
    return created


def _cleanup_old_snapshots(session: Session) -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(days=get_settings().metric_retention_days)
    session.exec(delete(SystemSnapshot).where(SystemSnapshot.created_at < cutoff))
    session.exec(delete(ContainerSnapshot).where(ContainerSnapshot.created_at < cutoff))

