from datetime import timedelta

from sqlmodel import SQLModel, Session, create_engine

from app.models import ContainerSnapshot, SystemSnapshot, utcnow
from app.queries import latest_container_snapshots


def test_latest_container_snapshots_uses_latest_poll_and_dedupes_by_name():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)

    older = utcnow() - timedelta(minutes=5)
    latest = utcnow()

    with Session(engine) as session:
        session.add(SystemSnapshot(server_id=1, created_at=older))
        session.add(
            ContainerSnapshot(
                server_id=1,
                container_id="old-id",
                container_name="sentinel-agent",
                image="sentinel-agent:latest",
                status="running",
                created_at=older + timedelta(seconds=1),
            )
        )
        session.add(SystemSnapshot(server_id=1, created_at=latest))
        session.add(
            ContainerSnapshot(
                server_id=1,
                container_id="new-id",
                container_name="sentinel-agent",
                image="sentinel-agent:latest",
                status="running",
                created_at=latest + timedelta(seconds=1),
            )
        )
        session.commit()

        rows = latest_container_snapshots(session, 1)

    assert len(rows) == 1
    assert rows[0]["id"] == "new-id"
    assert rows[0]["name"] == "sentinel-agent"

