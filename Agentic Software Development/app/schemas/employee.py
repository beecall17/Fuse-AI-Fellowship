from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, EmailStr
from datetime import date

# Base schema with common fields
class EmployeeBase(BaseModel):
    lastName: str = Field(..., min_length=1, max_length=50, description="Employee last name")
    firstName: str = Field(..., min_length=1, max_length=50, description="Employee first name")
    extension: str = Field(..., min_length=1, max_length=10, description="Phone extension")
    email: EmailStr = Field(..., description="Employee email address")
    officeCode: str = Field(..., min_length=1, max_length=10, description="Office code foreign key")
    reportsTo: Optional[int] = Field(None, description="Employee number this employee reports to")
    jobTitle: str = Field(..., min_length=1, max_length=50, description="Job title")

    @field_validator('lastName', 'firstName', 'extension', 'officeCode', 'jobTitle')
    @classmethod
    def validate_required_strings(cls, v):
        if v and len(v.strip()) == 0:
            raise ValueError('This field cannot be empty')
        return v.strip()

# Schema for creating new employees (employeeNumber is provided by client)
class EmployeeCreate(EmployeeBase):
    employeeNumber: int = Field(..., gt=0, description="Employee number (primary key)")

# Schema for updating employees (all fields optional)
class EmployeeUpdate(BaseModel):
    lastName: Optional[str] = Field(None, min_length=1, max_length=50)
    firstName: Optional[str] = Field(None, min_length=1, max_length=50)
    extension: Optional[str] = Field(None, min_length=1, max_length=10)
    email: Optional[EmailStr] = Field(None, description="Employee email address")
    officeCode: Optional[str] = Field(None, min_length=1, max_length=10)
    reportsTo: Optional[int] = Field(None, description="Employee number this employee reports to")
    jobTitle: Optional[str] = Field(None, min_length=1, max_length=50)

    @field_validator('lastName', 'firstName', 'extension', 'officeCode', 'jobTitle')
    @classmethod
    def validate_required_strings_update(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError('This field cannot be empty when provided')
        return v.strip() if v else v

# Schema for employee output (includes employeeNumber)
class EmployeeOut(EmployeeBase):
    employeeNumber: int
    
    class Config:
        from_attributes = True

# Schema for employee with customers
class EmployeeWithCustomers(EmployeeOut):
    customers: List = Field(default=[], description="List of customers managed by this employee")
    
    class Config:
        from_attributes = True

# Schema for employee with reports (employees who report to this employee)
class EmployeeWithReports(EmployeeOut):
    reports: List = Field(default=[], description="List of employees who report to this employee")
    
    class Config:
        from_attributes = True

# Schema for employee list response
class EmployeeList(BaseModel):
    employees: List[EmployeeOut]
    total: int
    skip: int
    limit: int
