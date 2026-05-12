from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator

# Base schema with common fields
class ProductBase(BaseModel):
    productName: str = Field(..., min_length=1, max_length=70, description="Product name")
    productLine: str = Field(..., min_length=1, max_length=50, description="Product line foreign key")
    productScale: str = Field(..., min_length=1, max_length=10, description="Product scale")
    productVendor: str = Field(..., min_length=1, max_length=50, description="Product vendor")
    productDescription: str = Field(..., min_length=1, description="Product description")
    quantityInStock: int = Field(..., ge=0, description="Quantity in stock")
    buyPrice: Decimal = Field(..., ge=0, decimal_places=2, description="Buy price")
    MSRP: Decimal = Field(..., ge=0, decimal_places=2, description="Manufacturer suggested retail price")

    @field_validator('productName', 'productLine', 'productScale', 'productVendor')
    @classmethod
    def validate_required_strings(cls, v):
        if v and len(v.strip()) == 0:
            raise ValueError('This field cannot be empty')
        return v.strip()

    @field_validator('MSRP')
    @classmethod
    def validate_msrp_ge_buy_price(cls, v, info):
        if 'buyPrice' in info.data and v < info.data['buyPrice']:
            raise ValueError('MSRP must be greater than or equal to buy price')
        return v

# Schema for creating new products (productCode is provided by client)
class ProductCreate(ProductBase):
    productCode: str = Field(..., min_length=1, max_length=15, description="Product code (primary key)")

    @field_validator('productCode')
    @classmethod
    def validate_product_code(cls, v):
        if v and len(v.strip()) == 0:
            raise ValueError('Product code cannot be empty')
        return v.strip()

# Schema for updating products (all fields optional)
class ProductUpdate(BaseModel):
    productName: Optional[str] = Field(None, min_length=1, max_length=70)
    productLine: Optional[str] = Field(None, min_length=1, max_length=50)
    productScale: Optional[str] = Field(None, min_length=1, max_length=10)
    productVendor: Optional[str] = Field(None, min_length=1, max_length=50)
    productDescription: Optional[str] = Field(None, min_length=1)
    quantityInStock: Optional[int] = Field(None, ge=0)
    buyPrice: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    MSRP: Optional[Decimal] = Field(None, ge=0, decimal_places=2)

    @field_validator('productName', 'productLine', 'productScale', 'productVendor')
    @classmethod
    def validate_optional_strings(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError('This field cannot be empty when provided')
        return v.strip() if v else v

    @field_validator('MSRP')
    @classmethod
    def validate_msrp_ge_buy_price_update(cls, v, info):
        if v is not None and 'buyPrice' in info.data and info.data['buyPrice'] is not None:
            if v < info.data['buyPrice']:
                raise ValueError('MSRP must be greater than or equal to buy price')
        return v

# Schema for product output (includes productCode)
class ProductOut(ProductBase):
    productCode: str
    
    class Config:
        from_attributes = True

# Schema for product with order details
class ProductWithOrderDetails(ProductOut):
    orderdetails: list = Field(default=[], description="List of order details for this product")
    
    class Config:
        from_attributes = True

# Schema for product list response
class ProductList(BaseModel):
    products: list[ProductOut]
    total: int
    skip: int
    limit: int
