from pydantic import BaseModel, Field, constr
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


class DeliveryAddress(BaseModel):
    address: constr(strip_whitespace=True, min_length=5) = Field(
        ..., example="123 Pizza Street"
    )
    postal_code: constr(strip_whitespace=True, min_length=4, max_length=10) = Field(
        ..., example="20100"
    )
    city: str = Field(example="Milan")
    country: str = Field(default="Italy", example="Italy")

    def to_string(self) -> str:
        return f"{self.address}, {self.postal_code}, {self.city}, {self.country}"


class OrderCreate(BaseModel):
    customer_name: Optional[str]
    customer_phone: Optional[str]
    delivery_address: DeliveryAddress
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
    priority: bool = False

    class Config:
        orm_mode = True


class OrderOut(BaseModel):
    id: int
    customer_name: str
    delivery_address: str
    status: str
    created_at: datetime

    class Config:
        orm_mode = True
