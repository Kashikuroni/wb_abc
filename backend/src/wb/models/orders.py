from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import int_pk, Base


class Product(Base):
    """Normalized product/SKU information."""
    __table_args__ = {"schema": "wb"}
    
    id: Mapped[int_pk]
    nm_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, comment="Wildberries product ID")
    barcode: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    supplier_article: Mapped[str] = mapped_column(String(255), index=True, comment="Seller's SKU")
    category: Mapped[str] = mapped_column(String(255))
    subject: Mapped[str] = mapped_column(String(255))
    brand: Mapped[str] = mapped_column(String(255))
    tech_size: Mapped[str] = mapped_column(String(100))
    
    orders: Mapped[list["Order"]] = relationship(back_populates="product")


class Warehouse(Base):
    """Normalized warehouse information."""
    __table_args__ = {"schema": "wb"}
    
    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(String(255), unique=True)
    warehouse_type: Mapped[str] = mapped_column(String(50), comment="Склад WB or Склад продавца")
    
    orders: Mapped[list["Order"]] = relationship(back_populates="warehouse")


class Region(Base):
    """Normalized region/geography information."""
    __table_args__ = {"schema": "wb"}
    
    id: Mapped[int_pk]
    country_name: Mapped[str] = mapped_column(String(255))
    oblast_okrug_name: Mapped[str] = mapped_column(String(255))
    region_name: Mapped[str] = mapped_column(String(255))
    
    __table_args__ = (
        Index("idx_region_composite", "country_name", "oblast_okrug_name", "region_name", unique=True),
        {"schema": "wb"},
    )
    
    orders: Mapped[list["Order"]] = relationship(back_populates="region")


class Order(Base):
    """Main order table with references to normalized entities."""
    __table_args__ = (
        Index("idx_orders_date", "date"),
        Index("idx_orders_last_change_date", "last_change_date"),
        Index("idx_orders_is_cancel", "is_cancel"),
        Index("idx_orders_product_id", "product_id"),
        {"schema": "wb"},
    )
    
    id: Mapped[int_pk]
    srid: Mapped[str] = mapped_column(String(255), unique=True, index=True, comment="Unique order identifier")
    
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_change_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    cancel_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    
    product_id: Mapped[int] = mapped_column(ForeignKey("wb.products.id"))
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("wb.warehouses.id"))
    region_id: Mapped[int] = mapped_column(ForeignKey("wb.regions.id"))
    
    income_id: Mapped[int] = mapped_column(Integer, comment="Income/supply identifier")
    is_supply: Mapped[bool] = mapped_column(Boolean)
    is_realization: Mapped[bool] = mapped_column(Boolean)
    is_cancel: Mapped[bool] = mapped_column(Boolean)
    
    total_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    discount_percent: Mapped[int] = mapped_column(Integer)
    spp: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    finished_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    price_with_disc: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    
    sticker: Mapped[str] = mapped_column(String(255))
    g_number: Mapped[str] = mapped_column(String(255))
    
    product: Mapped["Product"] = relationship(back_populates="orders")
    warehouse: Mapped["Warehouse"] = relationship(back_populates="orders")
    region: Mapped["Region"] = relationship(back_populates="orders")
