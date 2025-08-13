from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.api.routes.orders import get_optimizer
from app.database import create_new_db_session
from app.crud import create_driver, update_driver
from app.models.driver import Driver
from app.schemas.driver import DriverCreate, DriverUpdate, DriverOut
from app.services.orders import OrdersOptimizer

router = APIRouter(prefix="/drivers", tags=["Drivers"])


@router.post("/", response_model=DriverOut, status_code=201)
def create_driver_in_db(
    driver_data: DriverCreate,
    db: Session = Depends(create_new_db_session),
):
    new_driver = create_driver(
        db=db,
        driver_data=driver_data,
    )
    return new_driver


@router.get("/", response_model=List[DriverOut])
def list_drivers(db: Session = Depends(create_new_db_session)):
    return db.query(Driver).all()


@router.patch("/{driver_id}", response_model=DriverOut)
def update_driver_in_db(
    driver_id: int,
    driver_update: DriverUpdate,
    db: Session = Depends(create_new_db_session),
):
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    driver = update_driver(db=db, driver=driver, driver_update=driver_update)
    return driver


@router.get("/available", response_model=List[DriverOut])
def get_available_drivers_with_location(
    optimizer: OrdersOptimizer = Depends(get_optimizer),
    eta_threshold_minutes: int = Query(10, ge=0),
):
    """
    Get drivers who are available or delivering and finishing soon, with known location.
    """
    return optimizer.fetch_available_drivers_with_location(
        eta_threshold_minutes=eta_threshold_minutes
    )
