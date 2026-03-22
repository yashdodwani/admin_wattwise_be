"""
Database configuration and initialization.

This module sets up SQLAlchemy engine and session management.
Update DATABASE_URL with your actual PostgreSQL connection string.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
import os
from dotenv import load_dotenv
from typing import Generator
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

load_dotenv()


def _resolve_database_url() -> str:
    """Resolve DB URL from supported env keys with localhost fallback for dev."""
    db_url = (
        os.getenv("DATABASE_URL")
        or os.getenv("DB_URI")
        or os.getenv("DATABASE_URI")
    )
    if not db_url:
        return "postgresql://admin:password@localhost:5432/wattwise_admin"

    # Heroku-style postgres:// URLs are not accepted by SQLAlchemy 2.x
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    # Neon requires SSL. If omitted, enforce it automatically.
    parsed = urlparse(db_url)
    if parsed.scheme.startswith("postgresql") and ("neon.tech" in (parsed.hostname or "")):
        q = dict(parse_qsl(parsed.query, keep_blank_values=True))
        if "sslmode" not in q:
            q["sslmode"] = "require"
            db_url = urlunparse(parsed._replace(query=urlencode(q)))

    return str(db_url)


# Database URL from environment or fallback for local development
DATABASE_URL = _resolve_database_url()

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    pool_pre_ping=True,  # Verify connection before use
    pool_size=10,
    max_overflow=20
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Define Base for SQLAlchemy models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session for FastAPI routes.

    Yields:
        Session: Database session

    Example:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.

    Imports every model so SQLAlchemy registers them with the shared
    Base before calling create_all().
    """
    # Import all models to register them with Base.metadata
    import models.admin       # noqa: F401
    import models.user        # noqa: F401
    import models.complaint   # noqa: F401
    import models.transaction # noqa: F401
    import models.sms         # noqa: F401
    import models.settings    # noqa: F401
    import models.reference_data  # noqa: F401
    import models.notification # noqa: F401

    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")


def drop_db():
    """
    Drop all database tables.

    WARNING: This will delete all data. Use only for development/testing.
    """
    import models.admin       # noqa: F401
    import models.user        # noqa: F401
    import models.complaint   # noqa: F401
    import models.transaction # noqa: F401
    import models.sms         # noqa: F401
    import models.settings    # noqa: F401
    import models.reference_data  # noqa: F401
    import models.notification # noqa: F401

    Base.metadata.drop_all(bind=engine)
    print("✓ All database tables dropped")


if __name__ == "__main__":
    # Initialize database when run directly
    init_db()
