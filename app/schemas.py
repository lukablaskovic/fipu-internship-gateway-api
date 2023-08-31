from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from typing import Union


class User(BaseModel):
    id: int
    ime: str
    prezime: str
    email: EmailStr
    avatar: str
    account_type: str
    created_at: datetime

    class Config:
        from_attributes = True
        exclude = ("password",)


class StudentBase(BaseModel):
    ime: str
    prezime: str
    email: EmailStr
    JMBAG: str
    godina_studija: str


class StudentCreate(StudentBase):
    password: str
    process_instance_id: str


class Student(User):
    JMBAG: str
    godina_studija: str
    baserow_id: int
    process_instance_id: str


####################################################


class AdminBase(BaseModel):
    ime: str
    prezime: str
    email: EmailStr
    username: str


class AdminCreate(AdminBase):
    password: str


class Admin(User):
    username: str


####################################################


class LoginForm(BaseModel):
    email: str
    password: str
    remember_me: bool = False


class Token(BaseModel):
    access_token: str
    token_type: str
    timestamp: datetime


class TokenData(BaseModel):
    user_id: Optional[int] = None
    user_email: Optional[EmailStr] = None


UserOut = Union[Student, Admin]
