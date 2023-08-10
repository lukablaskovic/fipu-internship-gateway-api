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
    avatar: str = "https://avatars.dicebear.com/v2/gridy/Nelson-Jerde.svg"
    ime_prezime: str
    email: EmailStr
    password: str
    profile_type: ProfileType = ProfileType.STUDENT


class UserOut(BaseModel):
    id: int
    username: str
    avatar: str
    ime_prezime: str
    email: EmailStr
    profile_type: ProfileType

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
    user_email: Optional[EmailStr] = None
