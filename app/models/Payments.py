from app.core import Base
from sqlalchemy import Column, Integer, Date, Enum as SQLEnum
from datetime import date
from sqlalchemy.orm import relationship
from app.enum.PaymentMethodEnum import PaymentMethodEnum
from app.enum.StatusAccountEnum import StatusAccountEnum

class Payments(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    method = Column(SQLEnum(PaymentMethodEnum), nullable=False)
    status = Column(SQLEnum(StatusAccountEnum), default=StatusAccountEnum.ACTIVE)
    created_at = Column(Date, default=date.today)

    # Relationships
    payment_system = relationship("PaymentSystem", back_populates="payment")