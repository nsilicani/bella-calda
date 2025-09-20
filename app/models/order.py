from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Enum,
    Float,
    Boolean,
    JSON,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from app.models.cluster import order_cluster_association
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

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    customer_name = Column(String, nullable=True)
    customer_phone = Column(String, nullable=True)
    delivery_address = Column(JSON, nullable=False)  # dict from DeliveryAddress
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    desired_delivery_time = Column(DateTime, nullable=False)
    items = Column(JSON, nullable=False)  # dict from OrderItems
    status = Column(Enum(OrderStatus), default=OrderStatus.pending, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    estimated_prep_time = Column(Float, default=0.0)  # minutes
    priority = Column(Boolean, nullable=False, default=False)

    creator = relationship("User", backref="orders")

    # Many-to-many relationship
    clusters = relationship(
        "OrderCluster",
        secondary="order_cluster_association",
        back_populates="orders",
    )
