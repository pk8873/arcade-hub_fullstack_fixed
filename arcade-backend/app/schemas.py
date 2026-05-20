"""Pydantic schemas for request/response models."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


# ---------- Auth ----------
class SignupRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=60, pattern=r"^[A-Za-z0-9_]+$")
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserPublic"


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class UserPublic(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_verified: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Wallet ----------
class WalletBalance(BaseModel):
    balance: int
    updated_at: Optional[datetime] = None


class WalletTransactionOut(BaseModel):
    id: int
    amount: int
    kind: str
    note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Games ----------
class ScoreSubmit(BaseModel):
    game_key: str = Field(min_length=1, max_length=64)
    score: int = Field(ge=0, le=10_000_000)
    duration_seconds: Optional[int] = Field(default=None, ge=0, le=24 * 3600)


class ScoreOut(BaseModel):
    id: int
    game_key: str
    score: int
    duration_seconds: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class LeaderboardRow(BaseModel):
    username: str
    score: int
    created_at: datetime


# ---------- Admin ----------
class AdminUserRow(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_verified: bool
    is_admin: bool
    is_active: bool
    balance: int
    created_at: datetime


class AdminAdjustBalance(BaseModel):
    user_id: int
    amount: int  # signed
    note: Optional[str] = None


class AdminStats(BaseModel):
    total_users: int
    verified_users: int
    total_scores: int
    total_coins_in_circulation: int


TokenResponse.model_rebuild()
