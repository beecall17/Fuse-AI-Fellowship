from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class Product(Base):
    """
    SQLAlchemy Product model representing the products table.
    """
    __tablename__ = "products"
    
    productCode = Column(String(15), primary_key=True, index=True)
    productName = Column(String(70), nullable=False, index=True)
    productLine = Column(String(50), ForeignKey('productlines.productLine'), nullable=False, index=True)
    productScale = Column(String(10), nullable=False)
    productVendor = Column(String(50), nullable=False)
    productDescription = Column(Text, nullable=False)
    quantityInStock = Column(Integer, nullable=False)
    buyPrice = Column(Numeric(10, 2), nullable=False)
    MSRP = Column(Numeric(10, 2), nullable=False)
    
    # Relationships
    productline = relationship("ProductLine", back_populates="products")
    orderdetails = relationship("OrderDetail", back_populates="product")
    
    def __repr__(self):
        return f"<Product(productCode={self.productCode}, productName='{self.productName}')>"
