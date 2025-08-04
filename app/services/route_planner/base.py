from abc import ABC, abstractmethod


class RoutePlannerService(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def initialize_client(self):
        pass

    @abstractmethod
    def get_coordinates(self, address_from: str, address_to: str):
        pass

    @abstractmethod
    def get_directions(self):
        pass

    @abstractmethod
    def get_optimize_route(self):
        pass
