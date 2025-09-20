from fastapi import APIRouter

from app.api.routes import auth, driver, orders

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(driver.router)
api_router.include_router(orders.router)
