"""SQLAlchemy database setup."""
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def _ensure_user_columns() -> None:
    """Lightweight migration: add password-reset columns if missing."""
    try:
        insp = inspect(engine)
        if "users" not in insp.get_table_names():
            return
        cols = {c["name"] for c in insp.get_columns("users")}
        with engine.begin() as conn:
            if "reset_token" not in cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN reset_token VARCHAR(128)"))
            if "reset_sent_at" not in cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN reset_sent_at DATETIME"))
    except Exception:
        # Non-fatal; create_all will handle fresh installs.
        pass


def init_db() -> None:
    # Import models so SQLAlchemy sees them before create_all.
    from app.models import user_model, wallet_model, game_model, play_model  # noqa: F401
    Base.metadata.create_all(bind=engine)
    _ensure_user_columns()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
