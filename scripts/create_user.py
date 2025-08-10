from app.config import settings
from app.models.user import User
from app.auth.utils import hash_password
from app.database import DatabaseManager
from app.crud import create_user

from constants import TEST_USERS_FOR_CLUSTERING


def init_db() -> None:
    with DatabaseManager() as db_session:
        user = (
            db_session.query(User)
            .filter(User.email == settings.FIRST_SUPERUSER)
            .first()
        )
    if not user:
        for test_user in TEST_USERS_FOR_CLUSTERING:
            user_in = User(
                email=test_user["email"],
                hashed_password=hash_password(test_user["password"]),
                full_name=test_user["full_name"],
                role=test_user["role"],  # or "staff" or "admin"
            )
            user = create_user(db=db_session, new_user=user_in)


if __name__ == "__main__":
    init_db()
