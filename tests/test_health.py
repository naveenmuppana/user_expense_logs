
def test_database_health_check_succeeds(client):
    response = client.get("/health/db")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "database": "Connected",
    }


from unittest.mock import Mock

from app.core.database import get_db


def test_database_health_check_fails(client):
    mock_db = Mock()
    mock_db.execute.side_effect = Exception("Simulated database failure")

    def override_get_db():
        yield mock_db

    from app.main import app

    app.dependency_overrides[get_db] = override_get_db

    try:
        response = client.get("/health/db")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Database unavailable"
    }
