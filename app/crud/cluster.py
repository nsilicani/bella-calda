from sqlalchemy.orm import Session

from app.models.cluster import OrderCluster as order_cluster_model
from app.models.order import Order
from app.schemas.cluster import OrderCluster


def create_cluster(*, db: Session, order_cluster: OrderCluster) -> None:
    new_cluster = order_cluster_model(
        id=order_cluster.id,
        time_window=order_cluster.time_window,
        total_items=order_cluster.total_items,
        earliest_delivery_time=order_cluster.earliest_delivery_time,
        cluster_route=order_cluster.cluster_route.model_dump(),
    )
    for idx in order_cluster.get_order_ids:
        order_obj = db.query(Order).get(idx)
        new_cluster.orders.append(order_obj)
    db.add(new_cluster)
    db.commit()
    db.refresh(new_cluster)
    return new_cluster
