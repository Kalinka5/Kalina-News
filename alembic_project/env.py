from logging.config import fileConfig
import os
import sys
from pathlib import Path

# Add the project root directory to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from app.db.base import Base
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# Get database URL from environment if available
def get_url():
    # Use environment variable if defined
    database_url = os.getenv("SQLALCHEMY_DATABASE_URI")
    if database_url:
        return database_url
        
    # Otherwise use SQLite
    sqlite_path = os.getenv("SQLITE_PATH", "kalina_news.db")
    return f"sqlite:///{sqlite_path}"

# Override sqlalchemy.url with environment variable if it exists
db_url = get_url()
config.set_main_option("sqlalchemy.url", db_url)

# Configure SQLite to use the correct migration approach
def process_revision_directives(context, revision, directives):
    # SQLite doesn't support ALTER TABLE for column changes
    if directives and config.get_main_option("sqlalchemy.url").startswith("sqlite"):
        from alembic.operations import ops
        
        # Handle both single directive and list of directives
        directive_list = directives if isinstance(directives, list) else [directives]
        
        for directive in directive_list:
            # Check if the directive has an 'ops' attribute (like UpgradeOps objects)
            if hasattr(directive, 'ops'):
                for operation in directive.ops:
                    # Skip unsupported ALTER operations in SQLite
                    if isinstance(operation, ops.AlterColumnOp):
                        operation.kw['existing_nullable'] = True

def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        process_revision_directives=process_revision_directives
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 