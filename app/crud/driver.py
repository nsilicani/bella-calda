from sqlalchemy.orm import Session

from app.models.driver import Driver
from app.schemas.driver import DriverCreate


def create_driver(*, db: Session, driver_data: DriverCreate):
    new_driver = Driver(
        user_id=driver_data.user_id,
        is_active=driver_data.is_active,
        current_route=driver_data.current_route,
    )
    db.add(new_driver)
    db.commit()
    db.refresh(new_driver)
    return new_driver
