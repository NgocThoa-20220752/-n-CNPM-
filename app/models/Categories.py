from app.core import Base
from sqlalchemy import Column, Integer, String, DateTime,Text, ForeignKey
from datetime import datetime
from sqlalchemy.orm import relationship

class Categories(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    parent_category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Self-referencing relationship
    parent_category = relationship("Categories", remote_side=[id], backref="sub_categories")

    # Relationships
    products = relationship("Products", back_populates="category")