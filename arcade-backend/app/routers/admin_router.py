"""Admin routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.game_model import GameScore
from app.models.user_model import User
from app.models.wallet_model import Wallet
from app.schemas import AdminAdjustBalance, AdminStats, AdminUserRow
from app.security import get_current_admin
from app.services.wallet_service import credit, get_or_create_wallet

router = APIRouter()


@router.get("/stats", response_model=AdminStats)
def stats(_: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    total_users = db.query(func.count(User.id)).scalar() or 0
    verified = db.query(func.count(User.id)).filter(User.is_verified.is_(True)).scalar() or 0
    scores = db.query(func.count(GameScore.id)).scalar() or 0
    coins = db.query(func.coalesce(func.sum(Wallet.balance), 0)).scalar() or 0
    return AdminStats(
        total_users=total_users,
        verified_users=verified,
        total_scores=scores,
        total_coins_in_circulation=int(coins),
    )


@router.get("/users", response_model=list[AdminUserRow])
def list_users(_: User = Depends(get_current_admin), db: Session = Depends(get_db), limit: int = 100):
    rows = (
        db.query(User, Wallet.balance)
        .outerjoin(Wallet, Wallet.user_id == User.id)
        .order_by(User.created_at.desc())
        .limit(min(limit, 500))
        .all()
    )
    return [
        AdminUserRow(
            id=u.id, email=u.email, username=u.username,
            is_verified=u.is_verified, is_admin=u.is_admin, is_active=u.is_active,
            balance=int(b or 0), created_at=u.created_at,
        )
        for (u, b) in rows
    ]


@router.post("/users/{user_id}/toggle-active", response_model=AdminUserRow)
def toggle_active(user_id: int, _: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(404, "User not found")
    u.is_active = not u.is_active
    db.commit()
    w = get_or_create_wallet(db, u)
    return AdminUserRow(
        id=u.id, email=u.email, username=u.username,
        is_verified=u.is_verified, is_admin=u.is_admin, is_active=u.is_active,
        balance=w.balance, created_at=u.created_at,
    )


@router.post("/users/{user_id}/force-verify", response_model=AdminUserRow)
def force_verify(user_id: int, _: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(404, "User not found")
    u.is_verified = True
    u.verification_token = None
    db.commit()
    w = get_or_create_wallet(db, u)
    return AdminUserRow(
        id=u.id, email=u.email, username=u.username,
        is_verified=u.is_verified, is_admin=u.is_admin, is_active=u.is_active,
        balance=w.balance, created_at=u.created_at,
    )


@router.post("/wallet/adjust")
def adjust_balance(payload: AdminAdjustBalance, _: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == payload.user_id).first()
    if not u:
        raise HTTPException(404, "User not found")
    w = credit(db, u, payload.amount, "admin_adjustment", payload.note)
    return {"ok": True, "new_balance": w.balance}
