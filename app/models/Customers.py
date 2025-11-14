from app.core import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class Customers(Base):
    __tablename__ = "customers"

    customer_id = Column(String(50), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    user = relationship("Users", back_populates="customer")
    orders = relationship("Orders", back_populates="customer")
    carts = relationship("Carts", back_populates="customer")
    product_consulting = relationship("ProductConsulting", back_populates="customer")