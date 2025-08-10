from typing import Dict, List, Optional
from typing_extensions import Annotated
from datetime import datetime
from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import config
from app.models.user import User
from app.models.order import Order
from app.schemas import OrderCreate, OrderResponse, OrderOut
from app.database import create_new_db_session
from app.auth.dependencies import get_current_user
from app.config_logging import logger
from app.services.orders import OrdersOptimizer
from app.services.route_planner.base import RoutePlannerService
from app.services.route_planner.factory import get_route_planner

router = APIRouter(prefix="/orders", tags=["Orders"])


@lru_cache
def get_settings():
    return config.Settings()


@lru_cache
def get_optimizer(db: Session = Depends(create_new_db_session)):
    return OrdersOptimizer(db=db, logger=logger)


# See https://fastapi.tiangolo.com/tutorial/response-model/#add-an-output-model
@router.post("/order/", response_model=OrderResponse, status_code=201)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(create_new_db_session),
    current_user: User = Depends(get_current_user),
    route_planner: RoutePlannerService = Depends(get_route_planner),
):
    # Geocode order address (fetching lat, lon) to fill model's fields
    # Return lon and lat
    lon, lat = route_planner.get_coordinates(
        address=order_data.delivery_address.address,
        postal_code=order_data.delivery_address.postal_code,
        city=order_data.delivery_address.city,
        country=order_data.delivery_address.country,
    )
    new_order = Order(
        creator_id=current_user.id,
        customer_name=order_data.customer_name,
        customer_phone=order_data.customer_phone,
        delivery_address=order_data.delivery_address.address,
        postal_code=order_data.delivery_address.postal_code,
        city=order_data.delivery_address.city,
        country=order_data.delivery_address.country,
        lat=lat,
        lon=lon,
        items=order_data.items,
        # NOTE: estimated_prep_time can be removed
        estimated_prep_time=order_data.estimated_prep_time,
        desired_delivery_time=order_data.desired_delivery_time,
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order


@router.post("/optimize", status_code=200)
def optimize_orders(optimizer: OrdersOptimizer = Depends(get_optimizer)):
    try:
        optimizer.run()
        return {"detail": "Order optimization completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clusters_by_time", response_model=Dict[datetime, List[OrderResponse]])
async def get_clustered_orders_by_time(
    settings: Annotated[config.Settings, Depends(get_settings)],
    optimizer: OrdersOptimizer = Depends(get_optimizer),
):
    ready_orders = optimizer.fetch_unassigned_orders()
    filtered = optimizer.filter_out_unavailable_orders(ready_orders)
    time_buckets = await optimizer.cluster_orders_by_time_window(
        orders=filtered,
        time_window_minutes=settings.CLUSTER_TIME_WINDOW_MINUTES,
    )
    return time_buckets


@router.get("/clusters", response_model=List[List[OrderResponse]])
async def get_clustered_orders_by_geo(
    settings: Annotated[config.Settings, Depends(get_settings)],
    optimizer: OrdersOptimizer = Depends(get_optimizer),
    route_planner: RoutePlannerService = Depends(get_route_planner),
):
    ready_orders = optimizer.fetch_unassigned_orders()
    filtered = optimizer.filter_out_unavailable_orders(ready_orders)
    logger.info(f"{filtered=}")
    clusters = await optimizer.cluster_orders_by_geographic_proximity(
        route_planner=route_planner,
        orders=filtered,
        max_pizzas_per_cluster=settings.MAX_PIZZAS_PER_CLUSTER,
    )
    return [[order for order in cluster] for cluster in clusters]


@router.get("/available_orders", response_model=List[OrderOut])
def get_available_orders(
    optimizer: OrdersOptimizer = Depends(get_optimizer),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
    radius_km: Optional[float] = Query(None),
):
    """
    Return a list of orders that are pending and ready to be assigned.
    Optional filters:
    - Time window (start_time to end_time)
    - Location radius (lat, lon, radius_km)
    """
    try:
        ready_orders = optimizer.fetch_unassigned_orders()
        filtered_orders = optimizer.filter_out_unavailable_orders(
            ready_orders,
            start_time=start_time,
            end_time=end_time,
            lat=lat,
            lon=lon,
            radius_km=radius_km,
        )
        return filtered_orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
