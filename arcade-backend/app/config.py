"""Application configuration loaded from environment variables."""
import os
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Core
    app_name: str = "Arcade Hub"
    app_env: str = os.getenv("APP_ENV", "development")
    secret_key: str = os.getenv("SECRET_KEY", "change-me-in-production-please")
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # Database (SQLite by default, set DATABASE_URL for Postgres on Render)
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./arcade.db")

    def model_post_init(self, __context) -> None:
        # Render / Heroku give "postgres://..." but SQLAlchemy 2 + psycopg3
        # needs the "postgresql+psycopg://" driver scheme.
        url = self.database_url
        if url.startswith("postgres://"):
            url = "postgresql+psycopg://" + url[len("postgres://"):]
        elif url.startswith("postgresql://") and "+psycopg" not in url:
            url = "postgresql+psycopg://" + url[len("postgresql://"):]
        object.__setattr__(self, "database_url", url)

    # Frontend base URL (used in verification emails)
    frontend_url: str = os.getenv("FRONTEND_URL", "https://arcade-hub-fullstack-fixed.onrender.com")
    backend_url: str = os.getenv("BACKEND_URL", "https://arcade-hub-3.onrender.com")

    # CORS
    cors_origins: str = os.getenv("CORS_ORIGINS", "*")

    # SMTP (use any free provider: Gmail app password, Brevo, Mailtrap, etc.)
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "www.patnametro.com@gmail.com")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "qghe tihx cygr gybq")
    smtp_from: str = os.getenv("SMTP_FROM", "www.patnametro.com@gmail.com")
    smtp_tls: bool = os.getenv("SMTP_TLS", "true").lower() == "true"

    # If true, emails are printed to console instead of sent (great for local dev).
    email_console_fallback: bool = os.getenv("EMAIL_CONSOLE_FALLBACK", "true").lower() == "true"

    # Initial wallet balance on signup (virtual coins, NOT real money)
    signup_bonus_coins: int = int(os.getenv("SIGNUP_BONUS_COINS", "500"))

    # Admin bootstrap (auto-created on startup if missing)
    admin_email: str = os.getenv("ADMIN_EMAIL", "admin@gmail.com")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "admin123")

    @property
    def cors_origins_list(self) -> List[str]:
        raw = self.cors_origins.strip()
        if raw == "*" or not raw:
            return ["*"]
        return [o.strip() for o in raw.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
