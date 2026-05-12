from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from datetime import date

# Base schema with common fields
class PaymentBase(BaseModel):
    paymentDate: date = Field(..., description="Date of payment")
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Payment amount")

    @field_validator('paymentDate')
    @classmethod
    def validate_payment_date_not_future(cls, v):
        if v > date.today():
            raise ValueError('Payment date cannot be in the future')
        return v

    @field_validator('amount')
    @classmethod
    def validate_amount_positive(cls, v):
        if v <= 0:
            raise ValueError('Payment amount must be greater than 0')
        return v

# Schema for creating new payments (composite primary key provided by client)
class PaymentCreate(PaymentBase):
    customerNumber: int = Field(..., gt=0, description="Customer number (part of primary key)")
    checkNumber: str = Field(..., min_length=1, max_length=50, description="Check number (part of primary key)")

    @field_validator('checkNumber')
    @classmethod
    def validate_check_number(cls, v):
        if v and len(v.strip()) == 0:
            raise ValueError('Check number cannot be empty')
        return v.strip()

# Schema for updating payments (all fields optional)
class PaymentUpdate(BaseModel):
    paymentDate: Optional[date] = Field(None, description="Date of payment")
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2, description="Payment amount")

    @field_validator('paymentDate')
    @classmethod
    def validate_payment_date_not_future_update(cls, v):
        if v is not None and v > date.today():
            raise ValueError('Payment date cannot be in the future')
        return v

    @field_validator('amount')
    @classmethod
    def validate_amount_positive_update(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Payment amount must be greater than 0')
        return v

# Schema for payment output (includes composite primary key)
class PaymentOut(PaymentBase):
    customerNumber: int
    checkNumber: str
    
    class Config:
        from_attributes = True

# Schema for payment list response
class PaymentList(BaseModel):
    payments: List[PaymentOut]
    total: int
    skip: int
    limit: int
