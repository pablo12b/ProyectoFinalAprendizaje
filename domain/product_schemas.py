"""
Product Schemas for Business Backend.

Pydantic models for data validation and serialization.
"""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProductStockSchema(BaseModel):
    """Pydantic schema for ProductStock."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    last_updated_at: datetime

    # Product info
    product_id: str
    product_name: str
    product_sku: str | None = None

    # Supplier
    supplier_id: str
    supplier_name: str

    # Quantities
    quantity_on_hand: int
    quantity_reserved: int
    quantity_available: int

    # Stock levels
    minimum_stock_level: int
    reorder_point: int
    optimal_stock_level: int
    reorder_quantity: int
    average_daily_usage: Decimal

    # Dates
    last_order_date: date | None = None
    last_stock_count_date: date | None = None
    expiration_date: date | None = None

    # Cost
    unit_cost: Decimal
    total_value: Decimal

    # Location
    batch_number: str | None = None
    warehouse_location: str
    shelf_location: str | None = None

    # Status
    stock_status: int
    is_active: bool

    notes: str | None = None


class ProductStockSummary(BaseModel):
    """Simplified product summary for search results."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_name: str
    product_sku: str | None = None
    supplier_name: str
    quantity_available: int
    stock_status: int
    unit_cost: Decimal
    warehouse_location: str
    is_active: bool


class SearchRequest(BaseModel):
    """Request model for semantic search."""

    query: str


class SearchResponse(BaseModel):
    """Response model for semantic search."""

    answer: str
    products_found: list[ProductStockSummary]
    query: str
