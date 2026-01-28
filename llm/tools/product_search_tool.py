"""
Product Search Tool for LangChain.

This tool allows the LLM to search products in the database.
Uses ProductService with SQLAlchemy ORM.
"""

from typing import Any

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from business_backend.database.models import ProductStock
from business_backend.services.product_service import ProductService


class ProductSearchInput(BaseModel):
    """Input schema for product search tool."""

    search_term: str = Field(
        description="The product name or keyword to search for in the database"
    )


class ProductSearchTool(BaseTool):
    """
    LangChain tool for searching products in the database.

    Uses ProductService to query the product_stocks table via SQLAlchemy ORM.
    """

    name: str = "product_search"
    description: str = (
        "Searches for products in the inventory database by name. "
        "Use this tool when the user asks about product availability, "
        "stock levels, or wants to find a specific product. "
        "Returns product information including name, quantity available, "
        "stock status, price, and supplier."
    )
    args_schema: type[BaseModel] = ProductSearchInput

    # Service reference (set during initialization)
    product_service: ProductService | None = None

    # Store last search results for the response
    last_results: list[ProductStock] = []

    model_config = {"arbitrary_types_allowed": True}

    def _run(self, search_term: str) -> str:
        """Sync version - not used, raises error."""
        raise NotImplementedError("Use async version")

    async def _arun(self, search_term: str) -> str:
        """
        Async search for products by name.

        Args:
            search_term: Product name or keyword to search

        Returns:
            Formatted string with product information
        """
        if self.product_service is None:
            return "Error: Product service not configured"

        products = await self.product_service.search_by_name(name=search_term, limit=10)

        # Store results for later use
        self.last_results = products

        if not products:
            return f"No products found matching '{search_term}'"

        # Format results for LLM
        results = []
        for p in products:
            status_text = self._get_stock_status_text(p.stock_status)
            results.append(
                f"- {p.product_name} (SKU: {p.product_sku or 'N/A'}): "
                f"{p.quantity_available} units available, "
                f"Status: {status_text}, "
                f"Price: ${p.unit_cost:.2f}, "
                f"Supplier: {p.supplier_name}, "
                f"Location: {p.warehouse_location}"
            )

        return f"Found {len(products)} products:\n" + "\n".join(results)

    def _get_stock_status_text(self, status: int) -> str:
        """Convert stock status code to text."""
        status_map = {
            0: "Out of Stock",
            1: "In Stock",
            2: "Low Stock",
            3: "Overstock",
        }
        return status_map.get(status, "Unknown")

    def get_last_results(self) -> list[ProductStock]:
        """Get the last search results."""
        return self.last_results


def create_product_search_tool(product_service: ProductService) -> ProductSearchTool:
    """
    Create a product search tool with the given service.

    Args:
        product_service: ProductService instance for database queries

    Returns:
        Configured ProductSearchTool
    """
    tool = ProductSearchTool()
    tool.product_service = product_service
    return tool
