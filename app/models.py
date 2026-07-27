from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.database import Base

last_seen = Column(
    DateTime,
    default=datetime.utcnow
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    last_seen = Column(
        DateTime,
        default=datetime.utcnow
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    sender = Column(String, nullable=False)
    receiver = Column(String, nullable=False)

    message = Column(String, nullable=False)

    status = Column(
        String,
        default="sent",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )