import requests

from constants import BASE_URL, TEST_USERS, ORDER_PAYLOAD


def login(username, password):
    """Authenticate and retrieve access token"""
    url = f"{BASE_URL}/api/v1/auth/login"
    response = requests.post(
        url,
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if response.status_code != 200:
        raise Exception(f"Login failed: {response.status_code} - {response.text}")

    token = response.json()["access_token"]
    return token


def create_order(token, order_payload):
    """Send authenticated request to create an order"""
    url = f"{BASE_URL}/api/v1/orders/order/"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post(url, json=order_payload, headers=headers)

    print(f"Status Code: {response.status_code}")
    print("Response:")
    print(response.json())


def optimize_order():
    ORDERS_OPTIMIZER_ENDPOINT = f"{BASE_URL}/api/v1/orders/optimize/"
    response_optimze = requests.post(url=ORDERS_OPTIMIZER_ENDPOINT)
    print(f"Status Code: {response_optimze.status_code}")
    print("Response:")
    print(response_optimze.json())


def get_available_orders():
    GET_AVAILABLE_ORDERS_ENDPOINT = f"{BASE_URL}/api/v1/orders/available_orders/"
    response_get_available_orders = requests.get(url=GET_AVAILABLE_ORDERS_ENDPOINT)
    print(f"Status Code: {response_get_available_orders.status_code}")
    print("Response:")
    print(response_get_available_orders.json())


if __name__ == "__main__":
    for test_user in TEST_USERS:
        ORDER_PAYLOAD["customer_name"] = test_user["full_name"]
        token = login(username=test_user["email"], password=test_user["password"])
        create_order(token=token, order_payload=ORDER_PAYLOAD)
    print("***" * 20)
    optimize_order()
    get_available_orders()
