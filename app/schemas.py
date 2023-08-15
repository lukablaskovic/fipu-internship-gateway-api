from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class StudentBase(BaseModel):
    name: str
    surname: str
    email: EmailStr
    jmbag: str
    year_of_study: str


class StudentCreate(StudentBase):
    password: str


class Student(StudentBase):
    id: int
    avatar: str = None
    type: str
    created_at: Optional[datetime] = None
    baserow_id: int


class StudentOut(Student):
    class Config:
        from_attributes = True
        exclude = ("password",)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
    user_email: Optional[EmailStr] = None
