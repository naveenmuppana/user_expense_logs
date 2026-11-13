
import os
from urllib.parse import urlparse

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.core.token import create_access_token
from app.main import app
from app.models import Expense, User

load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    raise RuntimeError("TEST_DATABASE_URL is missing")

parsed_test_url = urlparse(TEST_DATABASE_URL)
test_database_name = parsed_test_url.path.lstrip("/")

if test_database_name != "expense_tracker_test":
    raise RuntimeError(
        "Tests must use the expense_tracker_test database"
    )

test_engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


@pytest.fixture(autouse=True)
def clean_test_data():
    with test_engine.begin() as connection:
        connection.execute(delete(Expense))
        connection.execute(delete(User))


@pytest.fixture
def test_user():
    db = TestingSessionLocal()

    try:
        user = User(
            username="testuser",
            email="testuser@example.com",
            hashed_password=hash_password("TestPassword123"),
            is_active=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user.id

    finally:
        db.close()


@pytest.fixture
def auth_headers(test_user):
    token = create_access_token(test_user)

    return {
        "Authorization": f"Bearer {token}"
    }


@pytest.fixture
def client(auth_headers):
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            test_client.headers.update(auth_headers)
            yield test_client
    finally:
        app.dependency_overrides.clear()
