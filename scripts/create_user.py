import os

from dotenv import load_dotenv

load_dotenv()

from app.config import settings
from app.models.user import User
from app.models.driver import Driver, DriverStatus
from app.auth.utils import hash_password
from app.database import DatabaseManager
from app.crud import create_user, create_driver

from constants import TEST_USERS_FOR_CLUSTERING, TEST_USER_DRIVERS

START_LOCATION_LON = float(os.environ["CLUSTERING_SETTINGS__START_LOCATION_LON"])
START_LOCATION_LAT = float(os.environ["CLUSTERING_SETTINGS__START_LOCATION_LAT"])
assert START_LOCATION_LON is not None, f"Set START_LOCATION_LON as env"
assert START_LOCATION_LAT is not None, f"Set START_LOCATION_LAT as env"


def init_db() -> None:
    with DatabaseManager() as db_session:
        # Check superuser existence
        superuser = (
            db_session.query(User)
            .filter(User.email == settings.FIRST_SUPERUSER)
            .first()
        )

        # Create test users if not exists
        if not superuser:
            print("Creating Users ...")
            created_users = {}
            created_users_full_name = {}
            for test_user in TEST_USERS_FOR_CLUSTERING + TEST_USER_DRIVERS:
                existing = (
                    db_session.query(User)
                    .filter(User.email == test_user["email"])
                    .first()
                )
                if not existing:
                    user_in = User(
                        email=test_user["email"],
                        hashed_password=hash_password(test_user["password"]),
                        full_name=test_user["full_name"],
                        role=test_user["role"],
                    )
                    new_user = create_user(db=db_session, new_user=user_in)
                    created_users[test_user["email"]] = new_user.id
                    created_users_full_name[test_user["email"]] = new_user.full_name
                else:
                    created_users[test_user["email"]] = existing.id
                    created_users_full_name[test_user["email"]] = existing.full_name

            # Create drivers linked to the driver users
            print("Creating Drivers ...")
            for i, driver_user in enumerate(TEST_USER_DRIVERS):
                user_id = created_users[driver_user["email"]]
                user_full_name = created_users_full_name[test_user["email"]]
                # Check if driver already exists
                existing_driver = (
                    db_session.query(Driver).filter(Driver.user_id == user_id).first()
                )
                if not existing_driver:
                    new_driver = Driver(
                        user_id=user_id,
                        is_active=True,
                        full_name=user_full_name,
                        status=DriverStatus.AVAILABLE,
                        lat=round(START_LOCATION_LAT + i * 0.001, 6),
                        lon=round(START_LOCATION_LON + i * 0.001, 6),
                    )
                    create_driver(db=db_session, driver_data=new_driver)


if __name__ == "__main__":
    init_db()
