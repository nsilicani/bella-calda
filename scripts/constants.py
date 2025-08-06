from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

TEST_USERS = [
    {
        "email": "user@example.com",
        "password": "password123",
        "full_name": "Test User",
        "role": "user",
    },
    {
        "email": "johndoe@gmail.com",
        "password": "password456",
        "full_name": "John Doe",
        "role": "user",
    },
    {
        "email": "FooBar@gmail.com",
        "password": "password789",
        "full_name": "Foo Bar",
        "role": "user",
    },
]
ORDER_PAYLOAD = {
    "customer_name": "{user_customer_name}",
    "customer_phone": "+123456789",
    "delivery_address": {
        "address": "Via Roma 42",
        "city": "Milan",
        "postal_code": "20121",
    },
    "items": "Margherita,Pepsi",
    "estimated_prep_time": 20,
    "desired_delivery_time": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
}

ORDER_PAYLOAD_FOR_CLUSTERING = {
    "Test User": {
        "customer_name": "Test User",
        "customer_phone": "+123456789",
        "delivery_address": {
            "address": "Corso Buenos Aires 33",
            "city": "Milan",
            "postal_code": "20124",
        },
        "items": "Margherita,Pepsi",
        "estimated_prep_time": 20,
        "desired_delivery_time": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
    },
    "John Doe": {
        "customer_name": "John Doe",
        "customer_phone": "+123456789",
        "delivery_address": {
            "address": "Piazza Duomo 24",
            "city": "Milan",
            "postal_code": "20121",
        },
        "items": "Margherita,Pepsi",
        "estimated_prep_time": 20,
        "desired_delivery_time": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
    },
    "Foo Bar": {
        "customer_name": "Foo Bar",
        "customer_phone": "+123456789",
        "delivery_address": {
            # Add a near address to previous order:
            "address": "Piazza Duomo 26",
            "city": "Milan",
            "postal_code": "20121",
        },
        "items": "Margherita,Pepsi",
        "estimated_prep_time": 20,
        "desired_delivery_time": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
    },
}
