"""Models for Sky Climb, Flash Duel, Pitch Stocks."""
from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Boolean
from app.database import Base


class CrashRound(Base):
    __tablename__ = "crash_rounds"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    bet = Column(Integer, nullable=False)
    cashout_at = Column(Float, nullable=True)
    crash_at = Column(Float, nullable=False)
    payout = Column(Integer, nullable=False, default=0)
    won = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class QuizResult(Base):
    __tablename__ = "quiz_results"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    correct = Column(Integer, nullable=False)
    total = Column(Integer, nullable=False)
    avg_ms = Column(Integer, nullable=False, default=0)
    score = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class StockHolding(Base):
    __tablename__ = "stock_holdings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    player_key = Column(String(64), nullable=False, index=True)
    shares = Column(Integer, nullable=False, default=0)
    avg_cost = Column(Float, nullable=False, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
