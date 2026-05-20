"""Wallet helpers."""
from sqlalchemy.orm import Session

from app.models.user_model import User
from app.models.wallet_model import Wallet, WalletTransaction


def get_or_create_wallet(db: Session, user: User) -> Wallet:
    w = db.query(Wallet).filter(Wallet.user_id == user.id).first()
    if not w:
        w = Wallet(user_id=user.id, balance=0)
        db.add(w)
        db.commit()
        db.refresh(w)
    return w


def credit(db: Session, user: User, amount: int, kind: str, note: str | None = None) -> Wallet:
    if amount == 0:
        return get_or_create_wallet(db, user)
    w = get_or_create_wallet(db, user)
    w.balance = max(0, w.balance + amount)
    db.add(WalletTransaction(wallet_id=w.id, amount=amount, kind=kind, note=note))
    db.commit()
    db.refresh(w)
    return w


def debit(db: Session, user: User, amount: int, kind: str, note: str | None = None) -> Wallet:
    return credit(db, user, -abs(amount), kind, note)
