from app.core import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from datetime import datetime
from sqlalchemy.orm import relationship


class ProductItemImage(Base):
    __tablename__ = "product_item_images"

    id = Column(Integer, primary_key=True, index=True)
    product_item_id = Column(String(50), ForeignKey("product_items.id"), nullable=False)

    image_url = Column(Text, nullable=False)
    alt_text = Column(String(255), nullable=True)
    sort_order = Column(Integer, default=0)
    is_main = Column(Boolean, default=False)  # Ảnh chính của biến thể

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    product_item = relationship("ProductItem", back_populates="images")
