import os
import sys
from pathlib import Path

# Add project root to sys.path so imports work from any directory
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Use SQLite for local development (can switch to PostgreSQL later)
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / "signup_app.db"
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{DEFAULT_DB_PATH.resolve().as_posix()}",
)

# Base class for models
Base = declarative_base()

# Initialize engine and session
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    pool_pre_ping=True,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    """Initialize database by creating all tables."""
    # Ensure models are imported so SQLAlchemy registers table metadata.
    from database import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    print("✓ Database initialized successfully")

def get_db():
    """Dependency for getting DB session in FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

