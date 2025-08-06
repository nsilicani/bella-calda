from app.services.route_planner.base import RoutePlannerService
from app.services.route_planner import OpenRouteService
# from app.services.route_planner.googlemaps import GoogleMapsService # future

from app.config import settings, open_route_settings, google_maps_settings


def get_route_planner() -> RoutePlannerService:
    provider = settings.ROUTE_SERVICE_PROVIDER.lower()

    if provider == "openrouteservice":
        return OpenRouteService(
            api_key=open_route_settings.ROUTE_SERVICE_API_KEY,
            profile=open_route_settings.PROFILE,
            metric=open_route_settings.METRIC,
            units=open_route_settings.UNITS,
        )
    elif provider == "googlemaps":
        # return GoogleMapsService(api_key=google_maps_settings.ROUTE_SERVICE_API_KEY)
        raise NotImplementedError("Google Maps service is not yet implemented.")
    else:
        raise ValueError(f"Unsupported route service provider: {provider}")
