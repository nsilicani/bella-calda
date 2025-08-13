from app.models.driver import DriverStatus
from app.schemas.driver import DriverUpdate
from app.schemas.order import OrderResponse
from scripts.constants import (
    ORDER_PAYLOAD,
    GEO_CLUSTERS,
    TEST_USER_DRIVERS,
    NUMBER_UPDATE_DRIVERS,
    LOGIN_ENDPOINT,
    ORDERS_ENDPOINT,
    GET_AVAILABLE_ORDERS_ENDPOINT,
    ORDERS_OPTIMIZER_ENDPOINT,
    CLUSTER_ENDPOINT,
    CLUSTER_BY_TIME_ENDPOINT,
    DRIVERS_ENDPOINT,
    DRIVER_UPDATE_ENDPOINT,
    DRIVER_GET_AVAILABLE_ENDPOINT,
)


def test_routes_create_order(client, create_users, user_credentials):
    # Assert unauthorized
    unauthorized_response_login = client.post(
        url=LOGIN_ENDPOINT,
        data={
            "username": "user_not_in_db",
            "password": "wrong_password",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert unauthorized_response_login.status_code == 401

    # Assert authorized and store access token
    response_login = client.post(
        url=LOGIN_ENDPOINT,
        data={
            "username": user_credentials["email"],
            "password": user_credentials["password"],
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response_login.status_code == 200
    token = response_login.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response_orders = client.post(
        url=ORDERS_ENDPOINT, json=ORDER_PAYLOAD, headers=headers
    )
    assert response_orders.status_code == 201


def test_routes_order_get_available_orders(client, create_users, create_orders):
    # Test three parameters
    url = (
        GET_AVAILABLE_ORDERS_ENDPOINT
        + "?start_time={start_time}&radius_km={radius_km}&lat={lat}&lon={lon}"
    )
    start_time = "2025-08-05T10:00:00"
    radius_km = 2
    lon = 8.81
    lat = 45.48
    url = url.format(start_time=start_time, radius_km=radius_km, lat=lat, lon=lon)
    response_get_avail_orders = client.get(url=url)
    assert response_get_avail_orders.status_code == 200
    data = response_get_avail_orders.json()
    assert len(data) == 3

    # Test only geographic parameters
    url = GET_AVAILABLE_ORDERS_ENDPOINT + "?radius_km={radius_km}&lat={lat}&lon={lon}"
    radius_km = 2
    lon = 8.81
    lat = 45.48
    url = url.format(radius_km=radius_km, lat=lat, lon=lon)
    response_get_avail_orders = client.get(url=url)
    assert response_get_avail_orders.status_code == 200
    data = response_get_avail_orders.json()
    assert len(data) == 3


def test_routes_clusters_by_time(
    client, create_users_for_clustering, create_orders_for_clustering
):
    response_clusters = client.get(url=CLUSTER_BY_TIME_ENDPOINT)
    assert response_clusters.status_code == 200
    data = response_clusters.json()
    assert len(data) == 4
    for clustered_orders in data.values():
        for ord in clustered_orders:
            # We check order matching (we don't compare datetime fields, they have different datatype due to serialization):
            ord_out = OrderResponse(**ord).model_dump()
            keys_to_check = ["id", "creator_id", "delivery_address", "items"]
            assert all([ord[k] == ord_out[k] for k in keys_to_check])


def test_routes_clusters_by_geo(
    client, create_users_for_clustering, create_orders_for_clustering
):
    response_clusters = client.get(url=CLUSTER_ENDPOINT)
    assert response_clusters.status_code == 200
    data = response_clusters.json()
    assert len(data) == len(GEO_CLUSTERS)
    for idx, cluster in enumerate(data):
        for order_out, order_in in zip(cluster, GEO_CLUSTERS[idx]):
            assert order_out["delivery_address"]["address"] == order_in


def test_routes_order_optimizer(client, create_users, create_orders):
    response_optimze = client.post(url=ORDERS_OPTIMIZER_ENDPOINT)
    assert response_optimze.status_code == 200


def test_routes_list_driver(client, create_user_drivers):
    response_list_drivers = client.get(url=DRIVERS_ENDPOINT)
    assert response_list_drivers.status_code == 200
    data = response_list_drivers.json()
    assert len(data) == len(TEST_USER_DRIVERS)


def test_routes_update_driver(client, create_user_drivers):
    LAT = 45.46
    LON = 9.18
    driver_update = DriverUpdate(
        is_active=True,
        status=DriverStatus.DELIVERING,
        lat=LAT,
        lon=LON,
        current_route=None,
        estimated_finish_time=None,
    )
    # Fetch the first driver and store the driver ID
    response_list_drivers = client.get(url=DRIVERS_ENDPOINT)
    data = response_list_drivers.json()
    first_driver = data[0]
    first_driver_id = first_driver["id"]

    # Update LAT and LON of the first driver with driver ID
    response_update_driver = client.patch(
        url=DRIVER_UPDATE_ENDPOINT.format(driver_id=first_driver_id),
        json=driver_update.model_dump(),
    )
    assert response_update_driver.status_code == 200

    # Check update
    response_list_drivers = client.get(url=DRIVERS_ENDPOINT)
    data = response_list_drivers.json()
    first_driver = data[0]
    assert first_driver["lat"] == LAT
    assert first_driver["lon"] == LON


def test_routes_get_available_drivers(client, create_user_drivers, update_user_drivers):
    response_get_available_drivers = client.get(
        url=DRIVER_GET_AVAILABLE_ENDPOINT,
    )
    assert response_get_available_drivers.status_code == 200
    assert len(response_get_available_drivers.json()) == NUMBER_UPDATE_DRIVERS
