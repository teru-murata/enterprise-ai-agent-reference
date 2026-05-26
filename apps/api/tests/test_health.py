from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version_returns_project_metadata() -> None:
    response = client.get("/version")

    assert response.status_code == 200
    assert response.json()["name"] == "enterprise-ai-agent-reference"
    assert response.json()["version"] == "0.1.0"

