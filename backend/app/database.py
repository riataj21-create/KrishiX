"""Database configuration.

The engine is created lazily so tests can override DATABASE_URL via
environment variable before any app module is imported.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool, StaticPool

Base = declarative_base()

_engine = None
_SessionLocal = None


def _get_engine():
    global _engine
    if _engine is None:
        url = os.environ.get(
            "DATABASE_URL",
            "postgresql://krishix_user:krishix_password@postgres:5432/krishix_db",
        )
        if url.startswith("sqlite"):
            _engine = create_engine(
                url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
        else:
            _engine = create_engine(url, poolclass=NullPool, echo=False)
    return _engine


def _get_session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_get_engine())
    return _SessionLocal


# Backwards-compatible module-level names used throughout the app.
# These are properties-by-convention: code that does `from app.database import engine`
# gets the object once; code that calls get_db() always gets the right session.
class _LazyEngine:
    """Proxy that forwards all attribute access to the real engine (created lazily)."""
    def __getattr__(self, name):
        return getattr(_get_engine(), name)

    def __repr__(self):
        return repr(_get_engine())


engine = _LazyEngine()


def get_db():
    factory = _get_session_factory()
    db = factory()
    try:
        yield db
    finally:
        db.close()
