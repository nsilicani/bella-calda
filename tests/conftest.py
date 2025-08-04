import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, create_new_db_session
from app.models import user, order, driver

DATABASE_URL = "sqlite://"


# See: https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/#client-fixture
@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[create_new_db_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def base_url():
    return "http://localhost:8000"


@pytest.fixture
def user_credentials():
    return {
        "email": "user@example.com",
        "password": "password123",
        "full_name": "Test User",
        "role": "user",
    }
