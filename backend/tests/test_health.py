"""Check the HTTP contract used by the frontend's connection indicator."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_health_is_available_at_the_versioned_api_path(tmp_path):
    with TestClient(create_app(tmp_path/'scanner.sqlite3')) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {"status": "ok"}
