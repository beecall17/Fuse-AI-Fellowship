from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import relationship
from app.database.session import Base

class Customer(Base):
    """
    SQLAlchemy Customer model representing the customers table.
    """
    __tablename__ = "customers"
    
    customerNumber = Column(Integer, primary_key=True, index=True)
    customerName = Column(String(50), nullable=False, index=True)
    contactLastName = Column(String(50), nullable=False)
    contactFirstName = Column(String(50), nullable=False)
    phone = Column(String(50), nullable=False)
    addressLine1 = Column(String(50), nullable=False)
    addressLine2 = Column(String(50), nullable=True)
    city = Column(String(50), nullable=False)
    state = Column(String(50), nullable=True)
    postalCode = Column(String(15), nullable=True)
    country = Column(String(50), nullable=False)
    salesRepEmployeeNumber = Column(Integer, nullable=True)
    creditLimit = Column(Numeric(10, 2), nullable=True)
    
    # Relationships
    # orders = relationship("Order", back_populates="customer")
    # payments = relationship("Payment", back_populates="customer")
    
    def __repr__(self):
        return f"<Customer(customerNumber={self.customerNumber}, customerName='{self.customerName}')>"
