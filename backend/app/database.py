"""Database configuration."""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool, StaticPool

Base = declarative_base()
load_dotenv()


def _make_engine():
    url = os.getenv(
        "DATABASE_URL",
        "postgresql://krishix_user:krishix_password@postgres:5432/krishix_db",
    )
    if url.startswith("sqlite"):
        # SQLite: used in unit tests only
        return create_engine(
            url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    return create_engine(url, poolclass=NullPool, echo=False)


engine = _make_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
