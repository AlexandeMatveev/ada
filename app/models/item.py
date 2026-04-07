from sqlalchemy import Column, Integer, String, Float, DateTime,ForeignKey,Text,Boolean
from core.database import Base

from sqlalchemy.orm import relationship, sessionmaker

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    price = Column(Float)  # Добавьте
    stock = Column(Integer)  # Добавьте
    is_available = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"))



    order_items = relationship("OrderItem", back_populates="item", cascade="all, delete-orphan")
    owner = relationship("User", back_populates="items")