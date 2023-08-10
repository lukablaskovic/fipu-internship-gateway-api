from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.dialects.postgresql import ENUM

from app import db

Base = db.Base

ProfileType = ENUM("admin", "student", "company", name="profiletype", create_type=True)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    profile_type = Column(ProfileType, nullable=False)
    avatar = Column(String, nullable=False)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    ime_prezime = Column(String, nullable=False)
    password = Column(String, nullable=False)
