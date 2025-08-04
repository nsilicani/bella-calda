from datetime import datetime, timedelta


def test_routes_orders(client, base_url, user_credentials):
    ENDPOINT_SIGNUP = f"{base_url}/api/v1/auth/signup"
    response_signup = client.post(
        url=ENDPOINT_SIGNUP,
        json={
            "email": user_credentials["email"],
            "full_name": user_credentials["full_name"],
            "password": user_credentials["password"],
            "role": user_credentials["role"],
        },
    )
    assert response_signup.status_code == 201

    ENDPOINT_LOGIN = f"{base_url}/api/v1/auth/login"
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
    order_payload = {
        "customer_name": "Alice",
        "customer_phone": "+123456789",
        "delivery_address": "123 Pizza Street",
        "items": "Margherita,Pepsi",
        "estimated_prep_time": 20,
        "desired_delivery_time": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
    }
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response_orders = client.post(
        url=ORDERS_ENDPOINT, json=order_payload, headers=headers
    )
    assert response_orders.status_code == 201
