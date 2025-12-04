from typing import Optional

from src.wb.schemas import DateRangeRequest, OrderItem, OrdersResponse
from src.wb.clients.base import BaseApi


class OrdersApi(BaseApi):
    """
    API client for Wildberries orders and statistics endpoints.
    
    Provides methods to fetch and manage supplier orders from the Wildberries
    Statistics API. All methods are asynchronous and return validated Pydantic models.
    
    This class is accessed via the APIClient.orders property and should not be
    instantiated directly.
    """
    async def get_orders(
        self,
        date: DateRangeRequest,
        flag: Optional[int] = 1,
    )-> list[OrderItem]:
        """
        Fetch supplier orders from the external API.

        Retrieves orders filtered by last modification date. The filtering behavior 
        depends on the flag parameter.

        Args:
            date: Date filter in YYYY-MM-DD format (RFC3339, UTC+3)
            flag: 0 = orders >= date (≤100k), 1 = exact date match (all)

        Returns:
            OrdersResponse with the list of orders
        """
        response = await self.client.fetch(
            method="GET",
            url=self.client.urls.SUPPLIER_ORDERS,
            params={"dateFrom": date.date, "flag": flag}
        )
        result = OrdersResponse.model_validate(response)
        return result.root

