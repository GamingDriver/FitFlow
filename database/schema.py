"""
Database schema and initialization helpers
"""

from database.config import Base, engine
from database.models import User

def create_all_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully")

def drop_all_tables():
    """Drop all tables (use with caution!)"""
    Base.metadata.drop_all(bind=engine)
    print("All tables dropped")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "reset":
        print("Resetting database...")
        drop_all_tables()
        create_all_tables()
        print("Database reset complete")
    else:
        create_all_tables()
