from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from datetime import date
from enum import Enum

# Enum for order status
class OrderStatus(str, Enum):
    SHIPPED = "Shipped"
    RESOLVED = "Resolved"
    CANCELLED = "Cancelled"
    ON_HOLD = "On Hold"
    DISPUTED = "Disputed"
    IN_PROCESS = "In Process"

# Base schema with common fields
class OrderBase(BaseModel):
    orderDate: date = Field(..., description="Date the order was placed")
    requiredDate: date = Field(..., description="Date by which the order must be delivered")
    shippedDate: Optional[date] = Field(None, description="Actual ship date")
    status: OrderStatus = Field(..., description="Order status")
    comments: Optional[str] = Field(None, description="Order comments")
    customerNumber: int = Field(..., gt=0, description="Customer number foreign key")

    @field_validator('orderDate', 'requiredDate')
    @classmethod
    def validate_dates_not_future(cls, v):
        if v > date.today():
            raise ValueError('Date cannot be in the future')
        return v

    @field_validator('requiredDate')
    @classmethod
    def validate_required_date_after_order_date(cls, v, info):
        if 'orderDate' in info.data and v < info.data['orderDate']:
            raise ValueError('Required date must be after order date')
        return v

    @field_validator('shippedDate')
    @classmethod
    def validate_shipped_date_after_order_date(cls, v, info):
        if v is not None and 'orderDate' in info.data and v < info.data['orderDate']:
            raise ValueError('Shipped date cannot be before order date')
        return v

# Schema for creating new orders (orderNumber is provided by client)
class OrderCreate(OrderBase):
    orderNumber: int = Field(..., gt=0, description="Order number (primary key)")

# Schema for updating orders (all fields optional)
class OrderUpdate(BaseModel):
    orderDate: Optional[date] = Field(None, description="Date the order was placed")
    requiredDate: Optional[date] = Field(None, description="Date by which the order must be delivered")
    shippedDate: Optional[date] = Field(None, description="Actual ship date")
    status: Optional[OrderStatus] = Field(None, description="Order status")
    comments: Optional[str] = Field(None, description="Order comments")
    customerNumber: Optional[int] = Field(None, gt=0, description="Customer number foreign key")

    @field_validator('orderDate', 'requiredDate')
    @classmethod
    def validate_dates_not_future_update(cls, v):
        if v is not None and v > date.today():
            raise ValueError('Date cannot be in future')
        return v

    @field_validator('requiredDate')
    @classmethod
    def validate_required_date_after_order_date_update(cls, v, info):
        if v is not None and 'orderDate' in info.data and info.data['orderDate'] is not None:
            if v < info.data['orderDate']:
                raise ValueError('Required date must be after order date')
        return v

    @field_validator('shippedDate')
    @classmethod
    def validate_shipped_date_after_order_date_update(cls, v, info):
        if v is not None and 'orderDate' in info.data and info.data['orderDate'] is not None:
            if v < info.data['orderDate']:
                raise ValueError('Shipped date cannot be before order date')
        return v

# Schema for order output (includes orderNumber)
class OrderOut(OrderBase):
    orderNumber: int
    
    class Config:
        from_attributes = True

# Schema for order with order details
class OrderWithOrderDetails(OrderOut):
    orderdetails: List = Field(default=[], description="List of order details for this order")
    
    class Config:
        from_attributes = True

# Schema for order list response
class OrderList(BaseModel):
    orders: List[OrderOut]
    total: int
    skip: int
    limit: int
