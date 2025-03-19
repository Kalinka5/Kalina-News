#!/usr/bin/env python
"""Script to run Alembic migration upgrade."""
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

def run_migration():
    """Run the migration upgrade using Python -m alembic."""
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
        return True
    else:
        print(f"❌ Failed to apply migrations: {result.stderr}")
        return False

def main():
    """Main function."""
    print("Running Alembic migrations for Kalina News...\n")
    
    # Check if Alembic is installed
    if not check_alembic_installation():
        print("Failed to verify Alembic installation.")
        sys.exit(1)
    
    # Run migrations
    if not run_migration():
        print("Failed to run migrations.")
        sys.exit(1)
    
    print("\n✨ Migrations completed successfully! ✨")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1) 