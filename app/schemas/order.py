from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class OrderStatus(str, Enum):
    pending = "pending"
    preparing = "preparing"
    assigned = "assigned"
    delivering = "delivering"
    delivered = "delivered"
    cancelled = "cancelled"


class OrderCreate(BaseModel):
    customer_name: Optional[str]
    customer_phone: Optional[str]
    delivery_address: str
    items: str
    estimated_prep_time: float
    desired_delivery_time: datetime


class OrderResponse(BaseModel):
    id: int
    creator_id: int
    customer_name: Optional[str]
    customer_phone: Optional[str]
    delivery_address: str
    items: str
    status: OrderStatus
    created_at: datetime
    estimated_prep_time: float
    desired_delivery_time: datetime

    class Config:
        orm_mode = True
