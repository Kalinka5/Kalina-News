#!/usr/bin/env python3
"""
Direct database setup script without Alembic.
This script creates database tables directly using SQLAlchemy without relying on config settings.
Now configured to use SQLite instead of PostgreSQL.
"""

import os
import sys
from pathlib import Path

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import database components
try:
    from sqlalchemy import create_engine, inspect, text
    from sqlalchemy.exc import OperationalError
except ImportError:
    print("SQLAlchemy not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "sqlalchemy"])
    from sqlalchemy import create_engine, inspect, text
    from sqlalchemy.exc import OperationalError

# Import models from the app
from app.db.base_class import Base
from app.models.user import User
from app.models.article import Article
from app.models.category import Category
from app.models.tag import Tag
from app.models.comment import Comment

def get_db_connection_info():
    """Get database connection info from user input or environment."""
    print("Database Connection Setup")
    
    # Try to get from environment first
    db_path = os.getenv("SQLITE_PATH") or input("SQLite database path [kalina_news.db]: ") or "kalina_news.db"
    
    # Build the connection URL
    connection_url = f"sqlite:///{db_path}"
    
    return connection_url

def create_tables(connection_url):
    """Create database tables directly using the models from app/models."""
    # Create engine
    try:
        engine = create_engine(connection_url)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database connection successful!")
    except OperationalError as e:
        print(f"Error connecting to database: {e}")
        return False
    
    # Check if tables exist
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if existing_tables:
        print(f"Found existing tables: {', '.join(existing_tables)}")
        choice = input("Do you want to drop and recreate all tables? (y/N): ").lower()
        
        if choice == 'y':
            Base.metadata.drop_all(engine)
            print("Tables dropped")
        else:
            print("Keeping existing tables")
            return True
    
    # Create tables using the imported models
    try:
        print("Creating tables...")
        Base.metadata.create_all(engine)
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")
        return False
    
    return True

def main():
    """Main function."""
    print("=== Direct SQLite Database Setup for Kalina News ===")
    
    # Get database connection URL
    db_url = get_db_connection_info()
    print(f"Using database URL: {db_url}")
    
    # Create tables
    if create_tables(db_url):
        print("\n✅ Database setup completed!")
        print(f"Database URL: {db_url}")
    else:
        print("\n❌ Database setup failed.")

if __name__ == "__main__":
    main() 