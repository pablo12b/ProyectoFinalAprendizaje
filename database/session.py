"""
Session Factory for Business Backend.

Provides async session management using SQLAlchemy 2.0.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from business_backend.database.connection import get_engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """
    Get async session factory.

    Returns:
        async_sessionmaker configured for the engine
    """
    engine = get_engine()
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager for database sessions.

    Usage:
        async with get_session() as session:
            result = await session.execute(query)

    Yields:
        AsyncSession instance
    """
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
