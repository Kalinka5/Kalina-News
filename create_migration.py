#!/usr/bin/env python
"""Script to create Alembic migration revision for SQLite database."""
import os
import sys
import subprocess
import shutil
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

def check_if_migrations_exist():
    """Check if migration files exist."""
    versions_dir = os.path.join("alembic_project", "versions")
    
    # Skip __init__.py and __pycache__ directory
    migration_files = [f for f in os.listdir(versions_dir) 
                      if f.endswith('.py') and not f == '__init__.py']
    
    return len(migration_files) > 0

def create_migration(message="New migration"):
    """Create a new migration revision using Alembic."""
    # Set up database URL
    setup_database_url()
    
    # Check if migration files exist
    if not check_if_migrations_exist():
        print("No migration files found. Please run create_first_revision.py first.")
        print("Running: python create_first_revision.py")
        
        result = subprocess.run(
            [sys.executable, "create_first_revision.py"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ Failed to create initial migration: {result.stderr}")
            return False
    
    # Run alembic revision
    python_path = sys.executable
    command = f"{python_path} -m alembic revision --autogenerate -m \"{message}\""
    
    print(f"Running migration creation command: {command}")
    result = subprocess.run(
        command,
        shell=True,
        env=dict(os.environ, PYTHONPATH=os.getcwd()),
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Migration file created successfully!")
        print(result.stdout)
        return True
    else:
        print(f"❌ Failed to create migration: {result.stderr}")
        
        if "Target database is not up to date" in result.stderr:
            print("\n❗ Your database schema doesn't match the previous migrations.")
            print("❗ You need to run migrations first with 'python run_migration.py'")
            
            choice = input("Would you like to run migrations now? (y/N): ").lower()
            if choice == 'y':
                print("Running migrations...")
                run_result = subprocess.run(
                    [sys.executable, "run_migration.py"],
                    capture_output=True,
                    text=True
                )
                
                if run_result.returncode == 0:
                    print("Migrations applied successfully. Trying to create migration again...")
                    return create_migration(message)
        
        return False

def get_migration_message():
    """Get migration message from user."""
    default_message = "New migration"
    user_message = input(f"Enter migration message [{default_message}]: ")
    return user_message.strip() if user_message.strip() else default_message

def main():
    """Main function."""
    print("Creating Alembic migration for Kalina News (SQLite)...\n")
    
    # Check if Alembic is installed
    if not check_alembic_installation():
        print("Failed to verify Alembic installation.")
        sys.exit(1)
    
    # Get migration message
    message = get_migration_message()
    
    # Create migration
    if not create_migration(message):
        print("Failed to create migration.")
        sys.exit(1)
    
    print("\n✨ Migration creation completed successfully! ✨")
    print("\nNext steps:")
    print("1. Review the generated migration file in alembic_project/versions/")
    print("2. Run migrations with 'python run_migration.py'")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1) 