from pydantic import BaseModel, Field

class CountResponse(BaseModel):
    """
    Schema for individual count responses.
    """
    count: int = Field(..., ge=0, description="Total number of records")
    table: str = Field(..., description="Table name")

class OverallCounts(BaseModel):
    """
    Schema for aggregated counts from all tables.
    """
    customers: int = Field(..., ge=0, description="Total customers")
    orders: int = Field(..., ge=0, description="Total orders")
    products: int = Field(..., ge=0, description="Total products")
    employees: int = Field(..., ge=0, description="Total employees")
    offices: int = Field(..., ge=0, description="Total offices")
    payments: int = Field(..., ge=0, description="Total payments")
    orderdetails: int = Field(..., ge=0, description="Total order details")
    productlines: int = Field(..., ge=0, description="Total product lines")
