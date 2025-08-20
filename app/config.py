import os
import secrets
from typing import Dict, Any
from dotenv import load_dotenv

from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/pizza_db"
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_SETTINGS__")
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    FIRST_SUPERUSER: str = "user@example.com"
    DB_USERNAME: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "pizza_db"
    ROUTE_SERVICE_PROVIDER: str = "openrouteservice"
    POSTAL_CODE: str
    CITY: str
    COUNTRY: str


class ClusteringSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CLUSTERING_SETTINGS__")
    MAX_PIZZAS_PER_CLUSTER: int = 10
    CLUSTER_TIME_WINDOW_MINUTES: int = 15
    CLUSTER_DISTANCE_THRESHOLD: int = 120
    START_LOCATION_LON: float
    START_LOCATION_LAT: float
    ADDRESS: str
    POSTAL_CODE: str
    CITY: str
    COUNTRY: str
    ETA_THRESHOLD_MINUTES: int = 10


class ChefExperience(str, Enum):
    JUNIOR = "junior"
    MIDDLE = "middle"
    SENIOR = "senior"


class PizzaType(str, Enum):
    RUOTA_DI_CARRO = "ruota_di_carro_napoletana"
    NAPOLETANA = "napoletana"
    CONTEMPORANEA = "contemporanea"
    CLASSICA = "classica"


class PizzaPreparationSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PIZZA_PREPARATION_SETTINGS__")
    CHEFS: int
    CHEF_EXPERIENCE: ChefExperience
    CHEF_CAPACITY: Dict[str, int]
    BAKE_TIMES: Dict[str, int]
    NUM_OVENS: int
    SINGLE_OVEN_CAPACITY: int
    PIZZA_TYPE: PizzaType


class OpenRouteServiceSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OPENROUTESERVICE__")
    ROUTE_SERVICE_API_KEY: str
    PROFILE: str
    METRIC: str
    UNITS: str


class GoogleMapsSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GOOGLE_MAPS__")


settings = Settings()
open_route_settings = OpenRouteServiceSettings()
google_maps_settings = GoogleMapsSettings()
