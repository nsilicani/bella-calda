import requests

from constants import (
    LOGIN_ENDPOINT,
    CREATE_ORDER_ENDPOINT,
    ORDERS_OPTIMIZER_ENDPOINT,
    GET_AVAILABLE_ORDERS_ENDPOINT,
    CLUSTER_ENDPOINT,
    TEST_USERS_FOR_CLUSTERING,
    ORDER_PAYLOAD_FOR_CLUSTERING,
)


def login(username, password):
    """Authenticate and retrieve access token"""
    response = requests.post(
        LOGIN_ENDPOINT,
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if response.status_code != 200:
        raise Exception(f"Login failed: {response.status_code} - {response.text}")

    token = response.json()["access_token"]
    return token


def create_order(token, order_payload):
    """Send authenticated request to create an order"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post(CREATE_ORDER_ENDPOINT, json=order_payload, headers=headers)

    print(f"Status Code: {response.status_code}")
    print("Response:")
    print(response.json())


def optimize_order():
    response_optimze = requests.post(url=ORDERS_OPTIMIZER_ENDPOINT)
    print(f"Status Code: {response_optimze.status_code}")
    print("Response:")
    print(response_optimze.json())


def get_available_orders():
    response_get_available_orders = requests.get(url=GET_AVAILABLE_ORDERS_ENDPOINT)
    print(f"Status Code: {response_get_available_orders.status_code}")
    print("Response:")
    print(response_get_available_orders.json())


def cluster_orders():
    response_cluster_orders = requests.get(url=CLUSTER_ENDPOINT)
    print(f"Status Code: {response_cluster_orders.status_code}")
    print("Response:")
    data = response_cluster_orders.json()
    for idx, cluster in enumerate(data):
        print(f"Cluster: {idx}, ")
        for order in cluster:
            print(order["delivery_address"], order)
        print("\n")


if __name__ == "__main__":
    for test_user in TEST_USERS_FOR_CLUSTERING:
        order_payload = ORDER_PAYLOAD_FOR_CLUSTERING[test_user["full_name"]]
        token = login(username=test_user["email"], password=test_user["password"])
        create_order(token=token, order_payload=order_payload)
    print("***" * 20)
    optimize_order()
    get_available_orders()
    cluster_orders()
