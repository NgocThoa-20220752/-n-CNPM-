from app.core import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship

class OrderDetail(Base):
    __tablename__ = "order_details"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(String(50), ForeignKey("orders.id"), nullable=False)
    product_id = Column(String(50), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    total = Column(Numeric(15, 2), nullable=False)
    shipping_address = Column(String(500), nullable=False)
    note = Column(Text, nullable=True)

    # Relationships
    order = relationship("Orders", back_populates="order_details")
    product = relationship("Products", back_populates="order_details")