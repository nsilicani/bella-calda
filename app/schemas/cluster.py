from typing import List, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel, Field
import secrets
import enum

from app.schemas.order import DeliveryAddress, OrderResponse


class DeliveryStep(BaseModel):
    """
    A segment is the connection between two given coordinates.
    See: https://openrouteservice-py.readthedocs.io/en/latest/#module-openrouteservice.directions
    """

    name: str
    type: int
    distance: float
    duration: float
    duration_from_start: float
    instruction: str
    way_points: List[int]


class RouteSegment(BaseModel):
    distance: float
    duration: float
    steps: List[DeliveryStep]
    segment_start: DeliveryAddress
    segment_end: DeliveryAddress
    duration_from_start: float
    delivery_address: DeliveryAddress


class ClusterRoute(BaseModel):
    id: str = Field(default_factory=lambda: secrets.token_hex(2))
    distance: float = Field(..., description="Total traveled distance in meters")
    duration: float = Field(..., description="Total travel time in seconds")
    segments: List[RouteSegment]

class ClusterStatus(str, enum.Enum):
    to_be_assigned = "to_be_assigned"
    assigned = "assigned"
    delivered = "delivered"
    cancelled = "cancelled"

class OrderCluster(BaseModel):
    id: str = Field(default_factory=lambda: secrets.token_hex(2))
    time_window: datetime = Field(
        ..., description="Time window used to aggregate orders in clusters by time"
    )
    orders: List[OrderResponse]
    total_items: int = Field(..., description="Total number of pizzas in the cluster")
    earliest_delivery_time: datetime = Field(
        ..., description="Earliest delivery time among orders"
    )
    cluster_route: ClusterRoute = Field(..., description="cluster route specifications")
    cluster_status: ClusterStatus

    @property
    def customer_locations(self) -> List[Tuple[float, float]]:
        """
        Extract (lat, lon) for each order.
        """
        return [(order.lat, order.lon) for order in self.orders]

    @property
    def get_order_ids(self) -> List[int]:
        return [order.id for order in self.orders]

class OrderClusterUpdate(BaseModel):
    id: str
    time_window: Optional[datetime] = None
    orders: Optional[List[OrderResponse]] = None
    total_items: Optional[int] = None
    earliest_delivery_time: Optional[datetime] = None
    cluster_route: Optional[ClusterRoute] = None
    cluster_status: Optional[ClusterStatus] = None
