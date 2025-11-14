from app.core import Base
from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship

class Employees(Base):
    __tablename__ = "employees"

    employee_id = Column(String(50), primary_key=True, index=True)
    salary = Column(Numeric(15, 2), nullable=False)
    hire_date = Column(Date, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    user = relationship("Users", back_populates="employee")
