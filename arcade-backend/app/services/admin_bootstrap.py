"""Bootstrap a default admin account on startup.

Creates an admin user from ADMIN_EMAIL / ADMIN_PASSWORD env vars if it does
not already exist. Defaults to admin@gmail.com / admin123 for local dev.

CHANGE THESE IN PRODUCTION via env vars. The defaults are intentionally weak
so you can log in immediately on first run, but they are NOT safe for a
public deployment.
"""
from __future__ import annotations

import logging
import os

from app.database import SessionLocal
from app.models.user_model import User
from app.security import hash_password
from app.services.wallet_service import credit, get_or_create_wallet
from app.config import settings

logger = logging.getLogger("admin_bootstrap")


def bootstrap_admin() -> None:
    admin_email = (os.getenv("ADMIN_EMAIL") or settings.admin_email or "admin@gmail.com").lower()
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    admin_username = os.getenv("ADMIN_USERNAME", "admin")

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == admin_email).first()
        if existing:
            # Make sure flags are right even if the row existed already.
            changed = False
            if not existing.is_admin:
                existing.is_admin = True
                changed = True
            if not existing.is_verified:
                existing.is_verified = True
                changed = True
            if not existing.is_active:
                existing.is_active = True
                changed = True
            if changed:
                db.commit()
            logger.info("Admin already exists: %s", admin_email)
            return

        user = User(
            email=admin_email,
            username=admin_username,
            password_hash=hash_password(admin_password),
            is_admin=True,
            is_verified=True,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        get_or_create_wallet(db, user)
        credit(db, user, settings.signup_bonus_coins, "signup_bonus", "Admin welcome bonus")

        logger.warning(
            "==================================================================\n"
            " Admin account created\n"
            "   email:    %s\n"
            "   password: %s\n"
            " CHANGE THIS PASSWORD via ADMIN_PASSWORD env var before deploying!\n"
            "==================================================================",
            admin_email, admin_password,
        )
    finally:
        db.close()
