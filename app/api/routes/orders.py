from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.order import Order
from app.schemas import OrderCreate, OrderResponse
from app.database import create_new_db_session
from app.auth.dependencies import get_current_user  # You should define this

router = APIRouter(prefix="/orders", tags=["Orders"])


# See https://fastapi.tiangolo.com/tutorial/response-model/#add-an-output-model
@router.post("/order/", response_model=OrderResponse, status_code=201)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(create_new_db_session),
    current_user: User = Depends(get_current_user),
):
    new_order = Order(
        creator_id=current_user.id,
        customer_name=order_data.customer_name,
        customer_phone=order_data.customer_phone,
        delivery_address=order_data.delivery_address,
        items=order_data.items,
        estimated_prep_time=order_data.estimated_prep_time,
        desired_delivery_time=order_data.desired_delivery_time,
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order
