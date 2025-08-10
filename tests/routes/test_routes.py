from app.schemas.order import OrderResponse
from scripts.constants import ORDER_PAYLOAD, GEO_CLUSTERS


def test_routes_create_order(client, create_users, base_url, user_credentials):
    ENDPOINT_LOGIN = f"{base_url}/api/v1/auth/login"

    # Assert unauthorized
    unauthorized_response_login = client.post(
        url=ENDPOINT_LOGIN,
        data={
            "username": "user_not_in_db",
            "password": "wrong_password",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert unauthorized_response_login.status_code == 401

    # Assert authorized and store access token
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
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response_orders = client.post(
        url=ORDERS_ENDPOINT, json=ORDER_PAYLOAD, headers=headers
    )
    assert response_orders.status_code == 201


def test_routes_order_get_available_orders(
    client, base_url, create_users, create_orders
):
    GET_AVAILABLE_ORDERS_ENDPOINT = f"{base_url}/api/v1/orders/available_orders"
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
    client, base_url, create_users_for_clustering, create_orders_for_clustering
):
    CLUSTER_BY_TIME_ENDPOINT = f"{base_url}/api/v1/orders/clusters_by_time"
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
    client, base_url, create_users_for_clustering, create_orders_for_clustering
):
    CLUSTER_ENDPOINT = f"{base_url}/api/v1/orders/clusters"
    response_clusters = client.get(url=CLUSTER_ENDPOINT)
    assert response_clusters.status_code == 200
    data = response_clusters.json()
    assert len(data) == len(GEO_CLUSTERS)
    for idx, cluster in enumerate(data):
        for order_out, order_in in zip(cluster, GEO_CLUSTERS[idx]):
            assert order_out["delivery_address"] == order_in


def test_routes_order_optimizer(client, base_url, create_users, create_orders):
    ORDERS_OPTIMIZER_ENDPOINT = f"{base_url}/api/v1/orders/optimize/"
    response_optimze = client.post(url=ORDERS_OPTIMIZER_ENDPOINT)
    assert response_optimze.status_code == 200
