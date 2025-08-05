from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Enum,
    Float,
    Boolean,
)
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
    postal_code = Column(String, nullable=False)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False, default="Italy")

    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    desired_delivery_time = Column(DateTime, nullable=False)
    items = Column(String)  # JSON string or comma-separated
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)
    estimated_prep_time = Column(Float, default=0.0)  # minutes
    priority = Column(Boolean, nullable=False, default=False)

    creator = relationship("User", backref="orders")
