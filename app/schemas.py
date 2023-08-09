from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# USER


class UserCreate(BaseModel):
    username: str
    ime_prezime: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[str] = None
    user_email: Optional[EmailStr] = None
