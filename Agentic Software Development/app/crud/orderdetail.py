from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from fastapi import HTTPException, status
from app.models.orderdetail import OrderDetail
from app.models.order import Order
from app.models.product import Product
from app.schemas.orderdetail import OrderDetailCreate, OrderDetailUpdate
from app.core.logger import get_logger

logger = get_logger(__name__)

async def get_orderdetails(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[OrderDetail]:
    """Get all order details with pagination."""
    try:
        logger.info(f"Retrieving order details with skip={skip}, limit={limit}")
        result = await db.execute(
            select(OrderDetail)
            .offset(skip)
            .limit(limit)
            .order_by(OrderDetail.orderNumber, OrderDetail.productCode)
        )
        orderdetails = result.scalars().all()
        logger.info(f"Retrieved {len(orderdetails)} order details (skip={skip}, limit={limit})")
        return orderdetails
    except Exception as e:
        logger.error(f"Error retrieving order details: {e}")
        raise

async def get_orderdetail(db: AsyncSession, order_number: int, product_code: str) -> OrderDetail:
    """Get a single order detail by composite key."""
    try:
        logger.info(f"Retrieving order detail: order={order_number}, product={product_code}")
        result = await db.execute(
            select(OrderDetail).where(
                and_(
                    OrderDetail.orderNumber == order_number,
                    OrderDetail.productCode == product_code
                )
            )
        )
        orderdetail = result.scalar_one_or_none()
        
        if not orderdetail:
            logger.warning(f"Order detail not found: order={order_number}, product={product_code}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order detail with order {order_number} and product {product_code} not found"
            )
        
        logger.info(f"Retrieved order detail: order={order_number}, product={product_code}")
        return orderdetail
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving order detail order={order_number}, product={product_code}: {e}")
        raise

async def create_orderdetail(db: AsyncSession, orderdetail_data: OrderDetailCreate) -> OrderDetail:
    """Create a new order detail."""
    try:
        logger.info(f"Creating order detail: order={orderdetail_data.orderNumber}, product={orderdetail_data.productCode}")
        
        # Check if order detail already exists (composite key)
        existing = await db.execute(
            select(OrderDetail).where(
                and_(
                    OrderDetail.orderNumber == orderdetail_data.orderNumber,
                    OrderDetail.productCode == orderdetail_data.productCode
                )
            )
        )
        if existing.scalar_one_or_none():
            logger.warning(f"Order detail already exists: order={orderdetail_data.orderNumber}, product={orderdetail_data.productCode}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Order detail with order {orderdetail_data.orderNumber} and product {orderdetail_data.productCode} already exists"
            )
        
        # Check if order exists
        order_check = await db.execute(
            select(Order).where(Order.orderNumber == orderdetail_data.orderNumber)
        )
        if not order_check.scalar_one_or_none():
            logger.warning(f"Order not found: {orderdetail_data.orderNumber}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Order with number {orderdetail_data.orderNumber} does not exist"
            )
        
        # Check if product exists
        product_check = await db.execute(
            select(Product).where(Product.productCode == orderdetail_data.productCode)
        )
        if not product_check.scalar_one_or_none():
            logger.warning(f"Product not found: {orderdetail_data.productCode}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Product with code {orderdetail_data.productCode} does not exist"
            )
        
        # Check if line number already exists for this order
        line_number_check = await db.execute(
            select(OrderDetail).where(
                and_(
                    OrderDetail.orderNumber == orderdetail_data.orderNumber,
                    OrderDetail.orderLineNumber == orderdetail_data.orderLineNumber
                )
            )
        )
        if line_number_check.scalar_one_or_none():
            logger.warning(f"Line number already exists for order: order={orderdetail_data.orderNumber}, line={orderdetail_data.orderLineNumber}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Line number {orderdetail_data.orderLineNumber} already exists for order {orderdetail_data.orderNumber}"
            )
        
        # Create new order detail
        db_orderdetail = OrderDetail(**orderdetail_data.model_dump())
        db.add(db_orderdetail)
        await db.commit()
        await db.refresh(db_orderdetail)
        
        logger.info(f"Created order detail: order={orderdetail_data.orderNumber}, product={orderdetail_data.productCode}")
        return db_orderdetail
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating order detail order={orderdetail_data.orderNumber}, product={orderdetail_data.productCode}: {e}")
        raise

async def update_orderdetail(db: AsyncSession, order_number: int, product_code: str, orderdetail_data: OrderDetailUpdate) -> OrderDetail:
    """Update an existing order detail."""
    try:
        logger.info(f"Updating order detail: order={order_number}, product={product_code}")
        
        # Get existing order detail
        orderdetail = await get_orderdetail(db, order_number, product_code)
        
        # Update order detail with provided fields
        update_data = orderdetail_data.model_dump(exclude_unset=True)
        
        # Check line number uniqueness if it's being updated
        if 'orderLineNumber' in update_data:
            line_number_check = await db.execute(
                select(OrderDetail).where(
                    and_(
                        OrderDetail.orderNumber == order_number,
                        OrderDetail.orderLineNumber == update_data['orderLineNumber'],
                        OrderDetail.productCode != product_code
                    )
                )
            )
            if line_number_check.scalar_one_or_none():
                logger.warning(f"Line number already exists for order: order={order_number}, line={update_data['orderLineNumber']}")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Line number {update_data['orderLineNumber']} already exists for order {order_number}"
                )
        
        for field, value in update_data.items():
            setattr(orderdetail, field, value)
        
        await db.commit()
        await db.refresh(orderdetail)
        
        logger.info(f"Updated order detail: order={order_number}, product={product_code}")
        return orderdetail
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating order detail order={order_number}, product={product_code}: {e}")
        raise

async def delete_orderdetail(db: AsyncSession, order_number: int, product_code: str) -> bool:
    """Delete an order detail."""
    try:
        logger.info(f"Deleting order detail: order={order_number}, product={product_code}")
        
        # Get existing order detail
        orderdetail = await get_orderdetail(db, order_number, product_code)
        
        await db.delete(orderdetail)
        await db.commit()
        
        logger.info(f"Deleted order detail: order={order_number}, product={product_code}")
        return True
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting order detail order={order_number}, product={product_code}: {e}")
        raise

async def get_orderdetails_by_order(db: AsyncSession, order_number: int) -> List[OrderDetail]:
    """Get all order details for a specific order."""
    try:
        logger.info(f"Retrieving order details for order: {order_number}")
        
        # Check if order exists
        order_check = await db.execute(
            select(Order).where(Order.orderNumber == order_number)
        )
        if not order_check.scalar_one_or_none():
            logger.warning(f"Order not found: {order_number}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with number {order_number} not found"
            )
        
        # Get order details for this order
        result = await db.execute(
            select(OrderDetail).where(OrderDetail.orderNumber == order_number)
            .order_by(OrderDetail.orderLineNumber)
        )
        orderdetails = result.scalars().all()
        
        logger.info(f"Retrieved {len(orderdetails)} order details for order {order_number}")
        return orderdetails
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving order details for order {order_number}: {e}")
        raise

async def get_orderdetails_by_product(db: AsyncSession, product_code: str) -> List[OrderDetail]:
    """Get all order details for a specific product."""
    try:
        logger.info(f"Retrieving order details for product: {product_code}")
        
        # Check if product exists
        product_check = await db.execute(
            select(Product).where(Product.productCode == product_code)
        )
        if not product_check.scalar_one_or_none():
            logger.warning(f"Product not found: {product_code}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with code {product_code} not found"
            )
        
        # Get order details for this product
        result = await db.execute(
            select(OrderDetail).where(OrderDetail.productCode == product_code)
            .order_by(OrderDetail.orderNumber)
        )
        orderdetails = result.scalars().all()
        
        logger.info(f"Retrieved {len(orderdetails)} order details for product {product_code}")
        return orderdetails
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving order details for product {product_code}: {e}")
        raise

async def get_orderdetails_count(db: AsyncSession) -> int:
    """Get total count of order details."""
    try:
        logger.info("Getting total order detail count")
        result = await db.execute(select(func.count()))
        count = result.scalar() or 0
        logger.info(f"Total order detail count: {count}")
        return count
    except Exception as e:
        logger.error(f"Error getting order detail count: {e}")
        raise
