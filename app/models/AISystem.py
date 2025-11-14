from app.core import Base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
class AISystem(Base):
    __tablename__ = "ai_systems"

    id_ai = Column(Integer, primary_key=True, index=True, autoincrement=True)
    model = Column(String(255), nullable=False)
    accuracy = Column(Float, nullable=False)

    # Relationships
    product_consulting = relationship("ProductConsulting", back_populates="ai_system")

