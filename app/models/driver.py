from sqlalchemy import Column, Integer, String, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    is_active = Column(Boolean, default=True)
    current_location = Column(String, nullable=True)  # could be lat,lng
    current_route = Column(JSON, nullable=True)  # list of order IDs or stops

    user = relationship("User", backref="driver_profile")
