from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

# Base schema with common fields
class OfficeBase(BaseModel):
    city: str = Field(..., min_length=1, max_length=50, description="City name")
    phone: str = Field(..., min_length=1, max_length=50, description="Phone number")
    addressLine1: str = Field(..., min_length=1, max_length=50, description="Address line 1")
    addressLine2: Optional[str] = Field(None, max_length=50, description="Address line 2")
    state: Optional[str] = Field(None, max_length=50, description="State or region")
    country: str = Field(..., min_length=1, max_length=50, description="Country name")
    postalCode: str = Field(..., min_length=1, max_length=15, description="Postal code")
    territory: str = Field(..., min_length=1, max_length=10, description="Sales territory")

    @field_validator('city', 'phone', 'addressLine1', 'country', 'postalCode', 'territory')
    @classmethod
    def validate_required_strings(cls, v):
        if v and len(v.strip()) == 0:
            raise ValueError('This field cannot be empty')
        return v.strip()

    @field_validator('addressLine2', 'state')
    @classmethod
    def validate_optional_strings(cls, v):
        if v is not None and len(v.strip()) == 0:
            return None
        return v.strip() if v else v

# Schema for creating new offices (officeCode is provided by client)
class OfficeCreate(OfficeBase):
    officeCode: str = Field(..., min_length=1, max_length=10, description="Office code (primary key)")

    @field_validator('officeCode')
    @classmethod
    def validate_office_code(cls, v):
        if v and len(v.strip()) == 0:
            raise ValueError('Office code cannot be empty')
        return v.strip()

# Schema for updating offices (all fields optional)
class OfficeUpdate(BaseModel):
    city: Optional[str] = Field(None, min_length=1, max_length=50)
    phone: Optional[str] = Field(None, min_length=1, max_length=50)
    addressLine1: Optional[str] = Field(None, min_length=1, max_length=50)
    addressLine2: Optional[str] = Field(None, max_length=50)
    state: Optional[str] = Field(None, max_length=50)
    country: Optional[str] = Field(None, min_length=1, max_length=50)
    postalCode: Optional[str] = Field(None, min_length=1, max_length=15)
    territory: Optional[str] = Field(None, min_length=1, max_length=10)

    @field_validator('city', 'phone', 'addressLine1', 'country', 'postalCode', 'territory')
    @classmethod
    def validate_required_strings_update(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError('This field cannot be empty when provided')
        return v.strip() if v else v

    @field_validator('addressLine2', 'state')
    @classmethod
    def validate_optional_strings_update(cls, v):
        if v is not None and len(v.strip()) == 0:
            return None
        return v.strip() if v else v

# Schema for office output (includes officeCode)
class OfficeOut(OfficeBase):
    officeCode: str
    
    class Config:
        from_attributes = True

# Schema for office with employees
class OfficeWithEmployees(OfficeOut):
    employees: List = Field(default=[], description="List of employees in this office")
    
    class Config:
        from_attributes = True

# Schema for office list response
class OfficeList(BaseModel):
    offices: List[OfficeOut]
    total: int
    skip: int
    limit: int
