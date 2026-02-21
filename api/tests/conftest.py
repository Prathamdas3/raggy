import os
import pytest
from typing import Any

os.environ["ENV"] = "testing"
os.environ["DEBUG"] = "true"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"


from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session
from sqlalchemy.pool import StaticPool
from sqlalchemy import text

from app.utils import HandlePassword

TEST_DATABASE_URL = "sqlite:///./test_db.sqlite"
TEST_PASSWORD = "Test@1234"


@pytest.fixture(scope="function")
def test_engine():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    with engine.connect() as conn:
        conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, email TEXT NOT NULL UNIQUE, password TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
            )
        )
        conn.commit()
    yield engine
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS users"))
        conn.commit()
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine: Any):
    with Session(test_engine) as session:
        yield session


@pytest.fixture(scope="function")
def client(db_session: Any):
    from app.main import app
    from app.db.db import get_session

    def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db_session: Any):
    from app.db.schema import Users

    password_handler = HandlePassword()
    hashed = password_handler.get_hashed_password(TEST_PASSWORD)

    user = Users(email="testuser@example.com", password=hashed)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return {"id": str(user.id), "email": user.email, "password": TEST_PASSWORD}


@pytest.fixture(scope="function")
def auth_cookies(client: Any, test_user: Any) :
    response = client.post(
        "/api/v1/auth/sign-in",
        json={"email": test_user["email"], "password": test_user["password"]},
    )
    assert response.status_code == 200

    cookies = {}
    for cookie in client.cookies:
        cookies[cookie.name] = cookie.value

    return cookies
