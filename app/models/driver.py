from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    JSON,
    ForeignKey,
    Float,
    DateTime,
    Enum,
    String,
)
from sqlalchemy.orm import relationship
from app.database import Base
import enum
from datetime import datetime


class DriverStatus(str, enum.Enum):
    AVAILABLE = "available"
    DELIVERING = "delivering"
    OFFLINE = "offline"


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    full_name = Column(String, nullable=False)

    is_active = Column(Boolean, default=True)

    status = Column(Enum(DriverStatus), default=DriverStatus.AVAILABLE, nullable=False)

    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)

    # JSON could store planned stops, order IDs, or route details
    current_route = Column(JSON, nullable=True)

    estimated_finish_time = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", backref="driver_profile")
