from sqlalchemy import Column, String, Text, LargeBinary
from sqlalchemy.orm import relationship
from app.database.session import Base

class ProductLine(Base):
    """
    SQLAlchemy ProductLine model representing the productlines table.
    """
    __tablename__ = "productlines"
    
    productLine = Column(String(50), primary_key=True, index=True)
    textDescription = Column(String(4000), nullable=True)
    htmlDescription = Column(Text, nullable=True)
    image = Column(LargeBinary, nullable=True)
    
    # Relationships
    products = relationship("Product", back_populates="productline")
    
    def __repr__(self):
        return f"<ProductLine(productLine='{self.productLine}')>"
