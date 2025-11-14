
from sqlalchemy import Column, Integer, String, Date, DateTime, Enum as SQLEnum
from datetime import datetime
from sqlalchemy.orm import relationship
from app.enum.GenderEnum import GenderEnum
from app.core import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(255), nullable=False)
    dob = Column(Date, nullable=False)
    phone_number = Column(String(20), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    gender = Column(SQLEnum(GenderEnum), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    account = relationship("Account", back_populates="user")
    customer = relationship("Customers", back_populates="user", uselist=False)
    admin = relationship("Admin", back_populates="user", uselist=False)
    employee = relationship("Employees", back_populates="user", uselist=False)


# from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Enum as SQLEnum, ForeignKey, Text, Numeric, Boolean