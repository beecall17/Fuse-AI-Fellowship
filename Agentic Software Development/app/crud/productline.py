from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status
from app.models.productline import ProductLine
from app.models.product import Product
from app.schemas.productline import ProductLineCreate, ProductLineUpdate
from app.core.logger import get_logger

logger = get_logger(__name__)

async def get_productlines(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[ProductLine]:
    """Get all product lines with pagination."""
    try:
        logger.info(f"Retrieving product lines with skip={skip}, limit={limit}")
        result = await db.execute(
            select(ProductLine)
            .offset(skip)
            .limit(limit)
            .order_by(ProductLine.productLine)
        )
        productlines = result.scalars().all()
        logger.info(f"Retrieved {len(productlines)} product lines (skip={skip}, limit={limit})")
        return productlines
    except Exception as e:
        logger.error(f"Error retrieving product lines: {e}")
        raise

async def get_productline(db: AsyncSession, product_line: str) -> ProductLine:
    """Get a single product line by name."""
    try:
        logger.info(f"Retrieving product line: {product_line}")
        result = await db.execute(
            select(ProductLine).where(ProductLine.productLine == product_line)
        )
        productline = result.scalar_one_or_none()
        
        if not productline:
            logger.warning(f"Product line not found: {product_line}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product line '{product_line}' not found"
            )
        
        logger.info(f"Retrieved product line: {product_line}")
        return productline
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving product line {product_line}: {e}")
        raise

async def create_productline(db: AsyncSession, productline_data: ProductLineCreate) -> ProductLine:
    """Create a new product line."""
    try:
        logger.info(f"Creating product line: {productline_data.productLine}")
        
        # Check if product line already exists
        existing = await db.execute(
            select(ProductLine).where(ProductLine.productLine == productline_data.productLine)
        )
        if existing.scalar_one_or_none():
            logger.warning(f"Product line already exists: {productline_data.productLine}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Product line '{productline_data.productLine}' already exists"
            )
        
        # Create new product line
        db_productline = ProductLine(**productline_data.model_dump())
        db.add(db_productline)
        await db.commit()
        await db.refresh(db_productline)
        
        logger.info(f"Created product line: {productline_data.productLine}")
        return db_productline
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating product line {productline_data.productLine}: {e}")
        raise

async def update_productline(db: AsyncSession, product_line: str, productline_data: ProductLineUpdate) -> ProductLine:
    """Update an existing product line."""
    try:
        logger.info(f"Updating product line: {product_line}")
        
        # Get existing product line
        result = await db.execute(
            select(ProductLine).where(ProductLine.productLine == product_line)
        )
        productline = result.scalar_one_or_none()
        
        if not productline:
            logger.warning(f"Product line not found for update: {product_line}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product line '{product_line}' not found"
            )
        
        # Update product line with provided fields
        update_data = productline_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(productline, field, value)
        
        await db.commit()
        await db.refresh(productline)
        
        logger.info(f"Updated product line: {product_line}")
        return productline
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating product line {product_line}: {e}")
        raise

async def delete_productline(db: AsyncSession, product_line: str) -> bool:
    """Delete a product line."""
    try:
        logger.info(f"Deleting product line: {product_line}")
        
        # Get existing product line
        result = await db.execute(
            select(ProductLine).where(ProductLine.productLine == product_line)
        )
        productline = result.scalar_one_or_none()
        
        if not productline:
            logger.warning(f"Product line not found for deletion: {product_line}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product line '{product_line}' not found"
            )
        
        # Check if product line has products
        products_check = await db.execute(
            select(Product).where(Product.productLine == product_line)
        )
        if products_check.scalar_one_or_none():
            logger.warning(f"Cannot delete product line {product_line}: has products")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot delete product line '{product_line}': it has associated products"
            )
        
        await db.delete(productline)
        await db.commit()
        
        logger.info(f"Deleted product line: {product_line}")
        return True
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting product line {product_line}: {e}")
        raise

async def get_productline_with_products(db: AsyncSession, product_line: str) -> ProductLine:
    """Get a product line with all its products."""
    try:
        logger.info(f"Retrieving product line with products: {product_line}")
        
        # Get product line
        productline = await get_productline(db, product_line)
        
        # Get products for this product line
        products_result = await db.execute(
            select(Product).where(Product.productLine == product_line)
            .order_by(Product.productCode)
        )
        products = products_result.scalars().all()
        
        # Attach products to product line
        productline.products = list(products)
        
        logger.info(f"Retrieved product line {product_line} with {len(products)} products")
        return productline
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving product line {product_line} with products: {e}")
        raise

async def get_productlines_count(db: AsyncSession) -> int:
    """Get total count of product lines."""
    try:
        logger.info("Getting total product line count")
        result = await db.execute(select(func.count(ProductLine.productLine)))
        count = result.scalar() or 0
        logger.info(f"Total product line count: {count}")
        return count
    except Exception as e:
        logger.error(f"Error getting product line count: {e}")
        raise
