from sqlalchemy.orm import Session

from app.models.user import User


def create_user(*, db: Session, new_user: User) -> User:
    # TODO: Add validation with Pydantic
    db_obj = new_user
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_user_by_email(db: Session, *, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()
