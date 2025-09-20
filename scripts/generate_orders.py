from datetime import datetime, timedelta
import random

random.seed(42)

from tqdm import tqdm

from scripts.create_order import (
    login,
    create_order,
    get_available_orders,
    optimize_order,
)

from app.auth.utils import hash_password
from app.database import DatabaseManager
from app.crud import create_user
from app.models.user import User
from generate_addresses import GENERATED_ADDRESSES

from faker import Faker

fake = Faker("it_IT")
Faker.seed(42)


def sample_address(address_dict: dict):
    postal_code = random.choice(list(address_dict))
    address = random.choice(address_dict[postal_code])
    return postal_code, address


"""
Route Planner API error: 400, error code: 6004,
'Request parameters exceed the server configuration limits.
Only a total of 3500 routes are allowed.
Hence, OpenRouteService can handle only 59*59 orders 
"""
N_ORDERS = 10
# Assuming pizza reservations can be taken within a 45-minute windown
PIZZA_RESERVATIONS_WINDOW = (15, 45)
with DatabaseManager() as db_session:
    print(f"Creating {N_ORDERS} Users ...")
    users_dict = dict()
    for _ in tqdm(range(N_ORDERS), total=N_ORDERS):
        # Create Users in DB
        user_email = fake.email()
        user_full_name = fake.name()
        user_password = fake.password()
        user_phone = fake.phone_number()
        users_dict[user_email] = {
            "email": user_email,
            "password": user_password,
            "full_name": user_full_name,
            "customer_phone": str(user_phone),
            "role": "user",
        }
        user_in = User(
            email=user_email,
            hashed_password=hash_password(user_password),
            full_name=user_full_name,
            role="user",
        )
        new_user = create_user(db=db_session, new_user=user_in)
# Create Orders
print("Create Orders ...")
now = datetime.utcnow()
GROUP_A = (now + timedelta(hours=1)).isoformat()
GROUP_B = (now + timedelta(hours=1, minutes=15)).isoformat()
GROUP_C = (now + timedelta(hours=1, minutes=30)).isoformat()
GROUP_D = (now + timedelta(hours=1, minutes=45)).isoformat()
TIME_GROUPS = [GROUP_A, GROUP_B, GROUP_C, GROUP_D]

PIZZAS = [
    "Margherita",
    "Diavola",
    "Quattro Formaggi",
    "Capricciosa",
    "Bufala",
    "Vegetariana",
    "Tonno e Cipolla",
    "Quattro Stagioni",
]
DRINKS = ["Coca-Cola", "Pepsi", "Fanta", "Sprite", "Water", "Beer", "Lemonade"]
# Create order payload
ORDER_PAYLOAD_FOR_OPT = dict()
for idx, user_info in enumerate(users_dict.values()):
    postal_code, address = sample_address(GENERATED_ADDRESSES)
    food = random.choices(PIZZAS, k=random.randint(1, 10))
    drink = random.choices(DRINKS, k=random.randint(1, 10))
    prep_time = random.randint(15, 25)
    desired_time = (
        now
        + timedelta(
            minutes=random.randint(
                PIZZA_RESERVATIONS_WINDOW[0], PIZZA_RESERVATIONS_WINDOW[1]
            )
        )
    ).isoformat()

    order_payload = {
        "id": idx + 1,
        "creator_id": idx + 100,
        "status": "pending",
        "created_at": str(now),
        "priority": False,
        "customer_name": user_info["full_name"],
        "customer_phone": user_info["customer_phone"],
        "delivery_address": {
            "address": address,
            "city": "Milan",
            "postal_code": postal_code,
        },
        "items": {"food": food, "drink": drink},
        "estimated_prep_time": prep_time,
        "desired_delivery_time": desired_time,
    }

    token = login(username=user_info["email"], password=user_info["password"])
    create_order(token=token, order_payload=order_payload)

available_orders = get_available_orders()
print(f"Total number of orders: {len(available_orders)}")
_ = optimize_order()
