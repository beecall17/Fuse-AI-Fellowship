from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class Payment(Base):
    """
    SQLAlchemy Payment model representing the payments table.
    """
    __tablename__ = "payments"
    
    customerNumber = Column(Integer, ForeignKey('customers.customerNumber'), primary_key=True, index=True)
    checkNumber = Column(String(50), primary_key=True)
    paymentDate = Column(Date, nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    
    # Relationships
    customer = relationship("Customer", back_populates="payments")
    
    def __repr__(self):
        return f"<Payment(customerNumber={self.customerNumber}, checkNumber='{self.checkNumber}', amount={self.amount})>"
