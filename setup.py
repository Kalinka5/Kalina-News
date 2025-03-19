#!/usr/bin/env python3
"""
Setup script for Kalina News project.
This script guides users through the installation process, including:
- Installing dependencies
- Creating a .env file
- Setting up SQLite
- Creating database tables
"""

import os
import sys
import subprocess
import shutil
from getpass import getpass
import platform

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)

def print_step(step, text):
    """Print a step in the setup process."""
    print(f"\n[{step}] {text}")

def run_command(command, check=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        return None

def check_python_version():
    """Check if Python version is compatible."""
    print_step(1, "Checking Python version")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ is required, but you have {version.major}.{version.minor}")
        print("Please upgrade your Python version and try again.")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_dependencies():
    """Install project dependencies."""
    print_step(2, "Installing dependencies")
    
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found")
        return False
    
    print("Installing Python dependencies...")
    result = run_command("pip install -r requirements.txt")
    
    if result and result.returncode == 0:
        print("✅ Dependencies installed successfully")
        return True
    else:
        print("❌ Failed to install dependencies")
        print(result.stderr if result else "Unknown error")
        return False

def create_env_file():
    """Create a .env file if it doesn't exist."""
    print_step(3, "Setting up environment variables")
    
    if os.path.exists(".env"):
        overwrite = input(".env file already exists. Overwrite? (y/N): ").lower() == 'y'
        if not overwrite:
            print("Keeping existing .env file")
            return True
    
    if os.path.exists(".env.example"):
        shutil.copy(".env.example", ".env")
        print("✅ Created .env file from .env.example")
        
        # Ask for customization
        customize = input("Would you like to customize the .env file now? (y/N): ").lower() == 'y'
        if customize:
            # Database settings
            db_user = input("PostgreSQL username [postgres]: ") or "postgres"
            db_password = getpass("PostgreSQL password [postgres]: ") or "postgres"
            db_name = input("PostgreSQL database name [kalina_news]: ") or "kalina_news"
            db_host = input("PostgreSQL host [localhost]: ") or "localhost"
            
            # Update .env file
            with open(".env", "r") as f:
                env_content = f.read()
            
            env_content = env_content.replace("POSTGRES_USER=postgres", f"POSTGRES_USER={db_user}")
            env_content = env_content.replace("POSTGRES_PASSWORD=postgres", f"POSTGRES_PASSWORD={db_password}")
            env_content = env_content.replace("POSTGRES_DB=kalina_news", f"POSTGRES_DB={db_name}")
            env_content = env_content.replace("POSTGRES_SERVER=localhost", f"POSTGRES_SERVER={db_host}")
            
            # Update the direct database URL as well
            db_url = f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}"
            env_content = env_content.replace(
                "SQLALCHEMY_DATABASE_URI=postgresql://postgres:postgres@localhost/kalina_news", 
                f"SQLALCHEMY_DATABASE_URI={db_url}"
            )
            
            with open(".env", "w") as f:
                f.write(env_content)
            
            print("✅ Updated .env file with your settings")
        
        return True
    else:
        print("❌ .env.example not found")
        print("Creating a basic .env file...")
        
        with open(".env", "w") as f:
            f.write("""# API Configuration
SECRET_KEY=your-secret-key-for-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
# 1 week

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Database Configuration
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=kalina_news
# You can use this direct database URL if you have connection issues
SQLALCHEMY_DATABASE_URI=postgresql://postgres:postgres@localhost/kalina_news

# Redis Configuration (for caching)
REDIS_HOST=localhost
REDIS_PORT=6379
""")
        print("✅ Created a basic .env file")
        return True

def check_sqlite():
    """Check if SQLite is available and set up the database path."""
    print_step(3, "Setting up SQLite")
    
    # Check if sqlite3 is installed
    result = run_command("sqlite3 --version", check=False)
    
    if result and result.returncode == 0:
        print(f"✅ SQLite is installed: {result.stdout.strip()}")
    else:
        print("⚠️ SQLite command-line tool might not be installed, but this is not critical.")
        print("   The Python sqlite3 module will be used, which is included in standard Python.")
    
    # Get the SQLite path from environment or use default
    sqlite_path = os.getenv("SQLITE_PATH", "kalina_news.db")
    
    # Ask user if they want to keep or change the path
    print(f"\nCurrent SQLite database path: {sqlite_path}")
    change_path = input("Would you like to change the database path? (y/N): ").lower() == 'y'
    
    if change_path:
        new_path = input(f"Enter new SQLite database path [default: {sqlite_path}]: ").strip()
        if new_path:
            sqlite_path = new_path
    
    # Update .env file with the SQLite path
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            env_content = f.read()
        
        # Update SQLITE_PATH
        if "SQLITE_PATH=" in env_content:
            env_content = '\n'.join([
                line if not line.startswith("SQLITE_PATH=") else f"SQLITE_PATH={sqlite_path}"
                for line in env_content.split('\n')
            ])
        else:
            # Find the database section and add SQLITE_PATH
            lines = env_content.split('\n')
            db_section_index = -1
            for i, line in enumerate(lines):
                if "# Database Configuration" in line:
                    db_section_index = i
                    break
            
            if db_section_index >= 0:
                lines.insert(db_section_index + 1, f"SQLITE_PATH={sqlite_path}")
                env_content = '\n'.join(lines)
            else:
                env_content += f"\n# Database Configuration\nSQLITE_PATH={sqlite_path}\n"
        
        # Update SQLALCHEMY_DATABASE_URI
        sqlite_uri = f"sqlite:///{sqlite_path}"
        if "SQLALCHEMY_DATABASE_URI=" in env_content:
            env_content = '\n'.join([
                line if not line.startswith("SQLALCHEMY_DATABASE_URI=") else f"SQLALCHEMY_DATABASE_URI={sqlite_uri}"
                for line in env_content.split('\n')
            ])
        else:
            env_content += f"SQLALCHEMY_DATABASE_URI={sqlite_uri}\n"
        
        # Write updated content back to .env
        with open(env_file, "w") as f:
            f.write(env_content)
    
    print(f"✅ SQLite configuration updated. Database path: {sqlite_path}")
    return True

def setup_database():
    """Set up the database by creating tables."""
    print_step(4, "Setting up database tables")
    
    # Check if the direct_db_setup.py script exists
    if os.path.exists("direct_db_setup.py"):
        print("Using direct_db_setup.py to create tables...")
        result = run_command("python3 direct_db_setup.py")
        
        if result and result.returncode == 0:
            print("✅ Database tables created successfully!")
            return True
        else:
            print("❌ Failed to create database tables.")
            return False
    
    # Try using db_setup.py as fallback
    elif os.path.exists("db_setup.py"):
        print("Using db_setup.py to run migrations...")
        result = run_command("python3 db_setup.py")
        
        if result and result.returncode == 0:
            print("✅ Database migrations applied successfully!")
            return True
        else:
            print("❌ Failed to apply database migrations.")
            return False
    
    else:
        print("❌ Could not find database setup scripts (direct_db_setup.py or db_setup.py).")
        return False

def main():
    """Main setup function."""
    print_header("Kalina News Project Setup")
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install dependencies
    if not install_dependencies():
        return
    
    # Create .env file
    if not create_env_file():
        return
    
    # Check SQLite setup
    if not check_sqlite():
        return
    
    # Set up database
    if not setup_database():
        return
    
    print_header("Setup Completed Successfully!")
    print("You can now start the application with:")
    print("  $ uvicorn app.main:app --reload")
    print("\nAccess the API documentation at:")
    print("  http://localhost:8000/docs")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user. You can run this script again anytime.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nAn unexpected error occurred: {e}")
        sys.exit(1) 