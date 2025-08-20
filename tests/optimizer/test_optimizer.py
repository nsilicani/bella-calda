from app.schemas.cluster import ClusterRoute, OrderCluster

import pytest

from datetime import datetime


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


def test_estimate_latest_pizza_ready_time(
    orders_optimizer, latest_pizza_ready_time_confs
):
    now = datetime.utcnow()
    latest_prep_time = orders_optimizer.estimate_latest_pizza_ready_time(
        total_pizzas=latest_pizza_ready_time_confs["total_pizzas"],
        chefs=latest_pizza_ready_time_confs["chefs"],
        chef_experience=latest_pizza_ready_time_confs["chef_experience"],
        chef_capacity=latest_pizza_ready_time_confs["chef_capacity"],
        bake_times=latest_pizza_ready_time_confs["bake_times"],
        num_ovens=latest_pizza_ready_time_confs["num_ovens"],
        single_oven_capacity=latest_pizza_ready_time_confs["single_oven_capacity"],
        pizza_type=latest_pizza_ready_time_confs["pizza_type"],
        now=datetime.utcnow(),
    )
    assert (latest_prep_time - now).seconds / 60 == latest_pizza_ready_time_confs[
        "estimate_latest_pizza_ready_time"
    ]  # 8 minutes to prepare 24 pizzas
