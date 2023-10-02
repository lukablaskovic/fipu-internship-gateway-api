from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean 
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql.expression import text
from app import db

Base = db.Base


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    avatar = Column(
        String,
        nullable=False,
        default="https://avatars.dicebear.com/v2/gridy/Nelson-Jerde.svg",
    )
    ime = Column(String, nullable=False)
    prezime = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)

    account_type: Mapped[str]
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
    )
    __mapper_args__ = {
        "polymorphic_identity": "employee",
        "polymorphic_on": "account_type",
    }

    def __repr__(self):
        return f"{self.__class__.__name__}({self.ime!r})"


class Admin(User):
    __tablename__ = "admin"
    id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=False)
    __mapper_args__ = {
        "polymorphic_identity": "admin",
    }


class Student(User):
    __tablename__ = "student"
    id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    baserow_id: Mapped[int] = mapped_column(Integer, nullable=False)
    JMBAG = Column(String, nullable=False, unique=True)
    godina_studija = Column(String, nullable=True)
    process_instance_id = Column(String, nullable=True)
    __mapper_args__ = {
        "polymorphic_identity": "student",
    }

class Message(Base):
    __tablename__ = "message"
    id: Mapped[int] = mapped_column(primary_key=True)
    sender_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    receiver_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()"))

    sender = relationship('User', foreign_keys=[sender_id])
    receiver = relationship('User', foreign_keys=[receiver_id])

    def __repr__(self):
        return f"Message(sender_id={self.sender_id}, receiver_id={self.receiver_id}, content={self.content})"
    
class Conversation(Base):
    __tablename__ = "conversation"

    id = Column(Integer, primary_key=True, index=True)
    user_1_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user_2_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user_1_last_message_read_id = Column(Integer, ForeignKey('message.id'), nullable=True)
    user_2_last_message_read_id = Column(Integer, ForeignKey('message.id'), nullable=True)
    status = Column(String, nullable=False)
    user_1_active = Column(Boolean, nullable=False)
    user_2_active = Column(Boolean, nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()"))

    user_1 = relationship('User', foreign_keys=[user_1_id])
    user_2 = relationship('User', foreign_keys=[user_2_id])
    last_message_read1 = relationship('Message', foreign_keys=[user_1_last_message_read_id])
    last_message_read2 = relationship('Message', foreign_keys=[user_2_last_message_read_id])

    def __repr__(self):
        return f"Conversation(user_1_id={self.user_1_id}, user_2_id={self.user_2_id}, status={self.status})"