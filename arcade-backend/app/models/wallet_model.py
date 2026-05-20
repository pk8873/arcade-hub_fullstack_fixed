"""Wallet + transaction models. Virtual coins only - NOT real money."""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    balance = Column(Integer, default=0, nullable=False)  # coins
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    transactions = relationship("WalletTransaction", back_populates="wallet", cascade="all, delete-orphan")


class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Integer, nullable=False)  # positive = credit, negative = debit
    kind = Column(String(32), nullable=False)  # signup_bonus, game_reward, game_entry, admin_adjustment
    note = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    wallet = relationship("Wallet", back_populates="transactions")
