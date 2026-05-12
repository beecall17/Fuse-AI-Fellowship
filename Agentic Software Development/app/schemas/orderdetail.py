from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal

# Base schema with common fields
class OrderDetailBase(BaseModel):
    quantityOrdered: int = Field(..., gt=0, description="Quantity of this product ordered")
    priceEach: Decimal = Field(..., gt=0, decimal_places=2, description="Price per unit at time of order")
    orderLineNumber: int = Field(..., gt=0, description="Line number within the order")

    @field_validator('quantityOrdered')
    @classmethod
    def validate_quantity_positive(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v

    @field_validator('priceEach')
    @classmethod
    def validate_price_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        return v

    @field_validator('orderLineNumber')
    @classmethod
    def validate_line_number_positive(cls, v):
        if v <= 0:
            raise ValueError('Line number must be greater than 0')
        return v

# Schema for creating new order details (composite primary key provided by client)
class OrderDetailCreate(OrderDetailBase):
    orderNumber: int = Field(..., gt=0, description="Order number (part of primary key)")
    productCode: str = Field(..., min_length=1, max_length=15, description="Product code (part of primary key)")

    @field_validator('productCode')
    @classmethod
    def validate_product_code(cls, v):
        if v and len(v.strip()) == 0:
            raise ValueError('Product code cannot be empty')
        return v.strip()

# Schema for updating order details (all fields optional)
class OrderDetailUpdate(BaseModel):
    quantityOrdered: Optional[int] = Field(None, gt=0, description="Quantity of this product ordered")
    priceEach: Optional[Decimal] = Field(None, gt=0, decimal_places=2, description="Price per unit at time of order")
    orderLineNumber: Optional[int] = Field(None, gt=0, description="Line number within the order")

    @field_validator('quantityOrdered')
    @classmethod
    def validate_quantity_positive_update(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v

    @field_validator('priceEach')
    @classmethod
    def validate_price_positive_update(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Price must be greater than 0')
        return v

    @field_validator('orderLineNumber')
    @classmethod
    def validate_line_number_positive_update(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Line number must be greater than 0')
        return v

# Schema for order detail output (includes composite primary key)
class OrderDetailOut(OrderDetailBase):
    orderNumber: int
    productCode: str
    
    class Config:
        from_attributes = True

# Schema for order detail list response
class OrderDetailList(BaseModel):
    orderdetails: List[OrderDetailOut]
    total: int
    skip: int
    limit: int
