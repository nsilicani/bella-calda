import pytest
import logging

from datetime import datetime

from app.config import ClusteringSettings
from app.models.order import Order
from app.services.orders.orders_optimizer import OrdersOptimizer
from app.services.route_planner.factory import get_route_planner


@pytest.fixture(name="logger")
def test_logger():
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)
    # Add a handler that captures logs during tests
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    return logger


@pytest.fixture(name="locations")
def locations_fixture():
    locations = [
        (45.463765, 9.188569),  # Pizzeria start
        (45.479426, 9.210024),
        (45.479442, 9.21004),
        (45.479812, 9.210421),
        (45.477287, 9.205439),
        (45.473702, 9.170685),
        (45.455633, 9.164073),
        (45.453036, 9.173099),
    ]
    locations = [(lon, lat) for lat, lon in locations]
    return locations


@pytest.fixture(name="orders")
def orders_fixture(locations):
    orders = []
    for idx, loc in enumerate(locations[1:]):
        new_order = Order(
            id=idx,
            creator_id=idx,
            customer_name=f"Customer_{idx}",
            customer_phone=f"Customer_phone_{idx}",
            lat=loc[1],
            lon=loc[0],
            delivery_address={
                "address": f"Address_{idx}",
                "postal_code": "20100",
                "city": "Milan",
                "country": "Italy",
            },
            items={"food": ["Margherita"], "drink": []},
            estimated_prep_time=20.0,
            desired_delivery_time=datetime.utcnow(),
            status="pending",
            created_at=datetime.utcnow(),
            priority=False,
        )
        orders.append(new_order)
    return orders


@pytest.fixture(name="orders_optimizer")
def optimizer_fixure(session, locations, logger):
    clustering_settings = ClusteringSettings(
        MAX_PIZZAS_PER_CLUSTER=10,
        CLUSTER_TIME_WINDOW_MINUTES=15,
        CLUSTER_DISTANCE_THRESHOLD=120,
        START_LOCATION_LON=locations[0][0],
        START_LOCATION_LAT=locations[0][1],
        ADDRESS="Test address 123",
        POSTAL_CODE="123456",
        CITY="Milan",
        COUNTRY="Italy",
    )
    orders_optimizer = OrdersOptimizer(
        db=session,
        logger=logger,
        route_planner=get_route_planner(),
        clustering_settings=clustering_settings,
    )
    return orders_optimizer
