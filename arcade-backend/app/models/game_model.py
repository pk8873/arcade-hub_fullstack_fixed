"""Game scores model."""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.database import Base


class GameScore(Base):
    __tablename__ = "game_scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    game_key = Column(String(64), nullable=False, index=True)  # e.g. "fruit_slice"
    score = Column(Integer, nullable=False)
    duration_seconds = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
