from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app


def test_ping_requires_bearer_token():
    client = TestClient(app)
    response = client.get("/api/ping")
    assert response.status_code == 401


def test_ping_accepts_valid_api_key():
    client = TestClient(app)
    response = client.get("/api/ping", headers={"Authorization": f"Bearer {get_settings().sentinel_api_key}"})
    assert response.status_code == 200
    assert response.json()["agent"] == "sentinel-agent"


def test_ping_rejects_invalid_api_key():
    client = TestClient(app)
    response = client.get("/api/ping", headers={"Authorization": "Bearer wrong"})
    assert response.status_code == 403

