from datetime import datetime, timedelta

from scripts.constants import ORDER_PAYLOAD


def test_routes_create_order(client, create_users, base_url, user_credentials):
    ENDPOINT_LOGIN = f"{base_url}/api/v1/auth/login"

    # Assert unauthorized
    unauthorized_response_login = client.post(
        url=ENDPOINT_LOGIN,
        data={
            "username": "user_not_in_db",
            "password": "wrong_password",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert unauthorized_response_login.status_code == 401

    # Assert authorized and store access token
    response_login = client.post(
        url=ENDPOINT_LOGIN,
        data={
            "username": user_credentials["email"],
            "password": user_credentials["password"],
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response_login.status_code == 200
    token = response_login.json()["access_token"]

    ORDERS_ENDPOINT = f"{base_url}/api/v1/orders/order/"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response_orders = client.post(
        url=ORDERS_ENDPOINT, json=ORDER_PAYLOAD, headers=headers
    )
    assert response_orders.status_code == 201


def test_routes_order_optimizer(client, base_url, create_users, create_orders):
    ORDERS_OPTIMIZER_ENDPOINT = f"{base_url}/api/v1/orders/optimize/"
    response_optimze = client.post(url=ORDERS_OPTIMIZER_ENDPOINT)
    assert response_optimze.status_code == 200
