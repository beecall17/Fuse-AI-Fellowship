from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class Order(Base):
    """
    SQLAlchemy Order model representing the orders table.
    """
    __tablename__ = "orders"
    
    orderNumber = Column(Integer, primary_key=True, index=True)
    orderDate = Column(Date, nullable=False, index=True)
    requiredDate = Column(Date, nullable=False)
    shippedDate = Column(Date, nullable=True)
    status = Column(String(15), nullable=False, index=True)
    comments = Column(Text, nullable=True)
    customerNumber = Column(Integer, ForeignKey('customers.customerNumber'), nullable=False, index=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="orders")
    orderdetails = relationship("OrderDetail", back_populates="order")
    
    def __repr__(self):
        return f"<Order(orderNumber={self.orderNumber}, customerNumber={self.customerNumber})>"
