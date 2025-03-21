#!/usr/bin/env python
"""
Script to create the first Alembic revision for SQLite database without comparing models.
This creates an empty revision that will serve as a starting point for future migrations.
"""
import os
import sys
import subprocess
from pathlib import Path

# Add the current directory to the Python path for app imports
sys.path.append(os.getcwd())

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

def create_empty_revision():
    """Create an empty initial revision without auto-generation."""
    print("Creating empty initial revision...")
    
    # First, check if there are any migrations
    versions_dir = os.path.join("alembic_project", "versions")
    migration_files = [f for f in os.listdir(versions_dir) 
                      if f.endswith('.py') and not f == '__init__.py']
    
    if migration_files:
        print("Migration files already exist:")
        for f in migration_files:
            print(f"  - {f}")
        
        response = input("Continue anyway? This will create a new revision. (y/N): ").lower()
        if response != 'y':
            print("Operation cancelled.")
            return False
    
    # Set up database URL
    setup_database_url()
    
    # Create an empty revision
    python_path = sys.executable
    command = f"{python_path} -m alembic revision -m \"Initial empty revision\""
    
    print(f"Running command: {command}")
    result = subprocess.run(
        command,
        shell=True,
        env=dict(os.environ, PYTHONPATH=os.getcwd()),
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Empty initial revision created successfully!")
        print(result.stdout)
        
        # Stamp the database with this revision
        command = f"{python_path} -m alembic stamp head"
        stamp_result = subprocess.run(
            command,
            shell=True,
            env=dict(os.environ, PYTHONPATH=os.getcwd()),
            capture_output=True,
            text=True
        )
        
        if stamp_result.returncode == 0:
            print("✅ Database stamped with initial revision!")
            return True
        else:
            print(f"❌ Failed to stamp database: {stamp_result.stderr}")
            return False
    else:
        print(f"❌ Failed to create initial revision: {result.stderr}")
        return False

def main():
    """Main function."""
    print("Creating first Alembic revision for SQLite database...\n")
    
    if create_empty_revision():
        print("\n✨ Initial revision created successfully! ✨")
        print("\nYou can now:")
        print("1. Make changes to your SQLAlchemy models")
        print("2. Run 'python create_migration.py' to create a migration for those changes")
        print("3. Run 'python run_migration.py' to apply the migrations")
    else:
        print("\n❌ Failed to create initial revision.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1) 