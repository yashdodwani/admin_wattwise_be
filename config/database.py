"""
Database configuration and initialization.

This module sets up SQLAlchemy engine and session management.
Update DATABASE_URL with your actual PostgreSQL connection string.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv
from typing import Generator

load_dotenv()

# Database URL from environment or use default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://admin:password@localhost:5432/wattwise_admin"
)
print(DATABASE_URL)
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

    This function creates all tables defined in SQLAlchemy models.
    Call this once during application startup.

    Example:
        if __name__ == "__main__":
            init_db()
            print("Database initialized successfully")
    """
    try:
        # Try relative import first (when imported as a module)
        from ..models.admin import Base
    except ImportError:
        # Fallback to absolute import (when run directly)
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from models.admin import Base

    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")


def drop_db():
    """
    Drop all database tables.

    WARNING: This will delete all data. Use only for development/testing.
    """
    try:
        # Try relative import first (when imported as a module)
        from ..models.admin import Base
    except ImportError:
        # Fallback to absolute import (when run directly)
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from models.admin import Base

    Base.metadata.drop_all(bind=engine)
    print("✓ All database tables dropped")


if __name__ == "__main__":
    # Initialize database when run directly
    init_db()

