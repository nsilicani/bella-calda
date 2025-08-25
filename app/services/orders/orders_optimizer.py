import secrets

from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
from logging import Logger

from geopy.distance import geodesic
from sklearn.cluster import AgglomerativeClustering

from scipy.optimize import linear_sum_assignment
import numpy as np

from app.config import ClusteringSettings, PizzaPreparationSettings
from app.crud.cluster import create_cluster
from app.crud.order import update_order_status
from app.models.driver import Driver, DriverStatus
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
        pizza_prep_settings: PizzaPreparationSettings,
        logger: Logger,
    ):
        self.db = db
        self.route_planner = route_planner
        self.clustering_settings = clustering_settings
        self.pizza_prep_settings = pizza_prep_settings
        self.logger = logger

    async def run(self):
        # 1) Prepare inputs
        ready_orders = self.fetch_unassigned_orders()
        filtered_orders = self.filter_out_unavailable_orders(ready_orders)
        self.logger.info(
            f"Fetched {len(ready_orders)} orders, {len(filtered_orders)} after filtering."
        )

        clustered_orders = await self.compute_clustered_orders(
            filtered_orders=filtered_orders
        )
        clusters = sorted(clustered_orders, key=lambda x: x.earliest_delivery_time)
        # Persist clusters in DB. TODO: add "status" field in cluster model
        for c in clusters:
            new_cluster = create_cluster(db=self.db, order_cluster=c)
        drivers = self.fetch_available_drivers_with_location(
            eta_threshold_minutes=self.clustering_settings.ETA_THRESHOLD_MINUTES
        )
        self.logger.info(
            f"Total Clusters: {len(clusters)} | Available Drivers: {len(drivers)}"
        )

        current_time = datetime.utcnow()
        D, C = len(drivers), len(clusters)
        # No clusters -> nothing to do
        if C == 0:
            self.logger.info("No clusters to assign.")
            return {"driver_to_cluster": {}, "unassigned_clusters": {}}

        # No drivers -> defer all clusters
        if D == 0:
            self.logger.info("No drivers available; deferring all clusters.")
            return {
                "driver_to_cluster": {},
                "unassigned_clusters": {
                    cluster.id: {"motivations": "No drivers available"}
                    for cluster in clusters
                },
            }

        # 2) Build rectangular cost matrix with NaNs for infeasible pairs
        costs = np.full((D, C), np.nan, dtype=float)
        motivations = {}  # (driver_id, cluster_id) -> reason/feasible

        for j, cluster in enumerate(clusters):
            latest_prep_time = self.estimate_latest_pizza_ready_time(
                total_pizzas=cluster.total_items,
                chefs=self.pizza_prep_settings.CHEFS,
                chef_experience=self.pizza_prep_settings.CHEF_EXPERIENCE,
                chef_capacity=self.pizza_prep_settings.CHEF_CAPACITY,
                bake_times=self.pizza_prep_settings.BAKE_TIMES,
                num_ovens=self.pizza_prep_settings.NUM_OVENS,
                single_oven_capacity=self.pizza_prep_settings.SINGLE_OVEN_CAPACITY,
                pizza_type=self.pizza_prep_settings.PIZZA_TYPE,
                now=current_time,
            )
            dispatch_ready_time = max(current_time, latest_prep_time)

            for i, driver in enumerate(drivers):
                driver_ready_time = (
                    current_time - driver.estimated_finish_time
                    if getattr(driver, "estimated_finish_time", None)
                    else current_time
                )
                wait_time = max(timedelta(0), dispatch_ready_time - driver_ready_time)

                delivery_estimates = self.simulate_delivery_times(
                    cluster=cluster,
                    dispatch_ready_time=dispatch_ready_time,
                    time_for_payment=timedelta(seconds=120),
                )

                # Hotness constraint: 20 minutes max from bake/dispatch to drop
                violates_hotness = any(
                    est["delivery_time"] - dispatch_ready_time > timedelta(minutes=20)
                    for est in delivery_estimates.values()
                )
                if violates_hotness:
                    motivations[(driver.id, cluster.id)] = "Hotness constraint not met"
                    # leave as NaN (infeasible)
                    continue

                # Compute finite cost
                # TODO: pass weights as config
                cost = self.compute_assignment_cost(
                    wait_time=wait_time,
                    delivery_times=delivery_estimates,
                    route_duration=cluster.cluster_route.duration,
                    weight_wait_time=0.2,
                    weight_max_lateness=0.5,
                    weight_route_duration=0.3,
                )
                costs[i, j] = float(cost)
                motivations[(driver.id, cluster.id)] = "Feasible"

        # 3) Replace NaNs with a large finite penalty (Big-M), solve assignment
        #    Big-M must dominate any real cost. Derive from observed finite costs.
        finite_vals = costs[np.isfinite(costs)]
        if finite_vals.size == 0:
            # No feasible pairs at all: everyone unassigned
            self.logger.info(
                "No feasible (driver, cluster) pairs. Deferring all clusters."
            )
            return {
                "driver_to_cluster": {},
                "unassigned_clusters": {
                    c.id: {"motivations": "No feasible driver"} for c in clusters
                },
            }

        max_real_cost = float(np.max(finite_vals))
        BIG_M = max(1.0, max_real_cost) * 1e6  # huge, but finite
        filled_costs = np.where(np.isfinite(costs), costs, BIG_M)

        # NOTE: linear_sum_assignment accepts rectangular matrices.
        row_ind, col_ind = linear_sum_assignment(filled_costs)

        # 4) Post-process: anything that hit BIG_M is treated as unassigned
        driver_to_cluster = {}
        unassigned_clusters = {}

        assigned_cluster_idx = set()
        for i, j in zip(row_ind, col_ind):
            driver = drivers[i]
            cluster = clusters[j]
            cost_ij = filled_costs[i, j]

            if cost_ij >= BIG_M:  # infeasible -> do NOT assign
                # Mark this cluster as still unassigned; driver remains idle.
                unassigned_clusters[cluster.id] = {
                    "motivations": motivations.get(
                        (driver.id, cluster.id), "No feasible driver"
                    )
                }
                self.logger.info(
                    f"Defer Cluster {cluster.id} (infeasible for all drivers)."
                )
            else:
                driver_to_cluster[driver.id] = {
                    "cluster": cluster,
                    "cost": float(cost_ij),
                }
                assigned_cluster_idx.add(j)
                self.logger.info(
                    f"Assign Driver: {driver.full_name} -> Cluster: {cluster.id} | Cost: {cost_ij:.2f}"
                )

        # 5) Any cluster not selected at all (when D < C) is unassigned
        for j, cluster in enumerate(clusters):
            if j not in assigned_cluster_idx and cluster.id not in unassigned_clusters:
                unassigned_clusters[cluster.id] = {"motivations": "No driver available"}
                self.logger.info(f"Cluster {cluster.id} deferred (not enough drivers).")

        order_idxs_to_update = [
            order_ids
            for v in driver_to_cluster.values()
            for order_ids in v["cluster"].get_order_ids
        ]
        self.logger.info("Updating orders status ...")
        update_order_status(db=self.db, order_ids=order_idxs_to_update)

        # TODO: update cluster's status
        # TODO: mark driver as unavailable

        return {
            "driver_to_cluster": driver_to_cluster,
            "unassigned_clusters": unassigned_clusters,
        }

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
                (Driver.status == DriverStatus.AVAILABLE)
                | (
                    (Driver.status == DriverStatus.DELIVERING)
                    & (
                        Driver.estimated_finish_time
                        <= now + timedelta(minutes=eta_threshold_minutes)
                    )
                )
            )
            .filter(Driver.lat.isnot(None), Driver.lon.isnot(None))
            .all()
        )
        # drivers = self.db.query(Driver).all()

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

    def estimate_latest_pizza_ready_time(
        self,
        total_pizzas: int,
        chefs: int,
        chef_experience: str,
        chef_capacity: Dict[str, int],
        bake_times: Dict[str, int],
        num_ovens: int,
        single_oven_capacity: int,
        pizza_type: str,
        now: datetime,
    ) -> datetime:
        """
        Compute when all pizzas in a cluster will be ready (prep + bake).
        Assumes the pizzeria only makes ONE type of pizza (pizza_type).
        """

        # --- Step 1. Count pizzas ---
        if total_pizzas == 0:
            return now

        # --- Step 2. Prep capacity ---
        base_capacity = chef_capacity[chef_experience]

        if chefs == 1:
            prep_capacity = base_capacity
        elif chefs == 2:
            prep_capacity = base_capacity * 3  # nonlinear boost for 2 chefs
        else:
            prep_capacity = base_capacity * chefs  # assume linear for >2

        prep_cycle_time = 120  # seconds per prep cycle

        # --- Step 3. Prep finish times ---
        prep_finish_times = []
        pizzas_remaining = total_pizzas
        t = prep_cycle_time
        while pizzas_remaining > 0:
            batch = min(prep_capacity, pizzas_remaining)
            prep_finish_times.extend([t] * batch)
            pizzas_remaining -= batch
            t += prep_cycle_time

        prep_finish_times.sort()

        # --- Step 4. Baking phase ---
        bake_time = bake_times[pizza_type]
        oven_capacity = num_ovens * single_oven_capacity
        oven_next_free = 0  # when ovens are next available
        finish_times = []

        # Process pizzas in oven batches
        i = 0
        while i < len(prep_finish_times):
            batch_ready_time = max(prep_finish_times[i : i + oven_capacity])
            start_time = max(batch_ready_time, oven_next_free)
            finish_time = start_time + bake_time
            finish_times.append(finish_time)

            # update state
            oven_next_free = finish_time
            i += oven_capacity

        latest_finish = max(finish_times)
        return now + timedelta(seconds=latest_finish)

    def simulate_delivery_times(
        self,
        cluster: OrderCluster,
        dispatch_ready_time: datetime,
        time_for_payment: timedelta = timedelta(seconds=60),
    ) -> Dict[int, dict]:
        """
        Simulate delivery times for each order (segment) in the cluster. Return a dict mapping order id to delivery time and desidered delivery time
        """
        cumulative_time = 0
        delivery_times_dict = dict()
        assert len(cluster.orders) == len(
            cluster.cluster_route.segments[:-1]
        )  # Exclude last segment because it is the return to pizzeria (starting point)
        for order, segment in zip(cluster.orders, cluster.cluster_route.segments[:-1]):
            delivery_times_dict[order.id] = dict()
            cumulative_time += segment.duration
            delivery_time = dispatch_ready_time + timedelta(seconds=cumulative_time)
            # Compute time for payment
            delivery_time += time_for_payment
            delivery_times_dict[order.id]["delivery_time"] = delivery_time
            delivery_times_dict[order.id]["desired_delivery_time"] = (
                order.desired_delivery_time
            )
            lateness = (
                (delivery_time - order.desired_delivery_time).seconds
                if delivery_time > order.desired_delivery_time
                else 0.0
            )
            delivery_times_dict[order.id]["lateness"] = lateness
        return delivery_times_dict

    def compute_assignment_cost(
        self,
        wait_time,
        delivery_times,
        route_duration,
        weight_wait_time: float,
        weight_max_lateness: float,
        weight_route_duration: float,
    ) -> float:
        max_lateness = max(
            delivery_time["lateness"] for delivery_time in delivery_times.values()
        )
        return (
            weight_wait_time * wait_time.seconds
            + weight_max_lateness * max_lateness
            + weight_route_duration * route_duration
        )
