import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, create_new_db_session
from app.models import user, order, driver
from app.models.driver import DriverStatus
from app.models.user import User
from app.schemas.driver import DriverUpdate
from scripts.constants import (
    BASE_URL,
    TEST_USERS,
    ORDER_PAYLOAD,
    TEST_USERS_FOR_CLUSTERING,
    ORDER_PAYLOAD_FOR_CLUSTERING,
    TEST_USER_DRIVERS,
    NUMBER_UPDATE_DRIVERS,
    SIGNUP_ENDPOINT,
    LOGIN_ENDPOINT,
    ORDERS_ENDPOINT,
    DRIVERS_ENDPOINT,
    DRIVER_UPDATE_ENDPOINT,
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
        resp = client.post(
            url=url,
            json={
                "email": user_credential["email"],
                "full_name": user_credential["full_name"],
                "password": user_credential["password"],
                "role": user_credential["role"],
            },
        )
        assert resp.status_code in [201, 200]


@pytest.fixture
def create_users(client, test_users):
    """
    Create test users in test db
    """
    create_users_utils(client=client, url=SIGNUP_ENDPOINT, users=test_users)


@pytest.fixture
def order_payload():
    return ORDER_PAYLOAD


@pytest.fixture
def order_payload_for_clustering():
    return ORDER_PAYLOAD_FOR_CLUSTERING


@pytest.fixture
def create_orders(client, test_users, order_payload):
    """
    Create test orders in test db
    """

    for user_credential in test_users:
        order_payload["customer_name"] = user_credential["full_name"]
        response_login = client.post(
            url=LOGIN_ENDPOINT,
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
def create_users_for_clustering(client, test_users_for_clustering):
    create_users_utils(
        client=client, url=SIGNUP_ENDPOINT, users=test_users_for_clustering
    )


@pytest.fixture
def create_orders_for_clustering(
    client, test_users_for_clustering, order_payload_for_clustering
):
    for user_credential in test_users_for_clustering:
        order_payload = order_payload_for_clustering[user_credential["full_name"]]
        response_login = client.post(
            url=LOGIN_ENDPOINT,
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
def test_driver_users():
    return TEST_USER_DRIVERS


@pytest.fixture
def create_user_drivers(client, test_driver_users, session):
    # First, create user
    create_users_utils(client=client, url=SIGNUP_ENDPOINT, users=test_driver_users)
    # Then, create driver by retrieving user id
    for user_credential in test_driver_users:
        existing_user = (
            session.query(User).filter(User.email == user_credential["email"]).first()
        )
        resp = client.post(
            url=DRIVERS_ENDPOINT,
            json={"user_id": existing_user.id, "full_name": existing_user.full_name},
        )
        assert resp.status_code == 201


@pytest.fixture
def update_user_drivers(client):
    updated_drivers = set()
    response_list_drivers = client.get(url=DRIVERS_ENDPOINT)
    data = response_list_drivers.json()

    for driver in data:
        if len(updated_drivers) >= NUMBER_UPDATE_DRIVERS:
            break

        driver_id = driver["id"]
        driver_full_name = driver["full_name"]

        # Find matching test driver
        for i, test_driver in enumerate(TEST_USER_DRIVERS):
            if (
                driver_full_name == test_driver["full_name"]
                and driver_full_name not in updated_drivers
            ):
                driver_update = DriverUpdate(
                    is_active=True,
                    status=DriverStatus.AVAILABLE,
                    lat=45.46 + i * 0.01,
                    lon=9.18 + i * 0.01,
                    current_route=None,
                    estimated_finish_time=None,
                )

                response_update_driver = client.patch(
                    url=DRIVER_UPDATE_ENDPOINT.format(driver_id=driver_id),
                    json=driver_update.model_dump(),
                )
                assert response_update_driver.status_code == 200
                updated_drivers.add(driver_full_name)
                break
