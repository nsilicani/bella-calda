from sqlalchemy import Column, Integer, String, Enum
from app.database import Base
import enum


class RoleEnum(str, enum.Enum):
    user = "user"
    staff = "staff"
    driver = "driver"
    superuser = "superuser"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.user)
