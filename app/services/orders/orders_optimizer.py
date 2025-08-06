from sqlalchemy.orm import Session
from app.models.order import Order
from typing import List, Optional
from datetime import datetime

from geopy.distance import geodesic
from sklearn.cluster import AgglomerativeClustering

from app.services.route_planner.base import RoutePlannerService


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
            # This allows filtering based on creation timestamps — useful for diagnostics or simulating "what-if" batches over specific time intervals.
            if start_time and order.created_at < start_time:
                continue
            if end_time and order.created_at > end_time:
                continue
            # This allows filtering for orders that are close enough to a specific area — useful for zone-based delivery planning or real-time geographic queries
            if lat is not None and lon is not None and radius_km is not None:
                order_coords = (order.lat, order.lon)
                center_coords = (lat, lon)
                if geodesic(order_coords, center_coords).km > radius_km:
                    continue

            filtered.append(order)

        return filtered

    async def cluster_orders(
        self,
        route_planner: RoutePlannerService,
        orders: List[Order],
        max_pizzas_per_cluster: int = 10,
    ) -> List[List[Order]]:
        if len(orders) < 2:
            return [orders]

        coords = [(order.lon, order.lat) for order in orders]

        try:
            matrix_response = route_planner.compute_distance_matrix(
                coords=coords,
            )
        except Exception as e:
            raise Exception(f"Route Planner API error: {e}")

        matrix_metrics = (
            "durations" if route_planner.metric == "duration" else "distances"
        )
        dist_matrix = matrix_response[matrix_metrics]

        clustering = AgglomerativeClustering(
            n_clusters=None,
            metric="precomputed",
            linkage="average",
            # TODO: set distance_threshold properly
            distance_threshold=2,  # max N minutes between points
        )
        labels = clustering.fit_predict(dist_matrix)

        clustered_orders = {}
        for label, order in zip(labels, orders):
            clustered_orders.setdefault(label, []).append(order)

        # Now enforce driver capacity (max pizzas per cluster)
        final_clusters = []
        for cluster in clustered_orders.values():
            buffer = []
            total_pizzas = 0
            for order in cluster:
                # TODO: implement pizza count robustly
                pizza_count = len(order.items.split(","))
                if total_pizzas + pizza_count > max_pizzas_per_cluster:
                    final_clusters.append(buffer)
                    buffer = []
                    total_pizzas = 0
                buffer.append(order)
                total_pizzas += pizza_count
            if buffer:
                final_clusters.append(buffer)

        return final_clusters
