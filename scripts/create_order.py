import requests
from datetime import datetime, timedelta

# ✅ API base URL
BASE_URL = "http://localhost:8000"

# ✅ Login credentials
EMAIL = "user@example.com"
PASSWORD = "password123"

# ✅ Order payload
order_payload = {
    "customer_name": "Alice",
    "customer_phone": "+123456789",
    "delivery_address": "123 Pizza Street",
    "items": "Margherita,Pepsi",
    "estimated_prep_time": 20,
    "desired_delivery_time": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
}


def login():
    """Authenticate and retrieve access token"""
    url = f"{BASE_URL}/api/v1/auth/login"
    response = requests.post(
        url,
        data={"username": EMAIL, "password": PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if response.status_code != 200:
        raise Exception(f"Login failed: {response.status_code} - {response.text}")

    token = response.json()["access_token"]
    return token


def create_order(token):
    """Send authenticated request to create an order"""
    url = f"{BASE_URL}/api/v1/orders/order/"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post(url, json=order_payload, headers=headers)

    print(f"Status Code: {response.status_code}")
    print("Response:")
    print(response.json())


if __name__ == "__main__":
    token = login()
    create_order(token)
