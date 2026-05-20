"""User model."""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(60), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    verification_token = Column(String(128), nullable=True, index=True)
    verification_sent_at = Column(DateTime, nullable=True)
    reset_token = Column(String(128), nullable=True, index=True)
    reset_sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
