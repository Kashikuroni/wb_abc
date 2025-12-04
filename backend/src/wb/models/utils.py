from decimal import Decimal

from src.wb.schemas import OrderItem

from .orders import Order, Product, Warehouse, Region

def create_order_from_item(order_item, session) -> Order:
    """
    Convert Pydantic OrderItem to SQLAlchemy ORM Order with normalized relations.
    
    Args:
        order_item: Pydantic OrderItem instance
        session: SQLAlchemy session for database operations
    
    Returns:
        Order ORM instance (not yet added to session)
    """
    from sqlalchemy import select
    
    product = session.scalar(
        select(Product).where(Product.nm_id == order_item.nm_id)
    )
    if not product:
        product = Product(
            nm_id=order_item.nm_id,
            barcode=order_item.barcode,
            supplier_article=order_item.supplier_article,
            category=order_item.category,
            subject=order_item.subject,
            brand=order_item.brand,
            tech_size=order_item.tech_size,
        )
        session.add(product)
        session.flush()
    
    warehouse = session.scalar(
        select(Warehouse).where(Warehouse.name == order_item.warehouse_name)
    )
    if not warehouse:
        warehouse = Warehouse(
            name=order_item.warehouse_name,
            warehouse_type=order_item.warehouse_type,
        )
        session.add(warehouse)
        session.flush()
    
    region = session.scalar(
        select(Region).where(
            Region.country_name == order_item.country_name,
            Region.oblast_okrug_name == order_item.oblast_okrug_name,
            Region.region_name == order_item.region_name,
        )
    )
    if not region:
        region = Region(
            country_name=order_item.country_name,
            oblast_okrug_name=order_item.oblast_okrug_name,
            region_name=order_item.region_name,
        )
        session.add(region)
        session.flush()
    
    order = Order(
        srid=order_item.srid,
        date=order_item.date,
        last_change_date=order_item.last_change_date,
        cancel_date=order_item.cancel_date,
        product_id=product.id,
        warehouse_id=warehouse.id,
        region_id=region.id,
        income_id=order_item.income_id,
        is_supply=order_item.is_supply,
        is_realization=order_item.is_realization,
        is_cancel=order_item.is_cancel,
        total_price=Decimal(str(order_item.total_price)),
        discount_percent=order_item.discount_percent,
        spp=Decimal(str(order_item.spp)),
        finished_price=Decimal(str(order_item.finished_price)),
        price_with_disc=Decimal(str(order_item.price_with_disc)),
        sticker=order_item.sticker,
        g_number=order_item.g_number,
    )
    
    return order


async def save_orders_to_db(orders: list[OrderItem], db_session):
    """
    Background task to save orders to database.
    
    Args:
        orders: List of order items to save
        db_session: Database session for saving
    """
    try:
        for order_item in orders:
            order = create_order_from_item(order_item, db_session)
            db_session.add(order)
        
        await db_session.commit()
        print(f"Successfully saved {len(orders)} orders to database")
    except Exception as e:
        await db_session.rollback()
        print(f"Error saving orders to database: {e}")
    finally:
        await db_session.close()
