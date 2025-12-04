"""
FastAPI dependency injection configuration for Wildberries API integration.

Provides reusable dependencies for:
- API credentials management
- APIClient lifecycle management
- Database session and API client aggregation

Usage:
    from src.wb.dependencies import ContextDep
    
    @router.post("/orders")
    async def get_orders(ctx: ContextDep):
        orders = await ctx.client.orders.get_orders(...)
        # Use ctx.db_session for database operations
"""

from dataclasses import dataclass
from typing import Annotated, AsyncGenerator

from fastapi import Depends
from pydantic import BaseModel

from src.dependencies import DBSessionDep
from src.config import WbSettings as Settings
from src.wb.clients.core import APIClient


class Credentials(BaseModel):
    """
    API credentials container for Wildberries authentication.
    
    Attributes:
        api_key: Wildberries API authorization token.
    """
    api_key: str

def get_credentials():
    """
    Retrieve and validate Wildberries API credentials from settings.
    
    Loads API key from environment configuration and wraps it in a
    Credentials object for dependency injection.
    
    Returns:
        Credentials object containing the API key.
    
    Raises:
        ValueError: If API_KEY is not specified in environment file.
    """
    settings = Settings()
    if settings.API_KEY is None:
        raise ValueError("Make sure you specified API_KEY in env file.")
    return Credentials(api_key=settings.API_KEY)
    

async def get_client(
    creds: Credentials = Depends(get_credentials),
) -> AsyncGenerator[APIClient, None]:
    """
    Create and manage APIClient lifecycle for dependency injection.
    
    Initializes an async context-managed APIClient with provided credentials
    and yields it for use in FastAPI endpoints. Automatically handles cleanup
    on request completion.
    
    Args:
        creds: Validated API credentials from get_credentials dependency.
    
    Yields:
        Configured APIClient instance ready for making API requests.
    
    Note:
        Used via ApiClientDep annotation in FastAPI route handlers.
        Client is automatically closed after request completion.
    """
    async with APIClient(
        api_key=creds.api_key,
    ) as client:
        yield client


ApiClientDep = Annotated[APIClient, Depends(get_client)]


@dataclass()
class Context:
    """
    Request context aggregator for FastAPI dependencies.
    
    Combines database session and API client into a single injectable
    dependency to reduce boilerplate in route handlers.
    
    Attributes:
        db_session: Active database session for ORM operations.
        client: Configured APIClient for Wildberries API requests.
    
    Note:
        Use ContextDep annotation to inject this into route handlers
        instead of injecting db_session and client separately.
    """
    db_session: DBSessionDep
    client: ApiClientDep


async def get_context(
    db_session: DBSessionDep,
    client: ApiClientDep,
) -> Context:
    """
    Aggregate database session and API client into unified context.
    
    Factory function for creating Context objects in FastAPI dependency
    injection system. Simplifies route signatures by combining multiple
    dependencies into one.
    
    Args:
        db_session: Database session dependency.
        client: API client dependency.
    
    Returns:
        Context object containing both dependencies.
    
    Note:
        Used via ContextDep annotation in route handlers.
    """
    return Context(
        db_session=db_session,
        client=client,
    )


ContextDep = Annotated[Context, Depends(get_context)]
