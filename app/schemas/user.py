from pydantic import BaseModel, EmailStr, constr
from typing import Literal


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: constr(min_length=6)
    role: Literal["user", "staff", "admin", "driver"]
