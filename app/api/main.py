from fastapi import APIRouter

from app.api.routes import auth, orders
from app.config import settings

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(orders.router)
