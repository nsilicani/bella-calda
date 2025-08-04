from app.config import settings
from app.models.user import User
from app.auth.utils import hash_password
from app.database import DatabaseManager
from app.crud import create_user


def init_db() -> None:
    with DatabaseManager() as db_session:
        user = (
            db_session.query(User)
            .filter(User.email == settings.FIRST_SUPERUSER)
            .first()
        )
    if not user:
        user_in = User(
            email="user@example.com",
            hashed_password=hash_password("password123"),
            full_name="Test User",
            role="user",  # or "staff" or "admin"
        )
        user = create_user(db=db_session, new_user=user_in)


if __name__ == "__main__":
    init_db()
