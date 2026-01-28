"""
ProductStock SQLAlchemy Model.

Maps to the existing product_stocks table in the public schema.
"""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Boolean, Date, DateTime, Integer, Numeric, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""

    pass


class ProductStock(Base):
    """
    ProductStock model for inventory management.

    Maps to product_stocks table in public schema.
    """

    __tablename__ = "product_stocks"
    __table_args__ = {"schema": "public"}

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default="now()",
    )
    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default="now()",
    )

    # Product identification
    product_id: Mapped[str] = mapped_column(String(255), nullable=False)
    product_name: Mapped[str] = mapped_column(String(500), nullable=False)
    product_sku: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Supplier information
    supplier_id: Mapped[str] = mapped_column(String(255), nullable=False)
    supplier_name: Mapped[str] = mapped_column(String(500), nullable=False)

    # Stock quantities
    quantity_on_hand: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    quantity_reserved: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    quantity_available: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    # Stock levels
    minimum_stock_level: Mapped[int] = mapped_column(Integer, nullable=False, server_default="10")
    reorder_point: Mapped[int] = mapped_column(Integer, nullable=False, server_default="20")
    optimal_stock_level: Mapped[int] = mapped_column(Integer, nullable=False, server_default="100")
    reorder_quantity: Mapped[int] = mapped_column(Integer, nullable=False, server_default="50")

    # Usage metrics
    average_daily_usage: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        server_default="0.0",
    )

    # Dates
    last_order_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_stock_count_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiration_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Cost information
    unit_cost: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        server_default="0.0",
    )
    total_value: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        server_default="0.0",
    )

    # Location information
    batch_number: Mapped[str | None] = mapped_column(String(255), nullable=True)
    warehouse_location: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        server_default="'MAIN'",
    )
    shelf_location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Status
    stock_status: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="1")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")

    # Additional info
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)

    def __repr__(self) -> str:
        return f"<ProductStock(id={self.id}, name={self.product_name}, qty={self.quantity_available})>"
