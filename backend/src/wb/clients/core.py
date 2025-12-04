import asyncio
from abc import ABC
from types import TracebackType
from typing import Any, Optional, Type

import httpx

from src.wb.clients.orders import OrdersApi
from src.wb.clients.urls import ExternalApiUrls


class FetchError(Exception):
    """Raised when an HTTP request fails."""


class APIClient(ABC):
    """
    Asynchronous HTTP client for Wildberries Statistics API.
    
    Manages HTTP connections, authentication, rate limiting, and provides access
    to various API endpoint groups. Must be used as an async context manager.
    
    Attributes:
        urls: Class containing all API endpoint URLs.
        orders: Property providing access to OrdersApi endpoints.
    
    Note:
        - Must be used with 'async with' statement
        - Rate limiting is controlled via semaphore
        - All requests include automatic authorization headers
    """
    def __init__(
        self,
        api_key: str,
        max_concurrent_requests: int = 10,
        timeout: float = 10.0
    ):
        """
        Initialize the API client with authentication and connection settings.
        
        Args:
            api_key: Wildberries API authorization token.
            max_concurrent_requests: Maximum number of concurrent API requests allowed.
                Prevents rate limiting by controlling parallel request count.
            timeout: Request timeout in seconds. Applied to all HTTP operations.
        """
        self.urls = ExternalApiUrls

        self._client: Optional[httpx.AsyncClient] = None
        self._semaphore = asyncio.Semaphore(max_concurrent_requests)
        self._timeout = timeout
        self._api_key = api_key



        self._orders: Optional[OrdersApi] = None


    async def __aenter__(self) -> "APIClient":
        """
        Enter the async context manager and initialize HTTP client.
        
        Creates and configures the underlying httpx.AsyncClient with base URL
        and timeout settings.
        
        Returns:
            Self instance with initialized HTTP client.
        """
        self._client = httpx.AsyncClient(
            base_url=ExternalApiUrls.BASE_URL,
            timeout=httpx.Timeout(self._timeout),
        )
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ):
        """
        Exit the async context manager and cleanup resources.
        
        Closes the HTTP client connection gracefully, ensuring all pending
        requests are completed.
        
        Args:
            exc_type: Exception type if an error occurred, None otherwise.
            exc_val: Exception instance if an error occurred, None otherwise.
            exc_tb: Exception traceback if an error occurred, None otherwise.
        """
        if self._client:
            await self._client.aclose()


    def get_default_headers(self) -> dict[str, Any]:
        """
        Get default HTTP headers for all API requests.
        
        Returns:
            Dictionary containing Authorization header with API key and
            Content-Type set to application/json.
        """
        return {
            "Authorization": self._api_key,
            "Content-Type": "application/json",
        }

    async def fetch(
        self,
        url: str,
        params: Optional[dict[str, Any]] = None,
        body: Optional[dict[str, Any]] = None,
        method: str = "POST",
        headers: Optional[dict[str, Any]] = None,
    ) -> Any:
        """
        Execute an HTTP request to the API with rate limiting and error handling.
        
        Performs rate-limited HTTP request with automatic header injection,
        error handling, and JSON response parsing. Merges provided headers
        with default authorization headers.
        
        Args:
            url: API endpoint URL (relative to base URL or absolute).
            params: Optional query parameters to include in the request.
            body: Optional JSON body for POST/PUT requests.
            method: HTTP method (GET, POST, PUT, DELETE, etc.). Defaults to POST.
            headers: Optional additional headers to merge with defaults.
        
        Returns:
            Parsed JSON response as Python dictionary or list.
        
        Raises:
            RuntimeError: If client is not initialized (used outside async context).
            FetchError: If HTTP request fails due to network error or non-2xx status code.
        
        Note:
            - Rate limiting is enforced via internal semaphore
            - Default headers (auth + content-type) are automatically included
            - Custom headers override defaults if keys conflict
        """
        if not self._client:
            raise RuntimeError("Client is not initialized. Use 'async with'.")

        merged_headers = {**self.get_default_headers(), **(headers or {})}

        async with self._semaphore:
            try:
                resp = await self._client.request(
                    method=method.upper(),
                    url=url,
                    params=params,
                    json=body,
                    headers=merged_headers,
                )
                resp.raise_for_status()
                return resp.json()

            except httpx.HTTPStatusError as e:
                text = e.response.text
                msg = f"Request failed (url={url}, params={params}, body={body}), status={e.response.status_code}, response={text}"
                raise FetchError(msg)

            except httpx.RequestError as e:
                msg = f"HTTP client error for request url={url}. Details: {e}"
                raise FetchError(msg)

    @property
    def orders(self) -> OrdersApi:
        """
        Access the Orders API endpoint group.
        
        Lazy-initializes and returns the OrdersApi instance for fetching
        supplier orders and related data.
        
        Returns:
            OrdersApi instance configured with this client.
        """
        if not self._orders:
            self._orders = OrdersApi(self)
        return self._orders
