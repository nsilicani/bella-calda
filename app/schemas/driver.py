from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from datetime import datetime
from enum import Enum


class DriverStatus(str, Enum):
    AVAILABLE = "available"
    DELIVERING = "delivering"
    OFFLINE = "offline"


class DriverBase(BaseModel):
    user_id: int
    full_name: str
    is_active: bool = True
    status: DriverStatus = DriverStatus.AVAILABLE
    lat: Optional[float] = None
    lon: Optional[float] = None
    current_route: Optional[Any] = None  # Could make this List[int] if only IDs
    estimated_finish_time: Optional[datetime] = None


class DriverCreate(DriverBase):
    pass


class DriverUpdate(BaseModel):
    is_active: Optional[bool] = None
    status: Optional[DriverStatus] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    current_route: Optional[Any] = None
    estimated_finish_time: Optional[datetime] = None


class DriverOut(DriverBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
