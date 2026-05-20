"""Wallet routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_model import User
from app.models.wallet_model import WalletTransaction
from app.schemas import WalletBalance, WalletTransactionOut
from app.security import get_current_user
from app.services.wallet_service import get_or_create_wallet

router = APIRouter()


@router.get("/balance", response_model=WalletBalance)
def balance(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    w = get_or_create_wallet(db, user)
    return WalletBalance(balance=w.balance, updated_at=w.updated_at)


@router.get("/transactions", response_model=list[WalletTransactionOut])
def transactions(user: User = Depends(get_current_user), db: Session = Depends(get_db), limit: int = 50):
    w = get_or_create_wallet(db, user)
    return (
        db.query(WalletTransaction)
        .filter(WalletTransaction.wallet_id == w.id)
        .order_by(WalletTransaction.created_at.desc())
        .limit(min(limit, 200))
        .all()
    )
