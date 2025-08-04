# 🍕 Bella Calda la Pizza Backend API

This is a backend service for an **on-demand pizza delivery platform**, built with **FastAPI**. The system supports user and staff registrations, secure login, order management, and route optimization for delivery dispatching.

---

## Features

- **Authentication** with JWT (signup & login)
- **Order creation and tracking**
- **Staff order entry** (e.g. phone-in orders)
- **Superuser control** (view/update all orders)
- **Route optimization** for delivery drivers (planned feature)
- **Dockerized PostgreSQL** database

---

## Setup Instructions

### Requirements

- Python 3.10+
- Docker (for DB setup)

### Install Dependencies
Dependencies can be installed via `uv`:
```bash
uv venv
source .venv/bin/activate # or .\venv\Scripts\activate on Windows

uv pip install .
```
or
```bash
uv pip install .
```
This will read the `pyproject.toml`, resolve dependencies, and install them efficiently.

Dependencies can be installed without `uv`:

```bash
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

pip install -r requirements.txt
```
---

### Set up envs
Create a `.env` file in project's root:
```env
OPENROUTESERVIE_API_KEY=<Your OpenRouteService API KEY>

DATABASE_URL=postgresql://postgres:postgres@localhost:5432/pizza_db

APP_CONFIGS__API_V1_STR=/api/v1
APP_CONFIGS__PROJECT_NAME=bella-calda-la-pizza
```

## Setup PostgreSQL with Docker

> If you don't have Docker installed, install it from https://www.docker.com/products/docker-desktop

### Create a containerized DB:

```bash
docker-compose up -d
```

This will expose your PostgreSQL DB at:
```
postgresql://postgres:postgres@localhost:5432/pizza
```

---

## Create Tables

Database tables are created during app start up (see [lifespan](https://fastapi.tiangolo.com/advanced/events/#lifespan))
Create the first user:
```bash
python app/scripts/create_user.py
```

---

## Authentication

### Signup

**POST** `/auth/signup/`  
Registers a new user.

```json
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "role": "user"
}
```

### Login

**POST** `/auth/login/`  
Returns a JWT token for use in protected endpoints.

```x-www-form-urlencoded
username: user@example.com
password: password123
```

Returns:

```json
{
  "access_token": "<jwt-token>",
  "token_type": "bearer"
}
```

Use it in `Authorization` headers:

```
Authorization: Bearer <token>
```

---

## Order Management Endpoints (WIP)

| METHOD | ROUTE | FUNCTIONALITY | ACCESS |
|--------|-------|---------------|--------|
| POST   | `/orders/order/` | Place an order | All users |
| PUT    | `/orders/order/update/{order_id}/` | Update an order | Creator/staff |
| PUT    | `/orders/order/status/{order_id}/` | Update order status | Admin |
| DELETE | `/orders/order/delete/{order_id}/` | Delete an order | Creator/staff |
| GET    | `/orders/user/orders/` | Get user’s own orders | Auth users |
| GET    | `/orders/orders/` | List all orders | Admin |
| GET    | `/orders/orders/{order_id}/` | Retrieve any order | Admin |
| GET    | `/orders/user/order/{order_id}/` | Get user’s specific order | Auth users |
| POST   | `/optimize/` | Route optimization (planned) | Admin |

---

## Testing the API

You can use [Postman](https://www.postman.com/) or `httpx`, `curl`, or Python scripts with `requests`.

Example:

```python
import requests

BASE_URL = "http://127.0.0.1:8000"

# Signup
resp = requests.post(f"{BASE_URL}/auth/signup/", json={
    "email": "user@example.com",
    "password": "securepass",
    "full_name": "Pizza Lover",
    "role": "user"
})
print(resp.json())
```

### Unit Tests
Use pytest to run unit tests. In conftest.py, we create a session object that will be used during testing, along with its own engine, and this new engine will use a new URL for the testing database. For more details, see [Create the Engine and Session for Testing](https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/#create-the-engine-and-session-for-testing).
```bash
pytest -vv
```

---

## Docs

Once server is running, visit:

- **Docs UI**: [`http://localhost:8000/docs`](http://localhost:8000/docs)
- **Redoc UI**: [`http://localhost:8000/redoc`](http://localhost:8000/redoc)

---

## Run the App

```bash
uvicorn app.main:app --reload
```
or (dev):
```bash
fastapi dev app/main.py
```
or (prodution mode):
```bash
fastapi run app/main.py
```

---

## Roles

- **User** – standard customer
- **Staff** – can place/edit orders manually (e.g. phone-in)
- **Admin** – can view/update all orders and statuses

---

## TODO

- [ ] Route optimization logic
- [ ] Assign best driver to order
- [ ] Role-based route protection
- [ ] Consider to switch to `SQLModel`, which is built on top of SQLAlchemy and Pydantic


## Resources
- [Route Optimization API](https://developers.google.com/maps/documentation/route-optimization/overview)
- [Route Optimization API - Request](https://developers.google.com/maps/documentation/route-optimization/construct-request)
- [Route Optimization API - Billing](https://developers.google.com/maps/documentation/route-optimization/usage-and-billing)
- [Route Optimization API - Python Client](https://github.com/googleapis/google-cloud-python/tree/main/packages/google-maps-routeoptimization)
- https://github.com/fastapi/full-stack-fastapi-template/blob/master/backend/app/initial_data.py
- https://tecadmin.net/installing-docker-on-windows/
- https://docs.docker.com/desktop/setup/install/windows-install/
- https://blog.ni18.in/the-operation-could-not-be-started-because-a-required-feature-is-not-installed/
- https://github.com/jod35/Pizza-Delivery-API/blob/main/README.md