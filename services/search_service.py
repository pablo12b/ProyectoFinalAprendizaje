"""
Search Service for Business Backend.

Orchestrates LLM with product search tool for semantic queries.
"""

from dataclasses import dataclass
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from loguru import logger

from business_backend.database.models import ProductStock
from business_backend.llm.provider import LLMProvider
from business_backend.llm.tools.product_search_tool import (
    ProductSearchTool,
    create_product_search_tool,
)
from business_backend.services.product_service import ProductService


@dataclass
class SearchResult:
    """Result from semantic search."""

    answer: str
    products_found: list[ProductStock]
    query: str


class SearchService:
    """Service for semantic search using LLM and product database."""

    SYSTEM_PROMPT = """You are a helpful inventory assistant. You help users find products and check stock availability.

When a user asks about products or stock, use the product_search tool to find information in the database.

Always provide clear, concise answers about:
- Whether the product exists
- How many units are available
- The product's stock status (In Stock, Low Stock, Out of Stock)
- Price and supplier information when relevant

If no products are found, let the user know politely and suggest they try a different search term.

Respond in the same language as the user's query."""

    def __init__(
        self,
        llm_provider: LLMProvider | None,
        product_service: ProductService,
        inference_service: Any | None = None,  # Loose type to avoid circular imports if any
    ) -> None:
        """
        Initialize SearchService.

        Args:
            llm_provider: LLM provider (can be None if disabled)
            product_service: ProductService for database queries
            inference_service: InferenceService for image analysis
        """
        self.llm_provider = llm_provider
        self.product_service = product_service
        self.inference_service = inference_service
        
        self.search_tool: ProductSearchTool | None = None
        self.image_tool: Any | None = None

        if llm_provider is not None:
            self.search_tool = create_product_search_tool(product_service)
            
            if inference_service is not None:
                from business_backend.llm.tools.image_recognition_tool import (
                    create_image_recognition_tool,
                )
                self.image_tool = create_image_recognition_tool(inference_service)

    async def semantic_search(self, query: str) -> SearchResult:
        """
        Perform semantic search using LLM with product search tool.

        Args:
            query: User's natural language query

        Returns:
            SearchResult with answer and found products
        """
        if self.llm_provider is None or self.search_tool is None:
            # Fallback: direct search without LLM
            logger.warning("LLM not configured, using fallback search")
            return await self._fallback_search(query)

        try:
            return await self._llm_search(query)
        except Exception as e:
            logger.error(f"LLM search failed: {e}")
            return await self._fallback_search(query)

    async def _llm_search(self, query: str) -> SearchResult:
        """Perform search using LLM with tool calling."""
        assert self.llm_provider is not None
        assert self.search_tool is not None

        # Bind tools to model
        tools = [self.search_tool]
        if self.image_tool:
            tools.append(self.image_tool)
            
        model_with_tools = self.llm_provider.bind_tools(tools)

        # Create messages
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ]

        # First LLM call - may request tool use
        response = await model_with_tools.ainvoke(messages)

        # Check if tool was called
        if hasattr(response, "tool_calls") and response.tool_calls:
            # Execute tool calls
            tool_messages = []
            for tool_call in response.tool_calls:
                result_content = "Error: Unknown tool"
                
                if tool_call["name"] == "product_search":
                    # Execute the search
                    result_content = await self.search_tool._arun(
                        tool_call["args"]["search_term"]
                    )
                elif tool_call["name"] == "image_recognition" and self.image_tool:
                    # Execute image recognition
                    result_content = await self.image_tool._arun(
                        tool_call["args"]["image_path"]
                    )
                    
                tool_messages.append(
                    ToolMessage(
                        content=result_content,
                        tool_call_id=tool_call["id"],
                    )
                )

            # Second LLM call with tool results
            messages_with_tools = [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": query},
                response,  # AI message with tool calls
                *tool_messages,  # Tool results
            ]

            final_response = await model_with_tools.ainvoke(messages_with_tools)
            answer = (
                final_response.content
                if isinstance(final_response.content, str)
                else str(final_response.content)
            )
        else:
            # No tool call, use direct response
            answer = (
                response.content
                if isinstance(response.content, str)
                else str(response.content)
            )

        return SearchResult(
            answer=answer,
            products_found=self.search_tool.get_last_results(),
            query=query,
        )

    async def _fallback_search(self, query: str) -> SearchResult:
        """
        Fallback search without LLM.

        Extracts keywords from query and searches directly.
        """
        # Simple keyword extraction (just use the query as search term)
        # In production, you might want more sophisticated NLP
        search_term = query.strip()

        # Remove common question words
        for word in ["tienen", "hay", "existe", "buscar", "quiero", "stock", "?", "¿"]:
            search_term = search_term.lower().replace(word, "")
        search_term = search_term.strip()

        if not search_term:
            return SearchResult(
                answer="Por favor, especifica el producto que buscas.",
                products_found=[],
                query=query,
            )

        products = await self.product_service.search_by_name(search_term, limit=10)

        if not products:
            answer = f"No encontré productos que coincidan con '{search_term}'."
        else:
            product_list = ", ".join(
                f"{p.product_name} ({p.quantity_available} disponibles)"
                for p in products[:5]
            )
            answer = f"Encontré {len(products)} producto(s): {product_list}"
        
        return SearchResult(
            answer=answer,
            products_found=products,
            query=query,
        )
