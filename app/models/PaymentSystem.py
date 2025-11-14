from app.core import Base
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
class PaymentSystem(Base):
    __tablename__ = "payment_systems"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)

    # Relationships
    payment = relationship("Payments", back_populates="payment_system")