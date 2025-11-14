from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from app.enum.RoleEnum import RoleEnum
from app.enum.StatusAccountEnum import StatusAccountEnum
from sqlalchemy.orm import relationship

from app.core import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(RoleEnum), nullable=False)
    status = Column(SQLEnum(StatusAccountEnum), default=StatusAccountEnum.ACTIVE)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Quan hệ 1-1 với bảng Users
    user = relationship("Users", back_populates="account", uselist=False)
