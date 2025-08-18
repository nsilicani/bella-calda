from app.config import settings
from app.models.user import User
from app.models.driver import Driver
from app.auth.utils import hash_password
from app.database import DatabaseManager
from app.crud import create_user, create_driver

from constants import TEST_USERS_FOR_CLUSTERING, TEST_USER_DRIVERS


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
            for driver_user in TEST_USER_DRIVERS:
                user_id = created_users[driver_user["email"]]
                user_full_name = created_users_full_name[test_user["email"]]
                # Check if driver already exists
                existing_driver = (
                    db_session.query(Driver).filter(Driver.user_id == user_id).first()
                )
                if not existing_driver:
                    new_driver = Driver(
                        user_id=user_id, is_active=True, full_name=user_full_name
                    )
                    create_driver(db=db_session, driver_data=new_driver)


if __name__ == "__main__":
    init_db()
