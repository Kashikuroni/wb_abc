from datetime import datetime, timedelta
from fastapi import APIRouter, BackgroundTasks, HTTPException, status

from src.wb.dependencies import ContextDep
from src.wb.services.abc_analytics import calculate_abc_analysis
from src.wb.schemas import ABCItem, DateRange
from src.wb.models.utils import save_orders_to_db

router = APIRouter(tags=["wb-orders"])

@router.post("/orders", response_model=list[ABCItem])
async def get_orders(
    ctx: ContextDep,
    date_range: DateRange,
    background_tasks: BackgroundTasks,
) -> list[ABCItem]:
    """
    Fetch orders and perform ABC analysis.
    
    Retrieves Wildberries supplier orders for the specified date range
    and calculates ABC categorization based on revenue contribution.
    Orders are saved to database asynchronously in the background.
    
    The date range is limited to the last 90 days. If date_to is provided,
    returns orders within the range; otherwise returns orders for the exact date.
    
    Args:
        ctx: Application context containing database session and API client.
        date_range: Date range filter with required date_from and optional date_to.
        background_tasks: FastAPI background tasks handler.
    
    Returns:
        List of ABCItem objects with categorization (A/B/C), revenue metrics,
        and cumulative share for each product.
    
    Raises:
        HTTPException 400: If date_from is older than 90 days.
        HTTPException 400: If no orders found for the specified period.
    
    Note:
        - Dates must be in YYYY-MM-DD format
        - Maximum historical data: 90 days
        - ABC categories: A (top 80% revenue), B (next 15%), C (remaining 5%)
        - Orders are saved to database asynchronously after response
    """
    current_date = datetime.now().date()
    date_from_dt = datetime.strptime(date_range.date_from.date, "%Y-%m-%d").date()
    
    days_diff = (current_date - date_from_dt).days
    
    if days_diff > 90:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя выгрузить отчет старше чем за 90 дней"
        )

    if date_range.date_to:
        orders_response = await ctx.client.orders.get_orders(date=date_range.date_from, flag=0)
        date_to_end = datetime.strptime(date_range.date_to.date, "%Y-%m-%d") + timedelta(days=1, seconds=-1)
        
        orders = [order for order in orders_response if order.last_change_date <= date_to_end]
    else:
        orders = await ctx.client.orders.get_orders(date=date_range.date_from)

    if not orders:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="List of orders is empty."
        )

    abc_result: list[ABCItem]  = await calculate_abc_analysis(orders)

    background_tasks.add_task(save_orders_to_db, orders, ctx.db_session)

    return abc_result
