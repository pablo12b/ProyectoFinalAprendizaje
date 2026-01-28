"""
Database Connection for Business Backend.

Single-tenant async engine using SQLAlchemy 2.0.
"""

import functools

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine as sa_create_async_engine
from sqlalchemy.pool import NullPool

from business_backend.config import get_business_settings


def create_async_engine(database_url: str) -> AsyncEngine:
    """
    Create async SQLAlchemy engine.

    Args:
        database_url: PostgreSQL connection URL

    Returns:
        AsyncEngine instance
    """
    return sa_create_async_engine(
        database_url,
        poolclass=NullPool,  # Recommended for async
        echo=False,
    )


@functools.cache
def get_engine() -> AsyncEngine:
    """
    Get cached async engine using settings.

    Returns:
        Cached AsyncEngine instance
    """
    settings = get_business_settings()
    return create_async_engine(str(settings.pg_url))
