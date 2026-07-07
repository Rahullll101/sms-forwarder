"""
Database Connection Manager

Responsible only for:

- Creating the PostgreSQL connection pool
- Providing database connections
- Closing the pool during shutdown
"""

from psycopg_pool import ConnectionPool

from app.config import settings


DATABASE_URL = (
    f"host={settings.database_host} "
    f"port={settings.database_port} "
    f"dbname={settings.database_name} "
    f"user={settings.database_user} "
    f"password={settings.database_password}"
)


pool = ConnectionPool(
    conninfo=DATABASE_URL,
    min_size=1,
    max_size=10,
    open=False,
)


def initialize_database() -> None:
    """
    Opens the connection pool.
    """
    pool.open()


def close_database() -> None:
    """
    Closes the connection pool.
    """
    pool.close()


def get_connection():
    """
    Returns a pooled PostgreSQL connection.

    Usage:

        with get_connection() as conn:
            ...
    """
    return pool.connection()