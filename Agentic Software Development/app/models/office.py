from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.database.session import Base

class Office(Base):
    """
    SQLAlchemy Office model representing the offices table.
    """
    __tablename__ = "offices"
    
    officeCode = Column(String(10), primary_key=True, index=True)
    city = Column(String(50), nullable=False, index=True)
    phone = Column(String(50), nullable=False)
    addressLine1 = Column(String(50), nullable=False)
    addressLine2 = Column(String(50), nullable=True)
    state = Column(String(50), nullable=True)
    country = Column(String(50), nullable=False)
    postalCode = Column(String(15), nullable=False)
    territory = Column(String(10), nullable=False)
    
    # Relationships
    employees = relationship("Employee", back_populates="office")
    
    def __repr__(self):
        return f"<Office(officeCode='{self.officeCode}', city='{self.city}')>"
