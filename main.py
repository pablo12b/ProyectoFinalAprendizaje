"""
Business Backend - Independent FastAPI Application.

This service provides GraphQL API for FAQs and Documents from CSV files.
Runs independently on port 9000 (configurable).

Architecture:
- Reads tenant data from CSV files (business_backend/data/{tenant}/)
- Exposes data via GraphQL queries (getFaqs, getDocuments)
- Completely independent from agent service
- No database access - stateless data provider

Usage:
    poetry run python -m business_backend.main --port 9000
"""

import argparse

import strawberry
import uvicorn
from aioinject.ext.strawberry import AioInjectExtension
from fastapi import FastAPI
from loguru import logger
from strawberry.fastapi import GraphQLRouter

from business_backend.api.graphql.queries import BusinessQuery
from business_backend.api.rest.endpoints import router as detection_router
from business_backend.api.rest.computer_endpoints import router as computer_router
from business_backend.container import create_business_container


def create_business_backend_app() -> FastAPI:
    """
    Create independent FastAPI application for business_backend.

    Returns:
        FastAPI application with GraphQL endpoint
    """
    app = FastAPI(
        title="Business Backend API",
        description="Provides FAQs and Documents from CSV files via GraphQL",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Create business_backend's own DI container
    container = create_business_container()
    logger.info("✅ Business Backend DI container created")

    # Connect AioInject middleware
    from aioinject.ext.fastapi import AioInjectMiddleware
    app.add_middleware(AioInjectMiddleware, container=container)

    # Create GraphQL schema with BusinessQuery as root
    schema = strawberry.Schema(
        query=BusinessQuery,
        extensions=[
            AioInjectExtension(container),  # Uses business_backend's container
        ],
    )
    logger.info("✅ Business Backend GraphQL schema created")

    # Add GraphQL router
    graphql_app = GraphQLRouter(
        schema,
        graphiql=True,  # Enable GraphiQL interface
    )
    app.include_router(graphql_app, prefix="/graphql")
    
    # Add REST router
    app.include_router(detection_router, prefix="/api", tags=["Detection"])
    app.include_router(computer_router, prefix="/api", tags=["Computers"])

    # Health check endpoint
    @app.get("/health")
    async def health():
        """Health check for business backend service."""
        return {
            "status": "ok",
            "service": "business_backend",
            "version": "1.0.0",
        }

    @app.get("/")
    async def root():
        """Root endpoint with service information."""
        return {
            "service": "Business Backend API",
            "version": "1.0.0",
            "graphql_endpoint": "/graphql",
            "graphiql_ui": "/graphql (browser)",
            "health_check": "/health",
            "docs": "/docs",
        }

    logger.info("✅ Business Backend FastAPI app created")
    return app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Business Backend Service")
    _ = parser.add_argument(
        "--port",
        type=int,
        default=9000,
        help="Port to run business backend on (default: 9000)",
    )
    _ = parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)",
    )

    args = parser.parse_args()

    app = create_business_backend_app()

    # Extract args with explicit types
    host: str = args.host
    port: int = args.port

    logger.info(f"🚀 Starting Business Backend on {host}:{port}")
    logger.info(f"📊 GraphiQL UI: http://localhost:{port}/graphql")
    logger.info(f"📖 API Docs: http://localhost:{port}/docs")

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
    )
