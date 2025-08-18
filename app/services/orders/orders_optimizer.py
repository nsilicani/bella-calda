import secrets

from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
from logging import Logger

from geopy.distance import geodesic
from sklearn.cluster import AgglomerativeClustering

from app.config import ClusteringSettings
from app.models.driver import Driver
from app.models.order import Order
from app.schemas.cluster import ClusterRoute, OrderCluster, DeliveryStep, RouteSegment
from app.schemas.order import DeliveryAddress, OrderResponse
from app.services.route_planner.base import RoutePlannerService


class OrdersOptimizer:
    def __init__(
        self,
        db: Session,
        route_planner: RoutePlannerService,
        clustering_settings: ClusteringSettings,
        logger: Logger,
    ):
        self.db = db
        self.route_planner = route_planner
        self.clustering_settings = clustering_settings
        self.logger = logger

    async def run(self):
        ready_orders = self.fetch_unassigned_orders()
        filtered_orders = self.filter_out_unavailable_orders(ready_orders)

        self.logger.info(
            f"Fetched {len(ready_orders)} orders, {len(filtered_orders)} after filtering."
        )
        clustered_orders = await self.compute_clustered_orders(
            filtered_orders=filtered_orders
        )
        # TODO: complete optimization process
        return clustered_orders

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

    def cluster_orders_by_time_window(
        self, orders: List[Order], time_window_minutes: int = 15
    ) -> Dict[datetime, List[Order]]:
        time_buckets: Dict[datetime, List[Order]] = defaultdict(list)
        for order in orders:
            rounded_time = order.desired_delivery_time.replace(
                minute=(order.desired_delivery_time.minute // time_window_minutes)
                * time_window_minutes,
                second=0,
                microsecond=0,
            )
            time_buckets[rounded_time].append(order)
        return time_buckets

    async def cluster_orders_by_geographic_proximity(
        self,
        orders: List[Order],
        max_pizzas_per_cluster: int = 10,
        cluster_distance_threshold: int = 120,
    ) -> List[List[Order]]:
        if len(orders) < 2:
            return [orders]

        # One or more pairs of lng/lat values: https://openrouteservice-py.readthedocs.io/en/latest/#module-openrouteservice.distance_matrix
        coords = [(order.lon, order.lat) for order in orders]
        self.logger.info(f"{coords=}")

        try:
            matrix_response = self.route_planner.compute_distance_matrix(
                coords=coords,
            )
        except Exception as e:
            raise Exception(f"Route Planner API error: {e}")

        matrix_metrics = (
            "durations" if self.route_planner.metric == "duration" else "distances"
        )
        dist_matrix = matrix_response[matrix_metrics]

        clustering = AgglomerativeClustering(
            n_clusters=None,
            metric="precomputed",
            linkage="average",
            distance_threshold=cluster_distance_threshold,  # max N minutes between points
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
                pizza_count = len(order.items["food"])
                if total_pizzas + pizza_count > max_pizzas_per_cluster:
                    final_clusters.append(buffer)
                    buffer = []
                    total_pizzas = 0
                buffer.append(order)
                total_pizzas += pizza_count
            if buffer:
                final_clusters.append(buffer)

        return final_clusters

    def fetch_available_drivers_with_location(
        self, eta_threshold_minutes: int = 10
    ) -> List[Driver]:
        """
        Fetch drivers who are available or whose delivery will finish soon,
        and have a known location.
        """
        now = datetime.utcnow()

        drivers = (
            self.db.query(Driver)
            .filter(
                (Driver.status == "available")
                | (
                    (Driver.status == "delivering")
                    & (
                        Driver.estimated_finish_time
                        <= now + timedelta(minutes=eta_threshold_minutes)
                    )
                )
            )
            .filter(Driver.lat.isnot(None), Driver.lon.isnot(None))
            .all()
        )

        self.logger.info(f"Fetched {len(drivers)} available drivers with location")
        return drivers

    def compute_total_items(self, orders: List[Order]) -> int:
        return sum([len(o.items["food"]) for o in orders])

    async def compute_clustered_orders(
        self, filtered_orders: List[Order]
    ) -> List[OrderCluster]:
        clustered_orders = []

        # Cluster orders by time
        self.logger.info(f"Cluster orders by time ...")
        # TODO: how to deal with time_window parameter ?
        time_clusters = self.cluster_orders_by_time_window(orders=filtered_orders)

        # Cluster order by geographic proximity
        for time_window, time_cluster in time_clusters.items():
            self.logger.info(f"Cluster orders by geographic proximity ...")
            geo_clusters = await self.cluster_orders_by_geographic_proximity(
                orders=time_cluster
            )
            for geo_cluster in geo_clusters:
                # Compute total items
                total_items = self.compute_total_items(geo_cluster)

                # Compute cluster_route
                cluster_route = self.compute_cluster_route(
                    orders=geo_cluster,
                    start_location=(
                        self.clustering_settings.START_LOCATION_LON,
                        self.clustering_settings.START_LOCATION_LAT,
                    ),
                )

                # Compute earliest delivery
                earliest_delivery_time = min(
                    [o.desired_delivery_time for o in geo_cluster]
                )
                # Store cluster
                cluster_obj = OrderCluster(
                    cluster_id=cluster_route.id,
                    time_window=time_window,
                    orders=[OrderResponse.model_validate(o) for o in geo_cluster],
                    total_items=total_items,
                    earliest_delivery_time=earliest_delivery_time,
                    cluster_route=cluster_route,
                )
                clustered_orders.append(cluster_obj)
        return clustered_orders

    def compute_cluster_route(
        self, orders: List[Order], start_location: Tuple[float]
    ) -> ClusterRoute:
        # Building coordinates: driver starts and ends at pizza restaurant location (start_location)
        coordinates = (
            [start_location] + [(o.lon, o.lat) for o in orders] + [start_location]
        )
        # Setting starting location
        PIZZA_RESTAURANT_BASE = DeliveryAddress(
            address=self.clustering_settings.ADDRESS,
            postal_code=self.clustering_settings.POSTAL_CODE,
            city=self.clustering_settings.CITY,
            country=self.clustering_settings.COUNTRY,
        )

        # Get directions
        direction_response = self.route_planner.get_directions(
            coordinates=coordinates, optimize_waypoints=True, format="json"
        )
        # Parse response
        parsed_route = self.route_planner.format_direction_response(
            coordinates=coordinates,
            direction_response=direction_response,
        )
        route = parsed_route["route"]
        visited_to_coord = parsed_route["visited_to_coord"]
        duration_from_start = 0

        route_segment_list = []
        for visited_idx, segment in enumerate(route["segments"]):
            segment_distance = segment["distance"]
            segment_duration = segment["duration"]

            # Storing steps
            delivery_steps = []
            for step in segment["steps"]:
                step_name = step["name"]
                step_distance = step["distance"]
                step_duration = step["duration"]
                duration_from_start += step_duration
                step_instruction = step["instruction"]
                step_way_points = step["way_points"]
                step_type = step["type"]
                delivery_step = DeliveryStep(
                    name=step_name,
                    type=step_type,
                    distance=step_distance,
                    duration=step_duration,
                    duration_from_start=round(duration_from_start, 2),
                    instruction=step_instruction,
                    way_points=step_way_points,
                )
                delivery_steps.append(delivery_step)

            # Setting segment start and end
            if visited_idx == 0:
                seg_start = PIZZA_RESTAURANT_BASE
                seg_start_idx = None
                seg_end_idx = visited_idx
            elif visited_idx == len(route["segments"]) - 1:
                seg_start_idx = visited_idx - 1
                seg_end_idx = None
                seg_end = PIZZA_RESTAURANT_BASE
            else:
                seg_start_idx = visited_idx - 1
                seg_end_idx = visited_idx

            idx_start_in_orders = (
                visited_to_coord[seg_start_idx] if seg_start_idx is not None else None
            )
            idx_end_in_orders = (
                visited_to_coord[seg_end_idx] if seg_end_idx is not None else None
            )
            seg_start = (
                orders[idx_start_in_orders].delivery_address
                if idx_start_in_orders is not None
                else PIZZA_RESTAURANT_BASE
            )
            seg_end = (
                orders[idx_end_in_orders].delivery_address
                if idx_end_in_orders is not None
                else PIZZA_RESTAURANT_BASE
            )
            # Storing segment
            route_segment = RouteSegment(
                distance=segment_distance,
                duration=segment_duration,
                steps=delivery_steps,
                segment_start=seg_start,
                segment_end=seg_end,
                duration_from_start=round(duration_from_start, 2),
                delivery_address=seg_end,
            )
            route_segment_list.append(route_segment)
        return ClusterRoute(
            id=secrets.token_hex(2),
            distance=parsed_route["distance"],
            duration=parsed_route["duration"],
            segments=route_segment_list,
        )
