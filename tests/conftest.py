import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, create_new_db_session
from app.models import user, order, driver
from scripts.constants import (
    BASE_URL,
    TEST_USERS,
    ORDER_PAYLOAD,
    TEST_USERS_FOR_CLUSTERING,
    ORDER_PAYLOAD_FOR_CLUSTERING,
)

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
    return BASE_URL


@pytest.fixture
def user_credentials():
    return {
        "email": "user@example.com",
        "password": "password123",
        "full_name": "Test User",
        "role": "user",
    }


@pytest.fixture
def test_users():
    return TEST_USERS


def create_users_utils(client, url, users):
    """
    Create test users in test db
    """

    for user_credential in users:
        client.post(
            url=url,
            json={
                "email": user_credential["email"],
                "full_name": user_credential["full_name"],
                "password": user_credential["password"],
                "role": user_credential["role"],
            },
        )


@pytest.fixture
def create_users(client, base_url, test_users):
    """
    Create test users in test db
    """
    ENDPOINT_SIGNUP = f"{base_url}/api/v1/auth/signup"
    create_users_utils(client=client, url=ENDPOINT_SIGNUP, users=test_users)


@pytest.fixture
def order_payload():
    return ORDER_PAYLOAD


@pytest.fixture
def order_payload_for_clustering():
    return ORDER_PAYLOAD_FOR_CLUSTERING


@pytest.fixture
def create_orders(client, base_url, test_users, order_payload):
    """
    Create test orders in test db
    """

    ENDPOINT_LOGIN = f"{base_url}/api/v1/auth/login"
    ORDERS_ENDPOINT = f"{base_url}/api/v1/orders/order/"
    for user_credential in test_users:
        order_payload["customer_name"] = user_credential["full_name"]
        response_login = client.post(
            url=ENDPOINT_LOGIN,
            data={
                "username": user_credential["email"],
                "password": user_credential["password"],
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token = response_login.json()["access_token"]
        order_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        client.post(url=ORDERS_ENDPOINT, json=order_payload, headers=order_headers)


@pytest.fixture
def test_users_for_clustering():
    return TEST_USERS_FOR_CLUSTERING


@pytest.fixture
def create_users_for_clustering(client, base_url, test_users_for_clustering):
    ENDPOINT_SIGNUP = f"{base_url}/api/v1/auth/signup"
    create_users_utils(
        client=client, url=ENDPOINT_SIGNUP, users=test_users_for_clustering
    )


@pytest.fixture
def create_orders_for_clustering(
    client, base_url, test_users_for_clustering, order_payload_for_clustering
):
    ENDPOINT_LOGIN = f"{base_url}/api/v1/auth/login"
    ORDERS_ENDPOINT = f"{base_url}/api/v1/orders/order/"
    for user_credential in test_users_for_clustering:
        order_payload = order_payload_for_clustering[user_credential["full_name"]]
        response_login = client.post(
            url=ENDPOINT_LOGIN,
            data={
                "username": user_credential["email"],
                "password": user_credential["password"],
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token = response_login.json()["access_token"]
        order_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        client.post(url=ORDERS_ENDPOINT, json=order_payload, headers=order_headers)
