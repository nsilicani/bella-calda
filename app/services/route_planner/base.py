from abc import ABC, abstractmethod
from typing import List


class RoutePlannerService(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def initialize_client(self):
        pass

    @abstractmethod
    def format_address(self, address: str, postal_code: str, city: str, state: str):
        pass

    @abstractmethod
    def get_coordinates(
        self, address: str, postal_code: str, city: str, state: str
    ) -> List[float]:
        """
        Converting addresses into geographic coordinates
        """
        pass

    @abstractmethod
    def get_directions(self):
        pass

    @abstractmethod
    def get_optimize_route(self):
        pass
