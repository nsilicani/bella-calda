from base import RoutePlannerService

from openrouteservice import Client


class OpenRouteService(RoutePlannerService):
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.client = self.initialize_client()

    def initialize_client(self) -> Client:
        return Client(key=self.key)

    def get_coordinates(self, address_from, address_to):
        coord_from = self.client.pelias_search(text=address_from)["features"][0][
            "geometry"
        ]["coordinates"]
        coord_to = self.client.pelias_search(text=address_to)["features"][0][
            "geometry"
        ]["coordinates"]
        return coord_from, coord_to

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

    def _get_optimize_route(self) -> None:
        pass
