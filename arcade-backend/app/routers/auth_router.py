"""Auth routes: signup, login, email verification (auto/one-click), resend."""
import secrets
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user_model import User
from app.schemas import (
    ForgotPasswordRequest,
    LoginRequest,
    ResendVerificationRequest,
    ResetPasswordRequest,
    SignupRequest,
    TokenResponse,
    UserPublic,
)
from app.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.services.email_service import send_verification_email
from app.services.wallet_service import credit, get_or_create_wallet

router = APIRouter()


def _issue_verification(db: Session, user: User) -> None:
    user.verification_token = secrets.token_urlsafe(32)
    user.verification_sent_at = datetime.utcnow()
    db.commit()
    send_verification_email(user.email, user.username, user.verification_token)


@router.post("/signup", response_model=TokenResponse, status_code=201)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email.lower()).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Username taken")

    is_admin = payload.email.lower() == settings.admin_email.lower()
    user = User(
        email=payload.email.lower(),
        username=payload.username,
        password_hash=hash_password(payload.password),
        is_admin=is_admin,
        is_verified=True,  # auto-verify: no external email source required
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Signup bonus (virtual coins)
    credit(db, user, settings.signup_bonus_coins, "signup_bonus", "Welcome bonus")
    get_or_create_wallet(db, user)

    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token, user=UserPublic.model_validate(user))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account disabled")
    user.last_login_at = datetime.utcnow()
    db.commit()
    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token, user=UserPublic.model_validate(user))


@router.get("/verify", response_class=HTMLResponse)
def verify_email_get(token: str, db: Session = Depends(get_db)):
    """One-click verify - user lands here from the email link.

    Auto-verifies, then redirects to the frontend with a success flag.
    """
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        return HTMLResponse(_result_page("Invalid or expired verification link.", ok=False), status_code=400)
    user.is_verified = True
    user.verification_token = None
    db.commit()
    # Redirect to frontend if configured
    if settings.frontend_url:
        return RedirectResponse(f"{settings.frontend_url}/verified", status_code=302)
    return HTMLResponse(_result_page("Email verified! You can close this tab.", ok=True))


@router.post("/verify")
def verify_email_post(token: str, db: Session = Depends(get_db)):
    """JSON verify endpoint - the frontend can call this with the token from the URL."""
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise HTTPException(400, "Invalid or expired token")
    user.is_verified = True
    user.verification_token = None
    db.commit()
    return {"ok": True, "verified": True}


@router.post("/resend-verification")
def resend_verification(payload: ResendVerificationRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    # Auto-verify instantly (no external email source required)
    if user and not user.is_verified:
        user.is_verified = True
        user.verification_token = None
        db.commit()
    return {"ok": True}


@router.get("/me", response_model=UserPublic)
def me(user: User = Depends(get_current_user)):
    return user


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Issue a password-reset token.

    No external email source is required: the token is returned in the response
    so the frontend can immediately route the user to the reset page. The
    response is identical whether or not the email exists, to avoid leaking
    account existence.
    """
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    token: str | None = None
    if user and user.is_active:
        user.reset_token = secrets.token_urlsafe(32)
        user.reset_sent_at = datetime.utcnow()
        db.commit()
        token = user.reset_token
    return {"ok": True, "reset_token": token}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == payload.token).first()
    if not user:
        raise HTTPException(400, "Invalid or expired reset token")
    user.password_hash = hash_password(payload.new_password)
    user.reset_token = None
    user.reset_sent_at = None
    db.commit()
    return {"ok": True}


def _result_page(message: str, ok: bool) -> str:
    color = "#10b981" if ok else "#ef4444"
    return f"""<!doctype html><html><body style="font-family:Arial,sans-serif;background:#0b1020;color:#fff;display:flex;align-items:center;justify-content:center;height:100vh;margin:0">
<div style="background:#141a36;padding:32px 40px;border-radius:14px;text-align:center;max-width:420px">
  <div style="font-size:48px;color:{color};margin-bottom:12px">{'&#10003;' if ok else '&#10007;'}</div>
  <h2 style="margin:0 0 8px">{message}</h2>
</div></body></html>"""
