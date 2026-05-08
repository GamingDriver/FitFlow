import os
import sys
from pathlib import Path

# Add project root to sys.path so imports work from any directory
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import create_engine, text
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

def ensure_sqlite_migrations():
    """Add missing SQLite columns for older database file versions."""
    if "sqlite" not in DATABASE_URL:
        return

    with engine.begin() as conn:
        result = conn.execute(text("PRAGMA table_info(workouts)"))
        columns = {row[1]: row for row in result}
        if "exercises_text" not in columns:
            conn.execute(text("ALTER TABLE workouts ADD COLUMN exercises_text TEXT"))
        if "exercises" in columns and columns["exercises"][3] == 1:  # nullable=0 means NOT NULL
            # For SQLite, recreate table to make exercises nullable
            workout_count = conn.execute(text("SELECT COUNT(*) FROM workouts")).scalar()
            if workout_count == 0:
                # Safe to recreate if no data
                conn.execute(text("DROP TABLE workouts"))
                conn.execute(text("""
                    CREATE TABLE workouts (
                        id VARCHAR(36) PRIMARY KEY,
                        user_id VARCHAR(36) NOT NULL REFERENCES users(id),
                        title VARCHAR(255) NOT NULL,
                        description TEXT,
                        exercises TEXT,
                        exercises_text TEXT,
                        created_at DATETIME NOT NULL
                    )
                """))
            else:
                # If there is data, just make exercises nullable by updating the schema
                # This is a simplified approach - in production, use proper migrations
                pass


def init_database():
    """Initialize database by creating all tables."""
    # Ensure models are imported so SQLAlchemy registers table metadata.
    from database import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    ensure_sqlite_migrations()
    print("Database initialized successfully")

def get_db():
    """Dependency for getting DB session in FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

