from app.services.route_planner.base import RoutePlannerService
from app.services.route_planner import OpenRouteService
# from app.services.route_planner.googlemaps import GoogleMapsService # future

from app.config import settings


def get_route_planner() -> RoutePlannerService:
    provider = settings.ROUTE_SERVICE_PROVIDER.lower()

    if provider == "openrouteservice":
        return OpenRouteService(api_key=settings.ROUTE_SERVICE_API_KEY)
    # elif provider == "googlemaps":
    #     return GoogleMapsService(api_key=settings.ROUTE_SERVICE_API_KEY)
    else:
        raise ValueError(f"Unsupported route service provider: {provider}")
