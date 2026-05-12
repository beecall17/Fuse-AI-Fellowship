from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

# Base schema with common fields
class ProductLineBase(BaseModel):
    textDescription: Optional[str] = Field(None, max_length=4000, description="Plain text description")
    htmlDescription: Optional[str] = Field(None, description="HTML description")
    image: Optional[bytes] = Field(None, description="Binary image data")

    @field_validator('textDescription')
    @classmethod
    def validate_text_description(cls, v):
        if v is not None and len(v.strip()) == 0:
            return None
        return v

    @field_validator('htmlDescription')
    @classmethod
    def validate_html_description(cls, v):
        if v is not None and len(v.strip()) == 0:
            return None
        return v

# Schema for creating new product lines (productLine is provided by client)
class ProductLineCreate(ProductLineBase):
    productLine: str = Field(..., min_length=1, max_length=50, description="Product line name (primary key)")

    @field_validator('productLine')
    @classmethod
    def validate_product_line(cls, v):
        if v and len(v.strip()) == 0:
            raise ValueError('Product line cannot be empty')
        return v.strip()

# Schema for updating product lines (all fields optional)
class ProductLineUpdate(BaseModel):
    textDescription: Optional[str] = Field(None, max_length=4000)
    htmlDescription: Optional[str] = Field(None)
    image: Optional[bytes] = Field(None)

    @field_validator('textDescription')
    @classmethod
    def validate_text_description_update(cls, v):
        if v is not None and len(v.strip()) == 0:
            return None
        return v

    @field_validator('htmlDescription')
    @classmethod
    def validate_html_description_update(cls, v):
        if v is not None and len(v.strip()) == 0:
            return None
        return v

# Schema for product line output (includes productLine)
class ProductLineOut(ProductLineBase):
    productLine: str
    
    class Config:
        from_attributes = True

# Schema for product line with products
class ProductLineWithProducts(ProductLineOut):
    products: List = Field(default=[], description="List of products in this product line")
    
    class Config:
        from_attributes = True

# Schema for product line list response
class ProductLineList(BaseModel):
    productlines: List[ProductLineOut]
    total: int
    skip: int
    limit: int
