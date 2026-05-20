"""Password hashing + JWT token helpers."""
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user_model import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def hash_password(pw: str) -> str:
    return pwd_context.hash(pw)


def verify_password(pw: str, hashed: str) -> bool:
    return pwd_context.verify(pw, hashed)


def create_access_token(sub: str, extra: Optional[dict] = None) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": sub, "exp": exp}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=["HS256"])


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
    user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    return user


def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin only")
    return user


def require_verified(user: User = Depends(get_current_user)) -> User:
    if not user.is_verified:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Email not verified")
    return user
