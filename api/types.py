"""
Business Backend - GraphQL Types.
Strawberry types for the business backend.
"""

import strawberry


@strawberry.type
class FAQType:
    """FAQ type for GraphQL."""

    category: str
    patterns: list[str]
    response: str
    audio_path: str | None = None


@strawberry.type
class ContextChunkType:
    """Context Chunk type for GraphQL."""

    category: str
    content: str
    metadata: dict[str, str] | None = None
