from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from typing import Union


class User(BaseModel):
    id: int
    name: str
    surname: str
    email: EmailStr
    avatar: str
    type: str
    created_at: datetime

    class Config:
        from_attributes = True
        exclude = ("password",)


class StudentBase(BaseModel):
    name: str
    surname: str
    email: EmailStr
    jmbag: str
    year_of_study: str


class StudentCreate(StudentBase):
    password: str


class Student(User):
    jmbag: str
    year_of_study: str
    baserow_id: int


####################################################


class AdminBase(BaseModel):
    name: str
    surname: str
    email: EmailStr
    username: str


class AdminCreate(AdminBase):
    password: str


class Admin(User):
    username: str


####################################################


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
    user_email: Optional[EmailStr] = None


UserOut = Union[Student, Admin]
