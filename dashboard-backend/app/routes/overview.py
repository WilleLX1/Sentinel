from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..auth import get_current_user
from ..database import get_session
from ..models import Alert, Server
from ..queries import latest_container_snapshots, latest_system_snapshot

router = APIRouter(prefix="/api", tags=["overview"], dependencies=[Depends(get_current_user)])


@router.get("/overview")
def overview(session: Session = Depends(get_session)) -> dict:
    servers = session.exec(select(Server).order_by(Server.name)).all()
    active_alerts = session.exec(select(Alert).where(Alert.resolved == False)).all()  # noqa: E712
    server_cards = []
    running_containers = 0
    unhealthy_containers = 0

    for server in servers:
        system = latest_system_snapshot(session, server.id or 0)
        containers = latest_container_snapshots(session, server.id or 0)
        running = sum(1 for c in containers if c["status"] == "running")
        unhealthy = sum(1 for c in containers if c["health"] == "unhealthy")
        running_containers += running
        unhealthy_containers += unhealthy
        server_alerts = [a for a in active_alerts if a.server_id == server.id]
        server_cards.append(
            {
                "id": server.id,
                "name": server.name,
                "url": server.url,
                "status": server.status,
                "environment": server.environment,
                "last_seen": server.last_seen,
                "cpu_percent": system.cpu_percent if system else None,
                "memory_percent": system.memory_percent if system else None,
                "disk_percent": system.disk_percent if system else None,
                "running_containers": running,
                "containers_total": len(containers),
                "active_alerts": len(server_alerts),
            }
        )

    return {
        "summary": {
            "total_servers": len(servers),
            "online_servers": sum(1 for s in servers if s.status == "online"),
            "offline_servers": sum(1 for s in servers if s.status == "offline"),
            "running_containers": running_containers,
            "unhealthy_containers": unhealthy_containers,
            "active_alerts": len(active_alerts),
            "critical_alerts": sum(1 for a in active_alerts if a.severity == "critical"),
        },
        "servers": server_cards,
        "alerts": active_alerts[-10:],
    }

