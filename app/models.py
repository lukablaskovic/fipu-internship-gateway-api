from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text

from app import db

Base = db.Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    ime_prezime = Column(String, nullable=False)
    password = Column(String, nullable=False)
