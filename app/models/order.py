from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum


class OrderStatus(str, enum.Enum):
    pending = "pending"
    preparing = "preparing"
    assigned = "assigned"
    delivering = "delivering"
    delivered = "delivered"
    cancelled = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    customer_name = Column(String, nullable=True)
    customer_phone = Column(String, nullable=True)
    delivery_address = Column(String, nullable=False)
    desired_delivery_time = Column(DateTime, nullable=False)
    items = Column(String)  # JSON string or comma-separated
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)
    estimated_prep_time = Column(Float, default=0.0)  # minutes

    creator = relationship("User", backref="orders")
