# Kalina News

A modern news platform built with FastAPI and SQLite.

## Features

- User authentication with JWT
- News article management
- Categories and tags
- Comments system
- API documentation with Swagger UI

## Prerequisites

- Python 3.8+
- SQLite (included in Python standard library)
- Redis (optional, for caching)

## Installation

### 1. Quick setup (recommended)

```bash
python setup.py
```

This will guide you through the setup process, including installing dependencies and creating a `.env` file.

### 2. Manual setup

```bash
# Clone the repository
git clone https://github.com/yourusername/kalina-news.git
cd kalina-news

# Install dependencies
pip install -r requirements.txt

# Create a .env file
cp .env.example .env
```

## Database Setup

### 1. SQLite Setup

SQLite is a file-based database that comes included with Python, so there's no separate database server to install or configure.

The default database file is `kalina_news.db` in the project root directory. You can change this by editing the `SQLITE_PATH` in your `.env` file:

```
SQLITE_PATH=kalina_news.db
SQLALCHEMY_DATABASE_URI=sqlite:///kalina_news.db
```

Make sure the path is writable by your application.

### 2. Application Database Setup

You can set up the application database using one of the following methods:

```bash
# Option 1: Setup with migrations (recommended)
make db-setup

# Option 2: Direct setup without migrations
make db-direct
```

Or run the setup scripts directly:

```bash
# Using migrations (alembic)
python db_setup.py

# Direct setup (without alembic)
python direct_db_setup.py
```

## Development

```bash
# Run the application
make run

# Create a new migration
make revision

# Apply migrations
make migrate

# Run tests
make test

# View all available commands
make help
```

## Docker Setup

You can also run the application using Docker:

```bash
# Build and start the containers
docker-compose up -d

# Stop the containers
docker-compose down
```

The SQLite database will be stored in a Docker volume for persistence.

## API Documentation

Once the application is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
