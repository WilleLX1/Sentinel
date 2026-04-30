from sqlmodel import SQLModel, Session, create_engine, select

from app.alerts import evaluate_server_alerts
from app.models import Alert, Server


def test_alerts_dedupe_and_resolve():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        server = Server(name="node", url="http://node", api_key_encrypted="x")
        session.add(server)
        session.commit()
        session.refresh(server)

        system = {"disk": {"percent": 90}, "memory": {"percent": 10}, "cpu_percent": 5}
        created = evaluate_server_alerts(session, server, system, [])
        session.commit()
        assert len(created) == 1

        created = evaluate_server_alerts(session, server, system, [])
        session.commit()
        assert len(created) == 0
        assert len(session.exec(select(Alert).where(Alert.resolved == False)).all()) == 1  # noqa: E712

        system = {"disk": {"percent": 20}, "memory": {"percent": 10}, "cpu_percent": 5}
        evaluate_server_alerts(session, server, system, [])
        session.commit()
        assert len(session.exec(select(Alert).where(Alert.resolved == False)).all()) == 0  # noqa: E712

