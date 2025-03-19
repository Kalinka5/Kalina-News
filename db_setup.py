#!/usr/bin/env python
"""
Database setup script for Kalina News.
This script runs alembic migrations directly using subprocess.
"""
import os
import sys
import subprocess
import importlib.util
import importlib
from pathlib import Path

# Add the current directory to the Python path for importing app modules
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Check if alembic is installed, and install it if not
# Important: Don't import alembic directly since it might import local directory
alembic_config = None
alembic_command = None

def check_alembic_installation():
    """Check if the real alembic package is installed correctly."""
    global alembic_config, alembic_command
    
    print("Checking Alembic installation...")
    
    # First, check if alembic exists in site-packages
    try:
        # Get the site-packages path
        import site
        site_packages = site.getsitepackages()[0]
        alembic_path = os.path.join(site_packages, 'alembic')
        
        if os.path.exists(alembic_path):
            print(f"Found Alembic at: {alembic_path}")
            
            # Manually import modules to avoid accidental local import
            alembic_spec = importlib.util.spec_from_file_location(
                "alembic", 
                os.path.join(alembic_path, "__init__.py")
            )
            alembic = importlib.util.module_from_spec(alembic_spec)
            alembic_spec.loader.exec_module(alembic)
            
            config_spec = importlib.util.spec_from_file_location(
                "alembic.config", 
                os.path.join(alembic_path, "config.py")
            )
            config = importlib.util.module_from_spec(config_spec)
            config_spec.loader.exec_module(config)
            
            command_spec = importlib.util.spec_from_file_location(
                "alembic.command", 
                os.path.join(alembic_path, "command.py")
            )
            command = importlib.util.module_from_spec(command_spec)
            command_spec.loader.exec_module(command)
            
            alembic_config = config.Config
            alembic_command = command
            
            print("✅ Alembic modules imported successfully!")
            return True
    except Exception as e:
        print(f"Error when attempting to manually import Alembic: {e}")
    
    # If direct import failed, try installing
    print("⚠️ Could not import Alembic modules. Attempting to install...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--force-reinstall", "alembic"])
        print("✅ Alembic reinstalled successfully!")
        
        # Try importing again
        result = subprocess.run(
            [sys.executable, "-c", "import alembic.config, alembic.command; print('Import successful')"],
            capture_output=True, 
            text=True
        )
        
        if "Import successful" in result.stdout:
            print("✅ Verified Alembic can be imported after installation!")
            return True
        else:
            print(f"❌ Still cannot import Alembic after installation.")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Failed to install Alembic: {e}")
        print("Please run 'pip install --force-reinstall alembic' manually and try again.")
        return False

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"Running: {description}...")
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        return False

def create_migration_with_command():
    """Create migration using subprocess."""
    # Use full path to python to avoid any confusion
    python_path = sys.executable
    command = f"{python_path} -m alembic revision --autogenerate -m \"Initial migration\""
    
    print(f"Running migration command: {command}")
    result = subprocess.run(
        command,
        shell=True,
        env=dict(os.environ, PYTHONPATH=os.getcwd()),
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Migration created successfully!")
        return True
    else:
        print(f"❌ Failed to create migration: {result.stderr}")
        return False

def apply_migrations_with_command():
    """Apply migrations using subprocess."""
    # Use full path to python to avoid any confusion
    python_path = sys.executable
    command = f"{python_path} -m alembic upgrade head"
    
    print(f"Running upgrade command: {command}")
    result = subprocess.run(
        command,
        shell=True,
        env=dict(os.environ, PYTHONPATH=os.getcwd()),
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Migrations applied successfully!")
        return True
    else:
        print(f"❌ Failed to apply migrations: {result.stderr}")
        return False

def setup_database():
    """Set up the database using Alembic migrations."""
    # Get database settings from environment or user input
    sqlalchemy_database_uri = os.getenv("SQLALCHEMY_DATABASE_URI")
    
    if not sqlalchemy_database_uri:
        # Using SQLite instead of PostgreSQL
        sqlite_path = os.getenv("SQLITE_PATH", "kalina_news.db")
        sqlalchemy_database_uri = f"sqlite:///{sqlite_path}"
        
        # Set the environment variable for the migration
        os.environ["SQLALCHEMY_DATABASE_URI"] = sqlalchemy_database_uri
    
    # Apply migrations
    print(f"\nUsing database: {sqlalchemy_database_uri}")
    
    create_migration = input("Create a new migration before applying? (y/N): ").lower() == "y"
    if create_migration:
        # Create migration using subprocess
        if not create_migration_with_command():
            print("⚠️ Failed to create migration.")
            return False
    
    # Apply migrations using subprocess
    if not apply_migrations_with_command():
        print("⚠️ Failed to apply migrations.")
        return False
    
    return True

def main():
    """Main function."""
    print("Setting up the Kalina News database...\n")
    
    # Check for the alembic installation first
    if not check_alembic_installation():
        print("\n⚠️ Alembic installation check failed. Please fix Alembic installation and try again.")
        sys.exit(1)
    
    if setup_database():
        print("\n✨ Database setup completed successfully! ✨")
    else:
        print("\n⚠️ Database setup failed. Please check the error messages above.")
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