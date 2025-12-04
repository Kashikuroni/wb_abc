"""
Pydantic schemas for Wildberries API requests and responses.

Defines data models for orders, errors, date ranges, and ABC analysis results.
All models use camelCase for API compatibility via alias_generator.
"""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator
from pydantic.alias_generators import to_camel


class OrderItem(BaseModel):
    """
    Individual order record from Wildberries Statistics API.
    
    Represents a single order with complete product, pricing, and logistics
    information. Used in OrdersResponse and as input for ABC analysis.
    
    Attributes:
        date: Order creation date and time.
        last_change_date: Last modification date and time (used for filtering).
        warehouse_name: Name of the warehouse handling the order.
        warehouse_type: Type of warehouse (WB warehouse or seller warehouse).
        country_name: Country of delivery.
        oblast_okrug_name: Federal district or region.
        region_name: Specific region of delivery.
        supplier_article: Seller's SKU/article number.
        nm_id: Wildberries product identifier (nomenclature ID).
        barcode: Product barcode (EAN/UPC).
        category: Product category name.
        subject: Product subject/type (e.g., "T-Shirts", "Sneakers").
        brand: Product brand name.
        tech_size: Technical size specification.
        income_id: Income/supply identifier.
        is_supply: Whether order is from supply.
        is_realization: Whether order is realization sale.
        total_price: Original price before discounts.
        discount_percent: Discount percentage applied.
        spp: Special price promotion value.
        finished_price: Final calculated price.
        price_with_disc: Price after discount (used for revenue calculations).
        is_cancel: Whether order was cancelled.
        cancel_date: Cancellation date and time.
        sticker: Sticker/label identifier.
        g_number: G-number identifier.
        srid: Unique order identifier (SRID).
    
    Note:
        Field names are automatically converted to camelCase for API compatibility.
        Use populate_by_name=True to accept both snake_case and camelCase.
    """
    date: datetime
    last_change_date: datetime
    warehouse_name: str
    warehouse_type: Literal["Склад WB", "Склад продавца"]
    country_name: str
    oblast_okrug_name: str
    region_name: str
    supplier_article: str
    nm_id: int
    barcode: str
    category: str
    subject: str
    brand: str
    tech_size: str
    income_id: int = Field(..., alias="incomeID")
    is_supply: bool
    is_realization: bool
    total_price: float
    discount_percent: int
    spp: float
    finished_price: float
    price_with_disc: float
    is_cancel: bool
    cancel_date: datetime
    sticker: str
    g_number: str
    srid: str

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class OrdersResponse(RootModel):
    """
    API response wrapper for orders list.
    
    Wraps the orders array returned by the Wildberries API into a validated
    Pydantic model. The root field contains the list of OrderItem objects.
    
    Attributes:
        root: List of OrderItem objects from the API response.
    """
    root: list[OrderItem]


class BadRequestError(BaseModel):
    """
    Bad request error response from Wildberries API.
    
    Returned when request validation fails (invalid parameters, missing fields, etc.).
    
    Attributes:
        errors: List of error messages describing validation failures.
    """
    errors: list[str]

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class ApiError(BaseModel):
    """
    Standard error response from Wildberries API.
    
    Base error model containing detailed information about API failures.
    Used as parent class for specific error types (401, 429, etc.).
    
    Attributes:
        title: Error title/summary.
        detail: Detailed error description.
        code: Error code identifier.
        request_id: Unique request identifier for debugging.
        origin: Origin service that generated the error.
        status: HTTP status code as float.
        status_text: HTTP status text description.
        timestamp: Error occurrence timestamp.
    """
    title: str
    detail: str
    code: str
    request_id: str
    origin: str
    status: float
    status_text: str
    timestamp: datetime

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class UnauthorizedError(ApiError):
    """
    Unauthorized error (HTTP 401) from Wildberries API.
    
    Returned when API key is invalid, missing, or expired.
    Inherits all fields from ApiError.
    """
    pass


class TooManyRequestsError(ApiError):
    """
    Rate limit exceeded error (HTTP 429) from Wildberries API.
    
    Returned when too many requests are made in a given time period.
    Inherits all fields from ApiError.
    """
    pass


class DateRangeRequest(BaseModel):
    """
    Date parameter for API requests with validation.
    
    Validates date string format and ensures it matches YYYY-MM-DD pattern
    required by the Wildberries API.
    
    Attributes:
        date: Date string in YYYY-MM-DD format (e.g., "2024-01-15").
    
    Raises:
        ValueError: If date string doesn't match YYYY-MM-DD format.
    """
    date: str

    @field_validator("date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """
        Validate date string format.
        
        Args:
            v: Date string to validate.
        
        Returns:
            Validated date string in YYYY-MM-DD format.
        
        Raises:
            ValueError: If date string doesn't match YYYY-MM-DD format.
        """
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError('Дата должна быть в формате YYYY-MM-DD (например, 2019-06-20)')


class DateRange(BaseModel):
    """
    Date range filter for querying orders.
    
    Supports both single date and date range queries. When date_to is None,
    only orders matching date_from exactly are returned (depending on flag).
    
    Attributes:
        date_from: Start date of the range (required).
        date_to: End date of the range (optional). If provided, filters orders
            between date_from and date_to inclusive.
    """
    date_from: DateRangeRequest
    date_to: Optional[DateRangeRequest]


class ABCItem(BaseModel):
    """
    ABC analysis result for a single product.
    
    Contains product information, ABC category assignment, and revenue metrics
    calculated by the ABC analysis algorithm.
    
    Attributes:
        supplier_article: Seller's SKU/article number.
        nm_id: Wildberries product identifier (nomenclature ID).
        barcode: Product barcode (EAN/UPC).
        subject: Product subject/type (e.g., "T-Shirts", "Sneakers").
        brand: Product brand name.
        category: ABC category assignment (A=top 80%, B=next 15%, C=remaining 5%).
        orders_count: Total number of orders for this product.
        revenue: Total revenue in rubles for this product.
        revenue_share: Percentage of total revenue contributed by this product.
        cumulative_share: Cumulative revenue percentage up to and including this product.
    """
    supplier_article: str
    nm_id: int
    barcode: str
    subject: str
    brand: str
    category: Literal["A", "B", "C"]
    orders_count: int
    revenue: float
    revenue_share: float       
    cumulative_share: float   

