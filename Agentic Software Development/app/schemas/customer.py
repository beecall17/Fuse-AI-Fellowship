from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

# Base schema with common fields
class CustomerBase(BaseModel):
    customerName: str = Field(..., min_length=1, max_length=50, description="Customer name")
    contactLastName: str = Field(..., min_length=1, max_length=50, description="Contact last name")
    contactFirstName: str = Field(..., min_length=1, max_length=50, description="Contact first name")
    phone: str = Field(..., min_length=1, max_length=50, description="Phone number")
    addressLine1: str = Field(..., min_length=1, max_length=50, description="Address line 1")
    addressLine2: Optional[str] = Field(None, max_length=50, description="Address line 2")
    city: str = Field(..., min_length=1, max_length=50, description="City")
    state: Optional[str] = Field(None, max_length=50, description="State")
    postalCode: Optional[str] = Field(None, max_length=15, description="Postal code")
    country: str = Field(..., min_length=1, max_length=50, description="Country")
    salesRepEmployeeNumber: Optional[int] = Field(None, description="Sales representative employee number")
    creditLimit: Optional[Decimal] = Field(None, ge=0, description="Credit limit")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v and len(v.strip()) == 0:
            raise ValueError('Phone number cannot be empty')
        return v.strip()

    @field_validator('customerName', 'contactLastName', 'contactFirstName', 'addressLine1', 'city', 'country')
    @classmethod
    def validate_required_strings(cls, v):
        if v and len(v.strip()) == 0:
            raise ValueError('This field cannot be empty')
        return v.strip()

# Schema for creating new customers (no customerNumber)
class CustomerCreate(CustomerBase):
    pass

# Schema for updating customers (all fields optional)
class CustomerUpdate(BaseModel):
    customerName: Optional[str] = Field(None, min_length=1, max_length=50)
    contactLastName: Optional[str] = Field(None, min_length=1, max_length=50)
    contactFirstName: Optional[str] = Field(None, min_length=1, max_length=50)
    phone: Optional[str] = Field(None, min_length=1, max_length=50)
    addressLine1: Optional[str] = Field(None, min_length=1, max_length=50)
    addressLine2: Optional[str] = Field(None, max_length=50)
    city: Optional[str] = Field(None, min_length=1, max_length=50)
    state: Optional[str] = Field(None, max_length=50)
    postalCode: Optional[str] = Field(None, max_length=15)
    country: Optional[str] = Field(None, min_length=1, max_length=50)
    salesRepEmployeeNumber: Optional[int] = None
    creditLimit: Optional[Decimal] = Field(None, ge=0)

    @field_validator('customerName', 'contactLastName', 'contactFirstName', 'addressLine1', 'city', 'country')
    @classmethod
    def validate_optional_strings(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError('This field cannot be empty when provided')
        return v.strip() if v else v

# Schema for customer output (includes customerNumber)
class CustomerOut(CustomerBase):
    customerNumber: int
    
    class Config:
        from_attributes = True

# Schema for customer with related data
class CustomerWithOrders(CustomerOut):
    orders: Optional[List['OrderOut']] = []
    payments: Optional[List['PaymentOut']] = []

# Order schema for related data
class OrderOut(BaseModel):
    orderNumber: int
    orderDate: datetime
    requiredDate: datetime
    shippedDate: Optional[datetime]
    status: str
    
    class Config:
        from_attributes = True

# Payment schema for related data
class PaymentOut(BaseModel):
    checkNumber: str
    paymentDate: datetime
    amount: Decimal
    
    class Config:
        from_attributes = True

# Schema for paginated response
class CustomerList(BaseModel):
    customers: List[CustomerOut]
    total: int
    skip: int
    limit: int
