from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, SmallInteger
from sqlalchemy.orm import relationship
from app.database.session import Base

class OrderDetail(Base):
    """
    SQLAlchemy OrderDetail model representing the orderdetails table.
    """
    __tablename__ = "orderdetails"
    
    orderNumber = Column(Integer, ForeignKey('orders.orderNumber'), primary_key=True, index=True)
    productCode = Column(String(15), ForeignKey('products.productCode'), primary_key=True)
    quantityOrdered = Column(Integer, nullable=False)
    priceEach = Column(Numeric(10, 2), nullable=False)
    orderLineNumber = Column(SmallInteger, nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="orderdetails")
    product = relationship("Product", back_populates="orderdetails")
    
    def __repr__(self):
        return f"<OrderDetail(orderNumber={self.orderNumber}, productCode='{self.productCode}')>"
