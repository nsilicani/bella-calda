from sqlalchemy.orm import Session

from app.models.driver import Driver
from app.schemas.driver import DriverCreate, DriverUpdate


def create_driver(*, db: Session, driver_data: DriverCreate):
    new_driver = Driver(
        user_id=driver_data.user_id,
        full_name=driver_data.full_name,
        is_active=driver_data.is_active,
        current_route=driver_data.current_route,
        status=driver_data.status,
        lat=driver_data.lat,
        lon=driver_data.lon,
    )
    db.add(new_driver)
    db.commit()
    db.refresh(new_driver)
    return new_driver


def update_driver(*, db: Session, driver: Driver, driver_update: DriverUpdate):
    for field, value in driver_update.model_dump(exclude_unset=True).items():
        setattr(driver, field, value)

    db.commit()
    db.refresh(driver)
    return driver
