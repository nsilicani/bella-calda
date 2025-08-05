from sqlalchemy.orm import Session
from app.models.order import Order
from typing import List, Optional
from datetime import datetime

from geopy.distance import geodesic


class OrdersOptimizer:
    def __init__(self, db: Session):
        self.db = db

    def run(self):
        ready_orders = self.fetch_unassigned_orders()
        filtered_orders = self.filter_out_unavailable_orders(ready_orders)

        # Add logging/debug prints if needed
        print(
            f"Fetched {len(ready_orders)} orders, {len(filtered_orders)} after filtering."
        )

        # TODO: continue with clustering, driver selection, etc.
        pass

    def fetch_unassigned_orders(self) -> List[Order]:
        return self.db.query(Order).filter(Order.status == "pending").all()

    def filter_out_unavailable_orders(
        self,
        orders: List[Order],
        *,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        radius_km: Optional[float] = None,
    ) -> List[Order]:
        filtered = []
        for order in orders:
            if not order.status != "pending":
                continue

            if start_time and order.created_at < start_time:
                continue
            if end_time and order.created_at > end_time:
                continue

            if lat is not None and lon is not None and radius_km is not None:
                order_coords = (order.lat, order.lon)
                center_coords = (lat, lon)
                if geodesic(order_coords, center_coords).km > radius_km:
                    continue

            filtered.append(order)

        return filtered
