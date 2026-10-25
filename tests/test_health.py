
from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app


def test_database_health_check_succeeds(client):
    response = client.get("/health/db")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "database": "Connected",
    }


def test_database_health_check_fails(client):
    mock_db = Mock()
    mock_db.execute.side_effect = Exception("Simulated database failure")

    def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    try:
        response = client.get("/health/db")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 500
    assert response.json() == {"detail": "Database unavailable"}


def test_global_exception_handler_returns_safe_message(client):
    @app.get("/test-unexpected-error")
    def trigger_error():
        raise RuntimeError("Sensitive internal database details")

    try:
        with TestClient(app, raise_server_exceptions=False) as test_client:
            response = test_client.get("/test-unexpected-error")
    finally:
        app.router.routes[:] = [
            route
            for route in app.router.routes
            if getattr(route, "path", None) != "/test-unexpected-error"
        ]

    assert response.status_code == 500
    assert response.json() == {
        "detail": "An unexpected error occurred"
    }
    assert "Sensitive internal database details" not in response.text
def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "This is the starting page"
    }