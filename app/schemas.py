from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from enum import Enum

# USER


class ProfileType(str, Enum):
    ADMIN = "admin"
    STUDENT = "student"
    COMPANY = "company"


class UserCreate(BaseModel):
    username: str
    ime_prezime: str
    email: EmailStr
    password: str
    profile_type: ProfileType


class UserOut(BaseModel):
    id: int
    username: str
    ime_prezime: str
    email: EmailStr
    profile_type: ProfileType = ProfileType.STUDENT

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
    user_email: Optional[EmailStr] = None
