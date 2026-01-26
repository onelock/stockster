"""
SQL-only Alembic environment configuration.
No ORM, no metadata, just pure SQL migrations with proper locking.
"""
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool, text

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_url():
    """Get database URL from environment or config."""
    return os.getenv(
        "DATABASE_URL",
        config.get_main_option("sqlalchemy.url")
    )


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        transaction_per_migration=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Creates an Engine and associates a connection with the context.
    Uses advisory locks to prevent concurrent migrations.
    """
    # Override URL from environment if provided
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        isolation_level="AUTOCOMMIT",  # Required for advisory locks
    )

    with connectable.connect() as connection:
        # Acquire PostgreSQL advisory lock to prevent concurrent migrations
        # Lock ID: 123456789 (arbitrary unique number for this app)
        lock_acquired = connection.execute(
            text("SELECT pg_try_advisory_lock(123456789)")
        ).scalar()
        
        if not lock_acquired:
            print("⚠️  Another migration is currently running. Waiting...")
            connection.execute(text("SELECT pg_advisory_lock(123456789)"))
            print("✅ Lock acquired")
        
        try:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                transaction_per_migration=True,
                compare_type=True,
            )

            with context.begin_transaction():
                context.run_migrations()
        except Exception as e:
            print(f"❌ Migration error: {e}")
            raise
        finally:
            # Always release the lock
            try:
                connection.execute(text("SELECT pg_advisory_unlock(123456789)"))
            except Exception as unlock_err:
                print(f"⚠️  Failed to release lock: {unlock_err}")


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
