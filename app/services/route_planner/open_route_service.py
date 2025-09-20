from typing import List, Tuple
from .base import RoutePlannerService

from openrouteservice import Client


class OpenRouteService(RoutePlannerService):
    def __init__(
        self, api_key: str, profile: str, metric: str, units: str, logger
    ) -> None:
        self.api_key = api_key
        self.profile = profile
        self.metric = metric
        self.units = units
        self.logger = logger
        self.client = self.initialize_client()

    def initialize_client(self) -> Client:
        return Client(key=self.api_key)

    @staticmethod
    def format_address(address, postal_code, city, country):
        return f"{address}, {postal_code}, {city}, {country}"

    def get_coordinates(
        self, address: str, postal_code: str, city: str, country: str
    ) -> List[float]:
        formatted_address = self.format_address(
            address=address, postal_code=postal_code, city=city, country=country
        )
        coords = self.client.pelias_search(text=formatted_address)["features"][0][
            "geometry"
        ]["coordinates"]
        return coords

    def compute_distance_matrix(self, coords: List[List[float]]) -> List[List[float]]:
        return self.client.distance_matrix(
            locations=coords,
            profile=self.profile,
            metrics=[self.metric],
            units=self.units,
            resolve_locations=False,
            sources=list(range(len(coords))),
            destinations=list(range(len(coords))),
        )

    def get_directions(
        self,
        coordinates: List[Tuple[float]],
        optimize_waypoints: bool,
        format: str = "geojson",
    ):
        return self.client.directions(
            coordinates=coordinates,
            profile=self.profile,  # can also use 'foot-walking', 'cycling-regular', 'driving-car'
            format=format,
            optimize_waypoints=optimize_waypoints,
            preference="fastest",
        )

    def get_optimize_route(self, order_locations: List[Tuple[float]]) -> None:
        # TODO: implement method
        pass

    def format_direction_response(
        self, coordinates: List[Tuple[float]], direction_response: dict
    ) -> dict:
        route = direction_response["routes"][0]
        opt_route_coords = direction_response["metadata"]["query"]["coordinates"]
        # Dict mapping the sorted visitated addresses to corresponding coords.
        # Ex: {0: 3, 1: 2} means the first visited place is that located in coordinates with index 3 (i.e coordinates[3])
        # NOTE: We exclude the first and last visited coords because driver stars and ends at pizza restaurant
        visited_to_coord = {
            i: coordinates[1:-1].index(tuple(visited))
            for i, visited in enumerate(opt_route_coords[1:-1])
        }
        # NOTE: If coords are equal, then summary dict = {} and in each step distance and duration = 0.0
        distance = route["summary"].get("distance", 0.0)
        duration = route["summary"].get("duration", 0.0)
        return dict(
            route=route,
            visited_to_coord=visited_to_coord,
            distance=distance,
            duration=duration,
        )
