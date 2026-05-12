from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status
from app.models.product import Product
from app.models.orderdetail import OrderDetail
from app.models.productline import ProductLine
from app.schemas.product import ProductCreate, ProductUpdate
from app.core.logger import get_logger

logger = get_logger(__name__)

async def get_products(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Product]:
    """Get all products with pagination."""
    try:
        logger.info(f"Retrieving products with skip={skip}, limit={limit}")
        result = await db.execute(
            select(Product)
            .offset(skip)
            .limit(limit)
            .order_by(Product.productCode)
        )
        products = result.scalars().all()
        logger.info(f"Retrieved {len(products)} products (skip={skip}, limit={limit})")
        return products
    except Exception as e:
        logger.error(f"Error retrieving products: {e}")
        raise

async def get_product(db: AsyncSession, product_code: str) -> Product:
    """Get a single product by product code."""
    try:
        logger.info(f"Retrieving product: {product_code}")
        result = await db.execute(
            select(Product).where(Product.productCode == product_code)
        )
        product = result.scalar_one_or_none()
        
        if not product:
            logger.warning(f"Product not found: {product_code}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with code {product_code} not found"
            )
        
        logger.info(f"Retrieved product: {product_code}")
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving product {product_code}: {e}")
        raise

async def create_product(db: AsyncSession, product_data: ProductCreate) -> Product:
    """Create a new product."""
    try:
        logger.info(f"Creating product: {product_data.productCode}")
        
        # Check if product code already exists
        existing = await db.execute(
            select(Product).where(Product.productCode == product_data.productCode)
        )
        if existing.scalar_one_or_none():
            logger.warning(f"Product code already exists: {product_data.productCode}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Product with code {product_data.productCode} already exists"
            )
        
        # Check if product line exists
        productline_check = await db.execute(
            select(ProductLine).where(ProductLine.productLine == product_data.productLine)
        )
        if not productline_check.scalar_one_or_none():
            logger.warning(f"Product line not found: {product_data.productLine}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Product line '{product_data.productLine}' does not exist"
            )
        
        # Create new product
        db_product = Product(**product_data.model_dump())
        db.add(db_product)
        await db.commit()
        await db.refresh(db_product)
        
        logger.info(f"Created product: {product_data.productCode}")
        return db_product
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating product {product_data.productCode}: {e}")
        raise

async def update_product(db: AsyncSession, product_code: str, product_data: ProductUpdate) -> Product:
    """Update an existing product."""
    try:
        logger.info(f"Updating product: {product_code}")
        
        # Get existing product
        result = await db.execute(
            select(Product).where(Product.productCode == product_code)
        )
        product = result.scalar_one_or_none()
        
        if not product:
            logger.warning(f"Product not found for update: {product_code}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with code {product_code} not found"
            )
        
        # Check product line if it's being updated
        if product_data.productLine:
            productline_check = await db.execute(
                select(ProductLine).where(ProductLine.productLine == product_data.productLine)
            )
            if not productline_check.scalar_one_or_none():
                logger.warning(f"Product line not found: {product_data.productLine}")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Product line '{product_data.productLine}' does not exist"
                )
        
        # Update product with provided fields
        update_data = product_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        
        await db.commit()
        await db.refresh(product)
        
        logger.info(f"Updated product: {product_code}")
        return product
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating product {product_code}: {e}")
        raise

async def delete_product(db: AsyncSession, product_code: str) -> bool:
    """Delete a product."""
    try:
        logger.info(f"Deleting product: {product_code}")
        
        # Get existing product
        result = await db.execute(
            select(Product).where(Product.productCode == product_code)
        )
        product = result.scalar_one_or_none()
        
        if not product:
            logger.warning(f"Product not found for deletion: {product_code}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with code {product_code} not found"
            )
        
        # Check if product has order details
        orderdetails_check = await db.execute(
            select(OrderDetail).where(OrderDetail.productCode == product_code)
        )
        if orderdetails_check.scalar_one_or_none():
            logger.warning(f"Cannot delete product {product_code}: has order details")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot delete product {product_code}: it has associated order details"
            )
        
        await db.delete(product)
        await db.commit()
        
        logger.info(f"Deleted product: {product_code}")
        return True
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting product {product_code}: {e}")
        raise

async def get_product_with_orderdetails(db: AsyncSession, product_code: str) -> Product:
    """Get a product with all its order details."""
    try:
        logger.info(f"Retrieving product with order details: {product_code}")
        
        # Get product
        product = await get_product(db, product_code)
        
        # Get order details for this product
        orderdetails_result = await db.execute(
            select(OrderDetail).where(OrderDetail.productCode == product_code)
            .order_by(OrderDetail.orderNumber)
        )
        orderdetails = orderdetails_result.scalars().all()
        
        # Attach order details to product
        product.orderdetails = list(orderdetails)
        
        logger.info(f"Retrieved product {product_code} with {len(orderdetails)} order details")
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving product {product_code} with order details: {e}")
        raise

async def get_products_count(db: AsyncSession) -> int:
    """Get total count of products."""
    try:
        logger.info("Getting total product count")
        result = await db.execute(select(func.count(Product.productCode)))
        count = result.scalar() or 0
        logger.info(f"Total product count: {count}")
        return count
    except Exception as e:
        logger.error(f"Error getting product count: {e}")
        raise
