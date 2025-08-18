from app.schemas.cluster import ClusterRoute, OrderCluster

import pytest


def test_compute_cluster_route(locations, orders, orders_optimizer):
    cluster_route = orders_optimizer.compute_cluster_route(
        orders=orders, start_location=locations[0]
    )
    assert isinstance(cluster_route, ClusterRoute)


@pytest.mark.asyncio
async def test_compute_clustered_orders(orders, orders_optimizer):
    clustered_orders = await orders_optimizer.compute_clustered_orders(
        filtered_orders=orders
    )
    assert all([isinstance(order, OrderCluster) for order in clustered_orders])
