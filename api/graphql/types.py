"""GraphQL types for Business Backend."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

import strawberry


@strawberry.type
class FAQ:
    """FAQ item with patterns and response."""

    type: str  # greeting, farewell, faq, etc.
    patterns: list[str]
    response: str
    category: str


@strawberry.type
class Document:
    """Business document with title and content."""

    id: str
    title: str
    content: str
    category: str


@strawberry.type
class ProductStockType:
    """Product stock information from database."""

    id: UUID
    created_at: datetime
    last_updated_at: datetime

    # Product identification
    product_id: str
    product_name: str
    product_sku: str | None

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
    last_order_date: date | None
    last_stock_count_date: date | None
    expiration_date: date | None

    # Cost
    unit_cost: Decimal
    total_value: Decimal

    # Location
    batch_number: str | None
    warehouse_location: str
    shelf_location: str | None

    # Status
    stock_status: int
    is_active: bool

    notes: str | None


@strawberry.type
class ProductSummaryType:
    """Simplified product summary for search results."""

    id: UUID
    product_name: str
    product_sku: str | None
    supplier_name: str
    quantity_available: int
    stock_status: int
    unit_cost: Decimal
    warehouse_location: str
    is_active: bool


@strawberry.type
class SemanticSearchResponse:
    """Response from semantic search with LLM."""

    answer: str
    products_found: list[ProductSummaryType]
    query: str
