from typing import List, Tuple
from datetime import datetime
from pydantic import BaseModel, Field

from app.schemas.order import OrderResponse


class OrderCluster(BaseModel):
    time_window: datetime
    orders: List[OrderResponse]
    total_items: int = Field(..., description="Total number of pizzas in the cluster")
    earliest_delivery_time: datetime = Field(
        ..., description="Earliest delivery time among orders"
    )
    cluster_route: List[str] = Field(..., description="Step of optimized route")

    @property
    def customer_locations(self) -> List[Tuple[float, float]]:
        """
        Extract (lat, lon) for each order.
        """
        return [(order.lat, order.lon) for order in self.orders]
