from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.order import Order
from app.schemas import OrderCreate, OrderResponse, OrderOut
from app.database import create_new_db_session
from app.auth.dependencies import get_current_user  # You should define this
from app.services.orders import OrdersOptimizer
from app.services.route_planner.base import RoutePlannerService
from app.services.route_planner.factory import get_route_planner

router = APIRouter(prefix="/orders", tags=["Orders"])


# See https://fastapi.tiangolo.com/tutorial/response-model/#add-an-output-model
@router.post("/order/", response_model=OrderResponse, status_code=201)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(create_new_db_session),
    current_user: User = Depends(get_current_user),
    route_planner: RoutePlannerService = Depends(get_route_planner),
):
    # Geocode order address (fetching lat, lon) to fill model's fields
    lat, lon = route_planner.get_coordinates(
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
        estimated_prep_time=order_data.estimated_prep_time,
        desired_delivery_time=order_data.desired_delivery_time,
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order


@router.post("/optimize", status_code=200)
def optimize_orders(db: Session = Depends(create_new_db_session)):
    try:
        optimizer = OrdersOptimizer(db)
        optimizer.run()
        return {"detail": "Order optimization completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/available_orders", response_model=List[OrderOut])
def get_available_orders(
    db: Session = Depends(create_new_db_session),
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
        optimizer = OrdersOptimizer(db)
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
