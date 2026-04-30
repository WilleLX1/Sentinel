from __future__ import annotations

from datetime import datetime, timezone

from sqlmodel import Session, select

from .models import Alert, Server

MANAGED_SOURCES = {"agent", "system", "container", "health"}


def upsert_alert(
    session: Session,
    server_id: int,
    severity: str,
    title: str,
    message: str,
    source: str,
    fingerprint: str,
) -> Alert | None:
    existing = session.exec(
        select(Alert).where(Alert.server_id == server_id, Alert.fingerprint == fingerprint, Alert.resolved == False)  # noqa: E712
    ).first()
    if existing:
        if existing.severity != severity or existing.message != message:
            existing.severity = severity
            existing.message = message
            session.add(existing)
        return None
    alert = Alert(
        server_id=server_id,
        severity=severity,
        title=title,
        message=message,
        source=source,
        fingerprint=fingerprint,
    )
    session.add(alert)
    session.flush()
    return alert


def resolve_missing(session: Session, server_id: int, active_fingerprints: set[str], sources: set[str] | None = None) -> None:
    source_filter = sources or MANAGED_SOURCES
    unresolved = session.exec(
        select(Alert).where(Alert.server_id == server_id, Alert.resolved == False)  # noqa: E712
    ).all()
    now = datetime.now(timezone.utc)
    for alert in unresolved:
        if alert.source in source_filter and alert.fingerprint not in active_fingerprints:
            alert.resolved = True
            alert.resolved_at = now
            session.add(alert)


def evaluate_server_alerts(session: Session, server: Server, system_data: dict | None, containers: list[dict]) -> list[Alert]:
    if server.id is None:
        return []

    active: set[str] = set()
    created: list[Alert] = []

    if system_data:
        disk_percent = float((system_data.get("disk") or {}).get("percent") or 0)
        memory_percent = float((system_data.get("memory") or {}).get("percent") or 0)
        cpu_percent = float(system_data.get("cpu_percent") or 0)

        if disk_percent >= 95:
            fp = "system:disk-critical"
            active.add(fp)
            alert = upsert_alert(session, server.id, "critical", "Disk usage critical", f"{server.name} disk usage is {disk_percent:.1f}%.", "system", fp)
            if alert:
                created.append(alert)
        elif disk_percent >= 85:
            fp = "system:disk-warning"
            active.add(fp)
            alert = upsert_alert(session, server.id, "warning", "Disk usage warning", f"{server.name} disk usage is {disk_percent:.1f}%.", "system", fp)
            if alert:
                created.append(alert)

        if memory_percent >= 95:
            fp = "system:memory-critical"
            active.add(fp)
            alert = upsert_alert(session, server.id, "critical", "Memory usage critical", f"{server.name} memory usage is {memory_percent:.1f}%.", "system", fp)
            if alert:
                created.append(alert)
        elif memory_percent >= 90:
            fp = "system:memory-warning"
            active.add(fp)
            alert = upsert_alert(session, server.id, "warning", "Memory usage warning", f"{server.name} memory usage is {memory_percent:.1f}%.", "system", fp)
            if alert:
                created.append(alert)

        if cpu_percent >= 95:
            fp = "system:cpu-critical"
            active.add(fp)
            alert = upsert_alert(session, server.id, "critical", "CPU usage critical", f"{server.name} CPU usage is {cpu_percent:.1f}%.", "system", fp)
            if alert:
                created.append(alert)

    for container in containers:
        name = container.get("name") or container.get("container_name") or container.get("id") or "unknown"
        ident = container.get("id") or name
        status = container.get("status")
        health = container.get("health")

        if status != "running":
            fp = f"container:{ident}:stopped"
            active.add(fp)
            alert = upsert_alert(session, server.id, "critical", "Container stopped", f'Container "{name}" is {status}.', "container", fp)
            if alert:
                created.append(alert)

        if health == "unhealthy":
            fp = f"container:{ident}:unhealthy"
            active.add(fp)
            alert = upsert_alert(session, server.id, "critical", "Container unhealthy", f'Container "{name}" is unhealthy.', "container", fp)
            if alert:
                created.append(alert)

    resolve_missing(session, server.id, active, {"system", "container"})
    return created


def mark_server_offline(session: Session, server: Server, message: str) -> list[Alert]:
    if server.id is None:
        return []
    fp = "agent:offline"
    alert = upsert_alert(session, server.id, "critical", "Agent offline", message, "agent", fp)
    return [alert] if alert else []


def mark_server_online(session: Session, server: Server) -> None:
    if server.id is None:
        return
    resolve_missing(session, server.id, set(), {"agent"})

