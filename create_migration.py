#!/usr/bin/env python
"""Script to create Alembic migration revision."""
import os
import sys
import subprocess
import site
import importlib.util
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
        print("Alembic CLI not found in PATH")
    
    # Check if alembic is installed in site-packages
    try:
        site_packages = site.getsitepackages()[0]
        alembic_path = os.path.join(site_packages, 'alembic')
        
        if os.path.exists(alembic_path):
            print(f"Found Alembic at: {alembic_path}")
            return True
    except Exception as e:
        print(f"Error checking for Alembic in site-packages: {e}")
    
    print("Alembic is not installed. Installing it now...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--force-reinstall", "alembic"])
        print("Alembic installed successfully!")
        return True
    except Exception as e:
        print(f"Error installing Alembic: {e}")
        return False

def create_migration(message="New migration"):
    """Create a new migration revision using Python -m alembic."""
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
        return True
    else:
        print(f"❌ Failed to create migration: {result.stderr}")
        return False

def get_migration_message():
    """Get migration message from user."""
    default_message = "New migration"
    user_message = input(f"Enter migration message [{default_message}]: ")
    return user_message.strip() if user_message.strip() else default_message

def main():
    """Main function."""
    print("Creating Alembic migration for Kalina News...\n")
    
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

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1) 