from app.core import Base
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey, Numeric
from datetime import datetime
from sqlalchemy.orm import relationship
from app.enum.PaymentStatusEnum import PaymentStatusEnum
from app.enum.OrderStatusEnum import OrderStatusEnum
from app.enum.PaymentMethodEnum import PaymentMethodEnum
class Orders(Base):
    __tablename__ = "orders"

    id = Column(String(50), primary_key=True, index=True)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False)
    order_date = Column(DateTime, default=datetime.now)
    total_amount = Column(Numeric(15, 2), nullable=False)
    payment_status = Column(SQLEnum(PaymentStatusEnum), default=PaymentStatusEnum.PENDING)
    order_status = Column(SQLEnum(OrderStatusEnum), default=OrderStatusEnum.PENDING)
    payment_method = Column(SQLEnum(PaymentMethodEnum), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    customer = relationship("Customers", back_populates="orders")
    order_details = relationship("OrderDetail", back_populates="order")
    reports = relationship("Reports", back_populates="order")