from app.core import Base
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from datetime import date
from sqlalchemy.orm import relationship
class Carts(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False)
    created_at = Column(Date, default=date.today)

    # Relationships
    customer = relationship("Customers", back_populates="carts")
    cart_details = relationship("CartDetail", back_populates="cart")