import os
import secrets
from dotenv import load_dotenv

from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/pizza_db"
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_CONFIGS__")
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
    ROUTE_SERVICE_API_KEY: str
    POSTAL_CODE: str
    CITY: str
    COUNTRY: str


settings = Settings()
