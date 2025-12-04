from collections import defaultdict
from typing import Literal

from src.wb.schemas import ABCItem, OrderItem


async def calculate_abc_analysis(
    orders: list[OrderItem],
    *,
    threshold_a: float = 80.0,
    threshold_b: float = 95.0,
    exclude_cancelled: bool = True,
) -> list[ABCItem]:
    """
    Perform ABC analysis on order list based on revenue contribution.
    
    Aggregates orders by product (nm_id), calculates revenue metrics, and assigns
    ABC categories using the Pareto principle. Category A represents products
    contributing to the top threshold_a% of revenue, B the next segment up to
    threshold_b%, and C the remaining products.
    
    Args:
        orders: List of orders to analyze.
        threshold_a: Cumulative revenue share threshold for category A in percent.
            Products up to this threshold are marked as 'A'. Defaults to 80.0.
        threshold_b: Cumulative revenue share threshold for category B in percent.
            Products between threshold_a and threshold_b are marked as 'B'.
            Products above threshold_b are marked as 'C'. Defaults to 95.0.
        exclude_cancelled: Whether to exclude cancelled orders from analysis.
            Filters out orders where is_cancel=True. Defaults to True.
    
    Returns:
        List of ABCItem objects sorted by revenue in descending order, containing
        product details, ABC category, order count, revenue, revenue share, and
        cumulative share. Returns empty list if no valid orders found or total
        revenue is zero.
    
    Note:
        - Products are aggregated by nm_id (Wildberries product identifier)
        - Revenue is calculated using price_with_disc field
        - All percentage values are rounded to 2 decimal places
        - Category assignment is based on sorted cumulative revenue contribution
    """
    filtered_orders = [
        order for order in orders 
        if not (exclude_cancelled and order.is_cancel)
    ]
    
    if not filtered_orders:
        return []
    
    aggregated: dict[int, dict] = defaultdict(lambda: {
        "supplier_article": "",
        "barcode": "",
        "subject": "",
        "brand": "",
        "orders_count": 0,
        "revenue": 0.0,
    })
    
    for order in filtered_orders:
        item = aggregated[order.nm_id]
        if not item["supplier_article"]:
            item["supplier_article"] = order.supplier_article
            item["barcode"] = order.barcode
            item["subject"] = order.subject
            item["brand"] = order.brand
        
        item["orders_count"] += 1
        item["revenue"] += order.price_with_disc
    
    total_revenue = sum(item["revenue"] for item in aggregated.values())
    
    if total_revenue == 0:
        return []
    
    sorted_items = sorted(
        aggregated.items(),
        key=lambda x: x[1]["revenue"],
        reverse=True
    )
    
    result: list[ABCItem] = []
    cumulative_share = 0.0
    
    for nm_id, data in sorted_items:
        revenue_share = (data["revenue"] / total_revenue) * 100
        cumulative_share += revenue_share
        
        if cumulative_share <= threshold_a:
            category: Literal["A", "B", "C"] = "A"
        elif cumulative_share <= threshold_b:
            category = "B"
        else:
            category = "C"
        
        result.append(ABCItem(
            supplier_article=data["supplier_article"],
            nm_id=nm_id,
            barcode=data["barcode"],
            subject=data["subject"],
            brand=data["brand"],
            category=category,
            orders_count=data["orders_count"],
            revenue=round(data["revenue"], 2),
            revenue_share=round(revenue_share, 2),
            cumulative_share=round(cumulative_share, 2),
        ))
    
    return result
