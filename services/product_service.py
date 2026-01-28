"""
Product Service for Business Backend.

Provides CRUD operations for ProductStock using SQLAlchemy ORM.
"""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from business_backend.database.models import ProductStock


class ProductService:
    """Service for product stock operations."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        """
        Initialize ProductService.

        Args:
            session_factory: Async session factory for database operations
        """
        self.session_factory = session_factory

    async def list_products(
        self,
        limit: int = 50,
        offset: int = 0,
        active_only: bool = True,
    ) -> list[ProductStock]:
        """
        List products with pagination.

        Args:
            limit: Maximum number of products to return
            offset: Number of products to skip
            active_only: If True, only return active products

        Returns:
            List of ProductStock instances
        """
        async with self.session_factory() as session:
            query = select(ProductStock)

            if active_only:
                query = query.where(ProductStock.is_active == True)  # noqa: E712

            query = query.order_by(ProductStock.product_name).limit(limit).offset(offset)

            result = await session.execute(query)
            return list(result.scalars().all())

    async def get_product(self, product_id: UUID) -> ProductStock | None:
        """
        Get a single product by ID.

        Args:
            product_id: UUID of the product

        Returns:
            ProductStock instance or None if not found
        """
        async with self.session_factory() as session:
            query = select(ProductStock).where(ProductStock.id == product_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def search_by_name(
        self,
        name: str,
        limit: int = 20,
        active_only: bool = True,
    ) -> list[ProductStock]:
        """
        Search products by name (case-insensitive).

        Args:
            name: Search term for product name
            limit: Maximum number of results
            active_only: If True, only return active products

        Returns:
            List of matching ProductStock instances
        """
        async with self.session_factory() as session:
            query = select(ProductStock).where(
                ProductStock.product_name.ilike(f"%{name}%")
            )

            if active_only:
                query = query.where(ProductStock.is_active == True)  # noqa: E712

            query = query.order_by(ProductStock.product_name).limit(limit)

            result = await session.execute(query)
            return list(result.scalars().all())

    async def get_low_stock_products(self, limit: int = 50) -> list[ProductStock]:
        """
        Get products with stock below reorder point.

        Args:
            limit: Maximum number of results

        Returns:
            List of ProductStock instances with low stock
        """
        async with self.session_factory() as session:
            query = (
                select(ProductStock)
                .where(ProductStock.is_active == True)  # noqa: E712
                .where(ProductStock.quantity_available <= ProductStock.reorder_point)
                .order_by(ProductStock.quantity_available)
                .limit(limit)
            )

            result = await session.execute(query)
            return list(result.scalars().all())

    async def count_products(self, active_only: bool = True) -> int:
        """
        Count total products.

        Args:
            active_only: If True, only count active products

        Returns:
            Total count of products
        """
        async with self.session_factory() as session:
            query = select(func.count(ProductStock.id))

            if active_only:
                query = query.where(ProductStock.is_active == True)  # noqa: E712

            result = await session.execute(query)
            return result.scalar_one()
