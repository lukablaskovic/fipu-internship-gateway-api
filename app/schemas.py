from pydantic import BaseModel, EmailStr, ValidationError
from typing import Optional
from datetime import datetime
from typing import Union

class Conversation(BaseModel):
    id: int
    user_1_id: int
    user_2_id: int
    status: str
    user_1_last_message_read_id: Union[int, None] = None
    user_2_last_message_read_id: Union[int, None] = None
    user_1_active: bool
    user_2_active: bool
    timestamp: datetime

    class Config:
        from_attributes = True

class ConversationPost(BaseModel):
    user_1_id: int
    user_2_id: int
    status: str
    user_1_last_message_read_id: Union[int, None] = None
    user_2_last_message_read_id: Union[int, None] = None
    user_1_active: bool
    user_2_active: bool

class ConversationUpdate(BaseModel):
    status: Union[str, None] = None
    user_1_last_message_read_id: Union[int, None] = None
    user_2_last_message_read_id: Union[int, None] = None
    user_1_active: Union[bool, None] = None
    user_2_active: Union[bool, None] = None

class Message(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    timestamp: datetime

    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    conversation_id: int
    receiver_id: int
    content: str

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
    baserow_id: Optional[int] = None


class Student(User):
    JMBAG: str
    godina_studija: str
    process_instance_id: Optional[str] = None
    baserow_id: int


try:
    Student()
except ValidationError as exc:
    print(repr(exc.errors()[0]["type"]))


class ProcessInstanceUpdate(BaseModel):
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
