from app.core import Base
from sqlalchemy import Column, Integer, String,ForeignKey
from sqlalchemy.orm import relationship
class ProductConsulting(Base):
    __tablename__ = "product_consulting"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    api_key = Column(String(255), nullable=False)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False)
    ai_system_id = Column(Integer, ForeignKey("ai_systems.id_ai"), nullable=True)

    # Relationships
    customer = relationship("Customers", back_populates="product_consulting")
    ai_system = relationship("AISystem", back_populates="product_consulting")