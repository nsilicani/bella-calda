from datetime import datetime, timedelta

# Endpoints
BASE_URL = "http://localhost:8000"
SIGNUP_ENDPOINT = f"{BASE_URL}/api/v1/auth/signup"
LOGIN_ENDPOINT = f"{BASE_URL}/api/v1/auth/login"
ORDERS_ENDPOINT = f"{BASE_URL}/api/v1/orders/order/"
ORDERS_OPTIMIZER_ENDPOINT = f"{BASE_URL}/api/v1/orders/optimize/"
GET_AVAILABLE_ORDERS_ENDPOINT = f"{BASE_URL}/api/v1/orders/available_orders/"
CLUSTER_BY_TIME_ENDPOINT = f"{BASE_URL}/api/v1/orders/clusters_by_time"
CLUSTER_ENDPOINT = f"{BASE_URL}/api/v1/orders/clusters"
DRIVERS_ENDPOINT = f"{BASE_URL}/api/v1/drivers/"
DRIVER_UPDATE_ENDPOINT = f"{BASE_URL}/api/v1/drivers/{{driver_id}}"
DRIVER_GET_AVAILABLE_ENDPOINT = f"{BASE_URL}/api/v1/drivers/available"

# Test Order
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
    "items": {"food": ["Margherita"], "drink": ["Pepsi"]},
    "estimated_prep_time": 20,
    "desired_delivery_time": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
}

# Test Clustering
TEST_USERS_FOR_CLUSTERING = [
    {
        "email": "alice.rossi@example.com",
        "password": "pass1234",
        "full_name": "Alice Rossi",
        "role": "user",
    },
    {
        "email": "marco.bianchi@example.com",
        "password": "pass5678",
        "full_name": "Marco Bianchi",
        "role": "user",
    },
    {
        "email": "lucia.verdi@example.com",
        "password": "pass9012",
        "full_name": "Lucia Verdi",
        "role": "user",
    },
    {
        "email": "giovanni.neri@example.com",
        "password": "pass3456",
        "full_name": "Giovanni Neri",
        "role": "user",
    },
    {
        "email": "anna.mancini@example.com",
        "password": "pass7890",
        "full_name": "Anna Mancini",
        "role": "user",
    },
    {
        "email": "luca.russo@example.com",
        "password": "pass1470",
        "full_name": "Luca Russo",
        "role": "user",
    },
    {
        "email": "chiara.ferri@example.com",
        "password": "pass2580",
        "full_name": "Chiara Ferri",
        "role": "user",
    },
    {
        "email": "davide.martini@example.com",
        "password": "pass3690",
        "full_name": "Davide Martini",
        "role": "user",
    },
    {
        "email": "elena.costantini@example.com",
        "password": "pass1111",
        "full_name": "Elena Costantini",
        "role": "user",
    },
    {
        "email": "matteo.ricci@example.com",
        "password": "pass2222",
        "full_name": "Matteo Ricci",
        "role": "user",
    },
    {
        "email": "serena.pace@example.com",
        "password": "pass3333",
        "full_name": "Serena Pace",
        "role": "user",
    },
    {
        "email": "fabio.fontana@example.com",
        "password": "pass4444",
        "full_name": "Fabio Fontana",
        "role": "user",
    },
    {
        "email": "marta.conti@example.com",
        "password": "pass5555",
        "full_name": "Marta Conti",
        "role": "user",
    },
    {
        "email": "alessandro.gallo@example.com",
        "password": "pass6666",
        "full_name": "Alessandro Gallo",
        "role": "user",
    },
    {
        "email": "valentina.riva@example.com",
        "password": "pass7777",
        "full_name": "Valentina Riva",
        "role": "user",
    },
    {
        "email": "stefano.mazzi@example.com",
        "password": "pass8888",
        "full_name": "Stefano Mazzi",
        "role": "user",
    },
    {
        "email": "giulia.costa@example.com",
        "password": "pass9999",
        "full_name": "Giulia Costa",
        "role": "user",
    },
    {
        "email": "andrea.vitali@example.com",
        "password": "pass0000",
        "full_name": "Andrea Vitali",
        "role": "user",
    },
    {
        "email": "ilaria.greco@example.com",
        "password": "passabcd",
        "full_name": "Ilaria Greco",
        "role": "user",
    },
    {
        "email": "federico.moretti@example.com",
        "password": "passefgh",
        "full_name": "Federico Moretti",
        "role": "user",
    },
]


# Time windows for clustering (15-min intervals)
now = datetime.utcnow()
GROUP_A = (now + timedelta(hours=1)).isoformat()
GROUP_B = (now + timedelta(hours=1, minutes=15)).isoformat()
GROUP_C = (now + timedelta(hours=1, minutes=30)).isoformat()
GROUP_D = (now + timedelta(hours=1, minutes=45)).isoformat()

# NOTE: openrouteservice fails in geocoding Via Torino 12 and 34. Hence, we set onl "Via Torino"
# TODO: user google-maps-api for more accurate geocoding
ORDER_PAYLOAD_FOR_CLUSTERING = {
    "Alice Rossi": {
        "customer_name": "Alice Rossi",
        "customer_phone": "+393491111111",
        "delivery_address": {
            "address": "Piazza Duomo 24",
            "city": "Milan",
            "postal_code": "20121",
        },
        "items": {"food": ["Margherita"], "drink": ["Coca-Cola"]},
        "estimated_prep_time": 20,
        "desired_delivery_time": GROUP_A,
    },
    "Marco Bianchi": {
        "customer_name": "Marco Bianchi",
        "customer_phone": "+393492222222",
        "delivery_address": {
            "address": "Piazza Duomo 26",
            "city": "Milan",
            "postal_code": "20121",
        },
        "items": {"food": ["Diavola"], "drink": ["Fanta"]},
        "estimated_prep_time": 25,
        "desired_delivery_time": GROUP_A,
    },
    "Lucia Verdi": {
        "customer_name": "Lucia Verdi",
        "customer_phone": "+393493333333",
        "delivery_address": {
            "address": "Piazza Duomo 28",
            "city": "Milan",
            "postal_code": "20121",
        },
        "items": {"food": ["Quattro Formaggi"], "drink": ["Sprite"]},
        "estimated_prep_time": 22,
        "desired_delivery_time": GROUP_A,
    },
    "Giovanni Neri": {
        "customer_name": "Giovanni Neri",
        "customer_phone": "+393494444444",
        "delivery_address": {
            "address": "Corso Buenos Aires 33",
            "city": "Milan",
            "postal_code": "20124",
        },
        "items": {"food": ["Capricciosa"], "drink": ["Water"]},
        "estimated_prep_time": 18,
        "desired_delivery_time": GROUP_A,
    },
    "Anna Mancini": {
        "customer_name": "Anna Mancini",
        "customer_phone": "+393495555555",
        "delivery_address": {
            "address": "Corso Buenos Aires 35",
            "city": "Milan",
            "postal_code": "20124",
        },
        "items": {"food": ["Margherita"], "drink": ["Pepsi"]},
        "estimated_prep_time": 20,
        "desired_delivery_time": GROUP_A,
    },
    "Luca Russo": {
        "customer_name": "Luca Russo",
        "customer_phone": "+393496666666",
        "delivery_address": {
            "address": "Corso Buenos Aires 39",
            "city": "Milan",
            "postal_code": "20124",
        },
        "items": {"food": ["Vegetariana"], "drink": ["Coca-Cola"]},
        "estimated_prep_time": 19,
        "desired_delivery_time": GROUP_B,
    },
    "Chiara Ferri": {
        "customer_name": "Chiara Ferri",
        "customer_phone": "+393497777777",
        "delivery_address": {
            "address": "Via Torino",
            "city": "Milan",
            "postal_code": "20123",
        },
        "items": {"food": ["Margherita"], "drink": ["Fanta"]},
        "estimated_prep_time": 21,
        "desired_delivery_time": GROUP_B,
    },
    "Davide Martini": {
        "customer_name": "Davide Martini",
        "customer_phone": "+393498888888",
        "delivery_address": {
            "address": "Via Torino",
            "city": "Milan",
            "postal_code": "20123",
        },
        "items": {"food": ["Diavola"], "drink": ["Beer"]},
        "estimated_prep_time": 23,
        "desired_delivery_time": GROUP_B,
    },
    "Elena Costantini": {
        "customer_name": "Elena Costantini",
        "customer_phone": "+393499999999",
        "delivery_address": {
            "address": "Viale Tunisia 10",
            "city": "Milan",
            "postal_code": "20124",
        },
        "items": {"food": ["Capricciosa"], "drink": ["Lemonade"]},
        "estimated_prep_time": 17,
        "desired_delivery_time": GROUP_B,
    },
    "Matteo Ricci": {
        "customer_name": "Matteo Ricci",
        "customer_phone": "+393400000000",
        "delivery_address": {
            "address": "Via Montenapoleone 5",
            "city": "Milan",
            "postal_code": "20121",
        },
        "items": {"food": ["Quattro Stagioni"], "drink": ["Water"]},
        "estimated_prep_time": 16,
        "desired_delivery_time": GROUP_B,
    },
    "Serena Pace": {
        "customer_name": "Serena Pace",
        "customer_phone": "+393401111111",
        "delivery_address": {
            "address": "Via Solari 12",
            "city": "Milan",
            "postal_code": "20144",
        },
        "items": {"food": ["Margherita"], "drink": ["Coca-Cola"]},
        "estimated_prep_time": 20,
        "desired_delivery_time": GROUP_C,
    },
    "Fabio Fontana": {
        "customer_name": "Fabio Fontana",
        "customer_phone": "+393402222222",
        "delivery_address": {
            "address": "Via Vigevano 18",
            "city": "Milan",
            "postal_code": "20144",
        },
        "items": {"food": ["Diavola"], "drink": ["Pepsi"]},
        "estimated_prep_time": 19,
        "desired_delivery_time": GROUP_C,
    },
    "Marta Conti": {
        "customer_name": "Marta Conti",
        "customer_phone": "+393403333333",
        "delivery_address": {
            "address": "Via Bergognone",
            "city": "Milan",
            "postal_code": "20144",
        },
        "items": {"food": ["Bufala"], "drink": ["Fanta"]},
        "estimated_prep_time": 21,
        "desired_delivery_time": GROUP_C,
    },
    "Alessandro Gallo": {
        "customer_name": "Alessandro Gallo",
        "customer_phone": "+393404444444",
        "delivery_address": {
            "address": "Via Tortona 30",
            "city": "Milan",
            "postal_code": "20144",
        },
        "items": {"food": ["Tonno e Cipolla"], "drink": ["Water"]},
        "estimated_prep_time": 18,
        "desired_delivery_time": GROUP_C,
    },
    "Valentina Riva": {
        "customer_name": "Valentina Riva",
        "customer_phone": "+393405555555",
        "delivery_address": {
            "address": "Viale Coni Zugna 3",
            "city": "Milan",
            "postal_code": "20144",
        },
        "items": {"food": ["Margherita"], "drink": ["Sprite"]},
        "estimated_prep_time": 20,
        "desired_delivery_time": GROUP_C,
    },
    "Stefano Mazzi": {
        "customer_name": "Stefano Mazzi",
        "customer_phone": "+393406666666",
        "delivery_address": {
            "address": "Via Washington 15",
            "city": "Milan",
            "postal_code": "20146",
        },
        "items": {"food": ["Diavola"], "drink": ["Lemonade"]},
        "estimated_prep_time": 22,
        "desired_delivery_time": GROUP_D,
    },
    "Giulia Costa": {
        "customer_name": "Giulia Costa",
        "customer_phone": "+393407777777",
        "delivery_address": {
            "address": "Via Foppa 16",
            "city": "Milan",
            "postal_code": "20144",
        },
        "items": {"food": ["Vegetariana"], "drink": ["Beer"]},
        "estimated_prep_time": 24,
        "desired_delivery_time": GROUP_D,
    },
    "Andrea Vitali": {
        "customer_name": "Andrea Vitali",
        "customer_phone": "+393408888888",
        "delivery_address": {
            "address": "Via Carlo Ravizza 8",
            "city": "Milan",
            "postal_code": "20149",
        },
        "items": {"food": ["Bufala"], "drink": ["Water"]},
        "estimated_prep_time": 19,
        "desired_delivery_time": GROUP_D,
    },
    "Ilaria Greco": {
        "customer_name": "Ilaria Greco",
        "customer_phone": "+393409999999",
        "delivery_address": {
            "address": "Via Marghera 12",
            "city": "Milan",
            "postal_code": "20149",
        },
        "items": {"food": ["Capricciosa"], "drink": ["Fanta"]},
        "estimated_prep_time": 20,
        "desired_delivery_time": GROUP_D,
    },
    "Federico Moretti": {
        "customer_name": "Federico Moretti",
        "customer_phone": "+393410000000",
        "delivery_address": {
            "address": "Via Raffaello Sanzio 4",
            "city": "Milan",
            "postal_code": "20149",
        },
        "items": {"food": ["Margherita"], "drink": ["Pepsi"]},
        "estimated_prep_time": 21,
        "desired_delivery_time": GROUP_D,
    },
}

GEO_CLUSTERS = {
    0: ["Piazza Duomo 24", "Piazza Duomo 26", "Piazza Duomo 28"],
    1: [
        "Corso Buenos Aires 33",
        "Corso Buenos Aires 35",
        "Corso Buenos Aires 39",
        "Viale Tunisia 10",
    ],
    2: ["Via Torino", "Via Torino"],
    3: ["Via Montenapoleone 5"],
    4: ["Via Solari 12", "Viale Coni Zugna 3", "Via Foppa 16"],
    5: ["Via Vigevano 18"],
    6: ["Via Bergognone"],
    7: ["Via Tortona 30"],
    8: [
        "Via Washington 15",
        "Via Carlo Ravizza 8",
        "Via Marghera 12",
        "Via Raffaello Sanzio 4",
    ],
}

# Test Drivers
TEST_USER_DRIVERS = [
    {
        "email": "driver1@example.com",
        "password": "password123",
        "full_name": "Test Driver One",
        "role": "driver",
    },
    {
        "email": "driver2@example.com",
        "password": "password123",
        "full_name": "Test Driver Two",
        "role": "driver",
    },
    {
        "email": "driver3@example.com",
        "password": "password123",
        "full_name": "Test Driver Three",
        "role": "driver",
    },
    {
        "email": "driver4@example.com",
        "password": "password123",
        "full_name": "Test Driver Four",
        "role": "driver",
    },
    {
        "email": "driver5@example.com",
        "password": "password123",
        "full_name": "Test Driver Five",
        "role": "driver",
    },
    {
        "email": "driver6@example.com",
        "password": "password123",
        "full_name": "Test Driver Six",
        "role": "driver",
    },
    {
        "email": "driver7@example.com",
        "password": "password123",
        "full_name": "Test Driver Seven",
        "role": "driver",
    },
    {
        "email": "driver8@example.com",
        "password": "password123",
        "full_name": "Test Driver Eight",
        "role": "driver",
    },
    {
        "email": "driver9@example.com",
        "password": "password123",
        "full_name": "Test Driver Nine",
        "role": "driver",
    },
    {
        "email": "driver10@example.com",
        "password": "password123",
        "full_name": "Test Driver Ten",
        "role": "driver",
    },
]
NUMBER_UPDATE_DRIVERS = 5
