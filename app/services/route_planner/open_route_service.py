from typing import List
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
        coord_from: str,
        coord_to: str,
        profile: str = "cycling-regular",
        format: str = "geojson",
    ):
        return self.client.directions(
            coordinates=[coord_from, coord_to],
            profile=profile,  # can also use 'foot-walking', 'cycling-regular', 'driving-car'
            format=format,
        )

    def get_optimize_route(self) -> None:
        pass
