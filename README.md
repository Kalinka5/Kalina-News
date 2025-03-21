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

## Understanding the Migration System

The Kalina News project uses Alembic with SQLite to manage database schema changes. The migration system consists of three primary scripts:

1. create_first_revision.py - Creates the initial empty migration (run only once)
2. create_migration.py - Creates new migrations when you change your models
3. run_migration.py - Applies pending migrations to update your database

## Initial Setup (First Time Only)

If you haven't set up migrations yet, follow these steps:

1. Create the initial revision:

`python create_first_revision.py`

This creates an empty migration and stamps your database as "up to date" with the current schema.

2. Verify setup:

`sqlite3 kalina_news.db ".tables"`

You should see an alembic_version table among others.

## Creating New Migrations

When you make changes to your SQLAlchemy models in the app/models/ directory, you need to create a migration to update the database schema:

1. Make changes to your models - Edit your model files in app/models/
2. Create a migration:
   `python create_migration.py`
3. Enter a descriptive message when prompted (e.g., "Add user profile fields" or "Create new comment table")
4. Check the generated migration file in the alembic_project/versions/ directory to make sure it correctly captures your changes

## Running Migrations

After creating a migration, you need to apply it to update your database:

1. Run the migration:
   `python run_migration.py`
2. Verify changes:
   `sqlite3 kalina_news.db ".schema table_name"`

Replace table_name with the name of the table you modified.

## Common Issues and Solutions

### If "Target database is not up to date" Error Occurs:

This usually means the database schema doesn't match what Alembic expects. You have two options:

1. Run migrations first:
   `python run_migration.py`
   Then try creating a migration again.

2. Reinitialize migrations (if the database is empty or can be reset):

- Delete the alembic_version table:
  `sqlite3 kalina_news.db "DROP TABLE alembic_version"`
- Run python create_first_revision.py again

### SQLite Limitations

SQLite has some limitations compared to other databases:

- Cannot drop columns
- Limited ability to alter column types
- Cannot rename tables in a single statement
  The migration scripts handle these limitations by creating new tables and copying data when necessary.

## Best Practices

1. Make small, incremental changes to your models
2. Create migrations frequently rather than making many model changes at once
3. Test migrations in a development environment before applying to production
4. Backup your database before running migrations
5. Review generated migration files before applying them
