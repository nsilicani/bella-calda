from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.user import User
from app.schemas.order import OrderCreate


def create_order(
    *, db: Session, current_user: User, order_data: OrderCreate, lon: float, lat: float
) -> Order:
    new_order = Order(
        creator_id=current_user.id,
        customer_name=order_data.customer_name,
        customer_phone=order_data.customer_phone,
        lat=lat,
        lon=lon,
        delivery_address=order_data.delivery_address.model_dump(),
        items=order_data.items.model_dump(),
        estimated_prep_time=order_data.estimated_prep_time,
        desired_delivery_time=order_data.desired_delivery_time,
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order
