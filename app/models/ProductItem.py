from app.core import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Float,
    Text,
    Numeric,
    ForeignKey,
    Enum as SQLEnum,
)
from datetime import datetime
from sqlalchemy.orm import relationship
from app.enum.StatusAccountEnum import StatusAccountEnum


class ProductItem(Base):
    __tablename__ = "product_items"

    id = Column(String(50), primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    weight = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    dimension = Column(String(100), nullable=True)
    expiry_date = Column(Date, nullable=True)

    price = Column(Numeric(15, 2), nullable=False)
    stock_quantity = Column(Integer, nullable=False, default=0)
    status = Column(SQLEnum(StatusAccountEnum), default=StatusAccountEnum.ACTIVE)

    cycle = Column(String(100), nullable=True)
    ingredient = Column(Text, nullable=True)
    how_to_use = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    product = relationship("Product", back_populates="items")
    images = relationship(
        "ProductItemImage",
        back_populates="product_item",
        cascade="all, delete-orphan"
    )

    cart_details = relationship("CartDetail", back_populates="product_item")
    order_details = relationship("OrderDetail", back_populates="product_item")
