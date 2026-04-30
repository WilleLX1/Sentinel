from __future__ import annotations

import json

from sqlmodel import Session, desc, select

from .models import ContainerSnapshot, SystemSnapshot


def latest_system_snapshot(session: Session, server_id: int) -> SystemSnapshot | None:
    return session.exec(
        select(SystemSnapshot)
        .where(SystemSnapshot.server_id == server_id)
        .order_by(desc(SystemSnapshot.created_at))
        .limit(1)
    ).first()


def latest_container_snapshots(session: Session, server_id: int) -> list[dict]:
    rows = session.exec(
        select(ContainerSnapshot)
        .where(ContainerSnapshot.server_id == server_id)
        .order_by(desc(ContainerSnapshot.created_at))
    ).all()
    seen: set[str] = set()
    result: list[dict] = []
    for row in rows:
        if row.container_id in seen:
            continue
        seen.add(row.container_id)
        result.append(
            {
                "id": row.container_id,
                "name": row.container_name,
                "image": row.image,
                "status": row.status,
                "health": row.health,
                "cpu_percent": row.cpu_percent,
                "memory_mb": row.memory_mb,
                "memory_percent": row.memory_percent,
                "restart_count": row.restart_count,
                "ports": json.loads(row.ports_json or "[]"),
                "compose_project": row.compose_project,
                "compose_service": row.compose_service,
                "created_at": row.created_at,
            }
        )
    return result

