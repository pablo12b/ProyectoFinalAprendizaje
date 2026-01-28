"""GraphQL queries for Business Backend.

This module exposes FAQs, Documents, and Products via GraphQL.
The data is read from CSV files (TenantDataService) and database (ProductService).
"""

from typing import Annotated
from uuid import UUID

import strawberry
from aioinject import Inject
from aioinject.ext.strawberry import inject
from loguru import logger

from business_backend.api.graphql.types import (
    FAQ,
    Document,
    ProductStockType,
    ProductSummaryType,
    SemanticSearchResponse,
)
from business_backend.services.product_service import ProductService
from business_backend.services.search_service import SearchService
from business_backend.services.tenant_data_service import TenantDataService


@strawberry.type
class BusinessQuery:
    """Business backend queries (FAQs, Documents)."""

    @strawberry.field
    @inject
    async def get_faqs(
        self, tenant: str, data_service: Annotated[TenantDataService, Inject]
    ) -> list[FAQ]:
        """
        Get FAQs for a tenant from CSV files.

        Example query:
            query {
              getFaqs(tenant: "app") {
                type
                patterns
                response
                category
              }
            }
        """
        logger.info(f"📋 GraphQL: getFaqs(tenant={tenant})")

        try:
            # Read FAQs from CSV using TenantDataService (returns FAQData model)
            faq_data = await data_service.read_faqs_csv(tenant)
        except FileNotFoundError as e:
            logger.error(f"❌ CSV not found: {e}")
            return []

        # Convert Pydantic models to GraphQL FAQ list
        faqs: list[FAQ] = []

        # Greetings
        if faq_data.greeting_patterns:
            faqs.append(
                FAQ(
                    type="greeting",
                    patterns=faq_data.greeting_patterns,
                    response=faq_data.responses.greeting,
                    category="greeting",
                )
            )

        # Farewells
        if faq_data.farewell_patterns:
            faqs.append(
                FAQ(
                    type="farewell",
                    patterns=faq_data.farewell_patterns,
                    response=faq_data.responses.farewell,
                    category="farewell",
                )
            )

        # Gratitude
        if faq_data.gratitude_patterns:
            faqs.append(
                FAQ(
                    type="gratitude",
                    patterns=faq_data.gratitude_patterns,
                    response=faq_data.responses.gratitude,
                    category="gratitude",
                )
            )

        # Assistant info
        if faq_data.assistant_info_patterns:
            faqs.append(
                FAQ(
                    type="assistant_info",
                    patterns=faq_data.assistant_info_patterns,
                    response=faq_data.responses.assistant_info,
                    category="assistant_info",
                )
            )

        # Help requests
        if faq_data.help_request_patterns:
            faqs.append(
                FAQ(
                    type="help_request",
                    patterns=faq_data.help_request_patterns,
                    response=faq_data.responses.help_request,
                    category="help_request",
                )
            )

        # FAQ items
        for item in faq_data.faq_items:
            faqs.append(
                FAQ(
                    type="faq",
                    patterns=item.patterns,
                    response=item.answer,
                    category=item.category,
                )
            )

        logger.info(f"✅ GraphQL: Returned {len(faqs)} FAQs for tenant: {tenant}")
        return faqs

    @strawberry.field
    @inject
    async def get_documents(
        self, tenant: str, data_service: Annotated[TenantDataService, Inject]
    ) -> list[Document]:
        """
        Get documents (chunks) for a tenant from CSV files.

        Example query:
            query {
              getDocuments(tenant: "app") {
                id
                title
                content
                category
              }
            }
        """
        logger.info(f"📚 GraphQL: getDocuments(tenant={tenant})")

        try:
            # Read chunks from CSV using TenantDataService (returns list[DocumentChunk])
            chunks = await data_service.read_chunks_csv(tenant)
        except FileNotFoundError as e:
            logger.error(f"❌ CSV not found: {e}")
            return []

        # Convert DocumentChunk models to Document GraphQL type
        result: list[Document] = [
            Document(
                id=f"{tenant}_{idx}",  # Generate unique ID
                title=chunk.category or "Unknown",  # Use category as title
                content=chunk.content,
                category=chunk.category or "general",
            )
            for idx, chunk in enumerate(chunks)
        ]

        logger.info(
            f"✅ GraphQL: Returned {len(result)} documents for tenant: {tenant}"
        )
        return result

    # =====================
    # Product Stock Queries
    # =====================

    @strawberry.field
    @inject
    async def products(
        self,
        product_service: Annotated[ProductService, Inject],
        limit: int = 50,
        offset: int = 0,
    ) -> list[ProductStockType]:
        """
        List products from database with pagination.

        Example query:
            query {
              products(limit: 10, offset: 0) {
                id
                productName
                quantityAvailable
                stockStatus
                unitCost
              }
            }
        """
        logger.info(f"📦 GraphQL: products(limit={limit}, offset={offset})")

        products = await product_service.list_products(limit=limit, offset=offset)

        result = [
            ProductStockType(
                id=p.id,
                created_at=p.created_at,
                last_updated_at=p.last_updated_at,
                product_id=p.product_id,
                product_name=p.product_name,
                product_sku=p.product_sku,
                supplier_id=p.supplier_id,
                supplier_name=p.supplier_name,
                quantity_on_hand=p.quantity_on_hand,
                quantity_reserved=p.quantity_reserved,
                quantity_available=p.quantity_available,
                minimum_stock_level=p.minimum_stock_level,
                reorder_point=p.reorder_point,
                optimal_stock_level=p.optimal_stock_level,
                reorder_quantity=p.reorder_quantity,
                average_daily_usage=p.average_daily_usage,
                last_order_date=p.last_order_date,
                last_stock_count_date=p.last_stock_count_date,
                expiration_date=p.expiration_date,
                unit_cost=p.unit_cost,
                total_value=p.total_value,
                batch_number=p.batch_number,
                warehouse_location=p.warehouse_location,
                shelf_location=p.shelf_location,
                stock_status=p.stock_status,
                is_active=p.is_active,
                notes=p.notes,
            )
            for p in products
        ]

        logger.info(f"✅ GraphQL: Returned {len(result)} products")
        return result

    @strawberry.field
    @inject
    async def product(
        self,
        product_service: Annotated[ProductService, Inject],
        id: UUID,
    ) -> ProductStockType | None:
        """
        Get a single product by ID.

        Example query:
            query {
              product(id: "uuid-here") {
                productName
                quantityAvailable
                supplierName
              }
            }
        """
        logger.info(f"📦 GraphQL: product(id={id})")

        p = await product_service.get_product(id)

        if p is None:
            logger.warning(f"⚠️ Product not found: {id}")
            return None

        return ProductStockType(
            id=p.id,
            created_at=p.created_at,
            last_updated_at=p.last_updated_at,
            product_id=p.product_id,
            product_name=p.product_name,
            product_sku=p.product_sku,
            supplier_id=p.supplier_id,
            supplier_name=p.supplier_name,
            quantity_on_hand=p.quantity_on_hand,
            quantity_reserved=p.quantity_reserved,
            quantity_available=p.quantity_available,
            minimum_stock_level=p.minimum_stock_level,
            reorder_point=p.reorder_point,
            optimal_stock_level=p.optimal_stock_level,
            reorder_quantity=p.reorder_quantity,
            average_daily_usage=p.average_daily_usage,
            last_order_date=p.last_order_date,
            last_stock_count_date=p.last_stock_count_date,
            expiration_date=p.expiration_date,
            unit_cost=p.unit_cost,
            total_value=p.total_value,
            batch_number=p.batch_number,
            warehouse_location=p.warehouse_location,
            shelf_location=p.shelf_location,
            stock_status=p.stock_status,
            is_active=p.is_active,
            notes=p.notes,
        )

    @strawberry.field
    @inject
    async def search_products(
        self,
        product_service: Annotated[ProductService, Inject],
        name: str,
        limit: int = 20,
    ) -> list[ProductSummaryType]:
        """
        Search products by name (case-insensitive).

        Example query:
            query {
              searchProducts(name: "leche") {
                productName
                quantityAvailable
                stockStatus
              }
            }
        """
        logger.info(f"🔍 GraphQL: searchProducts(name={name}, limit={limit})")

        products = await product_service.search_by_name(name=name, limit=limit)

        result = [
            ProductSummaryType(
                id=p.id,
                product_name=p.product_name,
                product_sku=p.product_sku,
                supplier_name=p.supplier_name,
                quantity_available=p.quantity_available,
                stock_status=p.stock_status,
                unit_cost=p.unit_cost,
                warehouse_location=p.warehouse_location,
                is_active=p.is_active,
            )
            for p in products
        ]

        logger.info(f"✅ GraphQL: Found {len(result)} products matching '{name}'")
        return result

    # =====================
    # Semantic Search Query
    # =====================

    @strawberry.field
    @inject
    async def semantic_search(
        self,
        search_service: Annotated[SearchService, Inject],
        query: str,
    ) -> SemanticSearchResponse:
        """
        Semantic search using LLM with product database.

        The LLM interprets the query and uses tools to search products,
        then generates a natural language response.

        Example query:
            query {
              semanticSearch(query: "¿Tienen leche en stock?") {
                answer
                productsFound {
                  productName
                  quantityAvailable
                }
                query
              }
            }
        """
        logger.info(f"🤖 GraphQL: semanticSearch(query={query})")

        response = await search_service.semantic_search(query)

        products_found = [
            ProductSummaryType(
                id=p.id,
                product_name=p.product_name,
                product_sku=p.product_sku,
                supplier_name=p.supplier_name,
                quantity_available=p.quantity_available,
                stock_status=p.stock_status,
                unit_cost=p.unit_cost,
                warehouse_location=p.warehouse_location,
                is_active=p.is_active,
            )
            for p in response.products_found
        ]

        logger.info(
            f"✅ GraphQL: Semantic search completed. Found {len(products_found)} products"
        )

        return SemanticSearchResponse(
            answer=response.answer,
            products_found=products_found,
            query=response.query,
        )
