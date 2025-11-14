from app.core import Base
from sqlalchemy import Column, Integer, String, Date,ForeignKey
from datetime import date
from sqlalchemy.orm import relationship
class CartDetail(Base):
    __tablename__ = "cart_details"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id = Column(String(50), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    created_at = Column(Date, default=date.today)

    # Relationships
    cart = relationship("Carts", back_populates="cart_details")
    product = relationship("Products", back_populates="cart_details")