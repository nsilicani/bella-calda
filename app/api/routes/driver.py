from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import create_new_db_session
from app.crud import create_driver
from app.models.driver import Driver
from app.schemas.driver import DriverCreate, DriverOut

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
