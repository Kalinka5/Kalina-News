#!/usr/bin/env python3
"""
Direct database setup script for Kalina News.
This script creates all database tables using SQLAlchemy models without using Alembic migrations.
Now configured to use SQLite instead of PostgreSQL.
"""

import os
import sys
import importlib.util
import traceback
from getpass import getpass
from pathlib import Path

# Add the current directory to the system path to make imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try importing SQLAlchemy components - install if missing
try:
    from sqlalchemy import create_engine, inspect
    from sqlalchemy.sql import text
    from sqlalchemy.exc import SQLAlchemyError, OperationalError
    from sqlalchemy.orm import sessionmaker
    
    # Import database models
    from app.db.base_class import Base
    from app.models.user import User
    from app.models.article import Article
    from app.models.category import Category  
    from app.models.tag import Tag
    from app.models.comment import Comment
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please install the required dependencies with: pip install -r requirements.txt")
    sys.exit(1)

def check_sqlite_path(db_path="kalina_news.db"):
    """Check if the SQLite database path is valid."""
    try:
        # Create the directory if it doesn't exist (for directory-based paths)
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            
        # Check if the path is writable
        if os.path.exists(db_path):
            return os.access(db_path, os.W_OK)
        else:
            # Check if the parent directory is writable
            parent_dir = os.path.dirname(db_path) or '.'
            return os.access(parent_dir, os.W_OK)
    except Exception:
        return False

def get_database_url():
    """Get database URL from environment or use default SQLite path."""
    # First check if SQLALCHEMY_DATABASE_URI is set in .env
    database_url = os.getenv("SQLALCHEMY_DATABASE_URI")
    
    # If not, use SQLite
    if not database_url:
        db_path = os.getenv("SQLITE_PATH", "kalina_news.db")
        database_url = f"sqlite:///{db_path}"
    
    return database_url

def print_sqlite_help():
    """Print help instructions for setting up SQLite."""
    print("\n=== SQLite Setup Instructions ===")
    print("It seems there was an issue with SQLite. Here's how to set it up:")
    
    print("\n1. Make sure you have SQLite installed:")
    print("   • It's usually pre-installed on most systems.")
    print("   • On Ubuntu/Debian: sudo apt install sqlite3")
    print("   • On Fedora/CentOS: sudo dnf install sqlite")
    print("   • On Arch/Manjaro: sudo pacman -S sqlite")
    print("   • On macOS with Homebrew: brew install sqlite")
    
    print("\n2. Make sure the application has write permission to the database file location.")
    print("   • Check permission: ls -la kalina_news.db (if it exists)")
    print("   • Change permission if needed: chmod 644 kalina_news.db")
    
    print("\n3. Verify your SQLite settings in .env file:")
    print("   • Add SQLITE_PATH=kalina_news.db or your preferred path")
    
    print("\nAfter completing these steps, run this script again.")

def create_tables():
    """Create all database tables using SQLAlchemy models."""
    database_url = get_database_url()
    db_path = database_url.replace('sqlite:///', '')
    
    # Check if SQLite file location is accessible
    if 'sqlite:///' in database_url and not check_sqlite_path(db_path):
        print(f"\n❌ Cannot access SQLite database at {db_path}.")
        print_sqlite_help()
        return False
    
    print(f"Connecting to database...")
    try:
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
    except OperationalError as e:
        print(f"❌ Error connecting to the database: {e}")
        print("\nPlease check your database configuration:")
        print(f"Database URL: {database_url}")
        print_sqlite_help()
        return False
    
    # Check if tables already exist
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if existing_tables:
        print("Found existing tables in the database:")
        for table in existing_tables:
            print(f"  - {table}")
        
        response = input("\nWould you like to drop and recreate all tables? (y/N): ").lower()
        if response == 'y':
            print("Dropping all tables...")
            Base.metadata.drop_all(bind=engine)
            print("All tables dropped successfully.")
        else:
            print("Keeping existing tables. Operation cancelled.")
            return True
    
    try:
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
        
        # Create a session to test the connection
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        with SessionLocal() as session:
            # Attempt to execute a simple query
            result = session.execute(text("SELECT 1")).scalar()
            if result == 1:
                print("Database connection test successful!")
    except SQLAlchemyError as e:
        print(f"Error creating database tables: {e}")
        return False
    
    return True

def main():
    """Main function to set up the database."""
    print("===== Kalina News Direct Database Setup (SQLite) =====")
    
    success = create_tables()
    
    if success:
        print("\n✅ Database setup completed successfully!")
        print("\nNext steps:")
        print("1. Run the application with: uvicorn app.main:app --reload")
        print("2. Access the API docs at: http://localhost:8000/docs")
    else:
        print("\n❌ Database setup failed. Please check the error messages above.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        traceback.print_exc()
        sys.exit(1) 