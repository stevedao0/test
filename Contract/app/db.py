from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import STORAGE_DIR


DB_PATH = STORAGE_DIR / "app.sqlite3"


def _sqlite_url(path: Path) -> str:
    # Windows-safe absolute path
    return "sqlite:///" + path.resolve().as_posix()


engine = create_engine(
    _sqlite_url(DB_PATH),
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)


@contextmanager
def session_scope() -> Session:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
