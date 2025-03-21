#!/usr/bin/env python
"""Script to run Alembic migration upgrade for SQLite database."""
import os
import sys
import subprocess
from pathlib import Path

# Add the current directory to the Python path for app imports
sys.path.append(os.getcwd())

def check_alembic_installation():
    """Check if alembic is properly installed."""
    print("Checking Alembic installation...")
    
    # Check if alembic CLI is available
    try:
        result = subprocess.run(
            ["alembic", "--version"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            print(f"Alembic CLI installed: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("Alembic is not installed. Installing it now...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "alembic", "sqlalchemy"])
        print("Alembic installed successfully!")
        return True
    except Exception as e:
        print(f"Error installing Alembic: {e}")
        return False

def setup_database_url():
    """Ensure database URL is set appropriately for SQLite."""
    # Check if URL is already set in environment
    database_url = os.getenv("SQLALCHEMY_DATABASE_URI")
    
    if not database_url:
        # Default to SQLite
        sqlite_path = os.getenv("SQLITE_PATH", "kalina_news.db")
        database_url = f"sqlite:///{sqlite_path}"
        os.environ["SQLALCHEMY_DATABASE_URI"] = database_url
    
    print(f"Using database: {database_url}")
    return database_url

def check_if_initialized():
    """Check if the database is initialized with Alembic."""
    import sqlite3
    
    # Get database path from environment or use default
    sqlite_path = os.getenv("SQLITE_PATH", "kalina_news.db")
    
    # Check if database file exists
    if not os.path.exists(sqlite_path):
        print(f"Database file does not exist at: {sqlite_path}")
        return False
        
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        
        # Check if alembic_version table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'")
        result = cursor.fetchone()
        
        # Close connection
        conn.close()
        
        # Return True if alembic_version table exists
        return result is not None
    except Exception as e:
        print(f"Error checking database state: {e}")
        return False

def initialize_alembic():
    """Initialize Alembic for an existing database."""
    print("Initializing Alembic for the existing database...")
    
    # Stamp the database with the current head
    command = f"{sys.executable} -m alembic stamp head"
    result = subprocess.run(
        command,
        shell=True,
        env=dict(os.environ, PYTHONPATH=os.getcwd()),
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Database successfully initialized for migrations!")
        print(result.stdout)
        return True
    else:
        print(f"❌ Failed to initialize database for migrations: {result.stderr}")
        return False

def run_migration():
    """Run the migration upgrade using Alembic."""
    # Set up database URL
    setup_database_url()
    
    # Check if Alembic is initialized
    if not check_if_initialized():
        print("Alembic is not initialized in this database.")
        choice = input("Do you want to initialize Alembic for the existing database? (Y/n): ").lower()
        
        if choice != 'n':
            if not initialize_alembic():
                print("Failed to initialize Alembic.")
                return False
        else:
            print("Aborting migration.")
            return False
    
    # Run alembic upgrade
    python_path = sys.executable
    command = f"{python_path} -m alembic upgrade head"
    
    print(f"Running migration command: {command}")
    result = subprocess.run(
        command,
        shell=True,
        env=dict(os.environ, PYTHONPATH=os.getcwd()),
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Database has been upgraded successfully!")
        print(result.stdout)
        return True
    else:
        print(f"❌ Failed to apply migrations: {result.stderr}")
        return False

def main():
    """Main function."""
    print("Running Alembic migrations for Kalina News (SQLite)...\n")
    
    # Check if Alembic is installed
    if not check_alembic_installation():
        print("Failed to verify Alembic installation.")
        sys.exit(1)
    
    # Run migrations
    if not run_migration():
        print("Failed to run migrations.")
        sys.exit(1)
    
    print("\n✨ Migrations completed successfully! ✨")
    print("\nYour database schema is now up to date!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1) 