from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status
from app.models.order import Order
from app.models.customer import Customer
from app.models.orderdetail import OrderDetail
from app.schemas.order import OrderCreate, OrderUpdate
from app.core.logger import get_logger

logger = get_logger(__name__)

async def get_orders(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Order]:
    """Get all orders with pagination."""
    try:
        logger.info(f"Retrieving orders with skip={skip}, limit={limit}")
        result = await db.execute(
            select(Order)
            .offset(skip)
            .limit(limit)
            .order_by(Order.orderNumber)
        )
        orders = result.scalars().all()
        logger.info(f"Retrieved {len(orders)} orders (skip={skip}, limit={limit})")
        return orders
    except Exception as e:
        logger.error(f"Error retrieving orders: {e}")
        raise

async def get_order(db: AsyncSession, order_number: int) -> Order:
    """Get a single order by order number."""
    try:
        logger.info(f"Retrieving order: {order_number}")
        result = await db.execute(
            select(Order).where(Order.orderNumber == order_number)
        )
        order = result.scalar_one_or_none()
        
        if not order:
            logger.warning(f"Order not found: {order_number}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with number {order_number} not found"
            )
        
        logger.info(f"Retrieved order: {order_number}")
        return order
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving order {order_number}: {e}")
        raise

async def create_order(db: AsyncSession, order_data: OrderCreate) -> Order:
    """Create a new order."""
    try:
        logger.info(f"Creating order: {order_data.orderNumber}")
        
        # Check if order number already exists
        existing = await db.execute(
            select(Order).where(Order.orderNumber == order_data.orderNumber)
        )
        if existing.scalar_one_or_none():
            logger.warning(f"Order number already exists: {order_data.orderNumber}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Order with number {order_data.orderNumber} already exists"
            )
        
        # Check if customer exists
        customer_check = await db.execute(
            select(Customer).where(Customer.customerNumber == order_data.customerNumber)
        )
        if not customer_check.scalar_one_or_none():
            logger.warning(f"Customer not found: {order_data.customerNumber}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Customer with number {order_data.customerNumber} does not exist"
            )
        
        # Create new order
        db_order = Order(**order_data.model_dump())
        db.add(db_order)
        await db.commit()
        await db.refresh(db_order)
        
        logger.info(f"Created order: {order_data.orderNumber}")
        return db_order
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating order {order_data.orderNumber}: {e}")
        raise

async def update_order(db: AsyncSession, order_number: int, order_data: OrderUpdate) -> Order:
    """Update an existing order."""
    try:
        logger.info(f"Updating order: {order_number}")
        
        # Get existing order
        result = await db.execute(
            select(Order).where(Order.orderNumber == order_number)
        )
        order = result.scalar_one_or_none()
        
        if not order:
            logger.warning(f"Order not found for update: {order_number}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with number {order_number} not found"
            )
        
        # Update order with provided fields
        update_data = order_data.model_dump(exclude_unset=True)
        
        # Validate customer if it's being updated
        if 'customerNumber' in update_data:
            customer_check = await db.execute(
                select(Customer).where(Customer.customerNumber == update_data['customerNumber'])
            )
            if not customer_check.scalar_one_or_none():
                logger.warning(f"Customer not found: {update_data['customerNumber']}")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Customer with number {update_data['customerNumber']} does not exist"
                )
        
        for field, value in update_data.items():
            setattr(order, field, value)
        
        await db.commit()
        await db.refresh(order)
        
        logger.info(f"Updated order: {order_number}")
        return order
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating order {order_number}: {e}")
        raise

async def delete_order(db: AsyncSession, order_number: int) -> bool:
    """Delete an order."""
    try:
        logger.info(f"Deleting order: {order_number}")
        
        # Get existing order
        result = await db.execute(
            select(Order).where(Order.orderNumber == order_number)
        )
        order = result.scalar_one_or_none()
        
        if not order:
            logger.warning(f"Order not found for deletion: {order_number}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with number {order_number} not found"
            )
        
        # Check if order has order details
        orderdetails_check = await db.execute(
            select(OrderDetail).where(OrderDetail.orderNumber == order_number)
        )
        if orderdetails_check.scalar_one_or_none():
            logger.warning(f"Cannot delete order {order_number}: has order details")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot delete order {order_number}: it has associated order details"
            )
        
        await db.delete(order)
        await db.commit()
        
        logger.info(f"Deleted order: {order_number}")
        return True
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting order {order_number}: {e}")
        raise

async def get_order_with_orderdetails(db: AsyncSession, order_number: int) -> Order:
    """Get an order with all its order details."""
    try:
        logger.info(f"Retrieving order with order details: {order_number}")
        
        # Get order
        order = await get_order(db, order_number)
        
        # Get order details for this order
        orderdetails_result = await db.execute(
            select(OrderDetail).where(OrderDetail.orderNumber == order_number)
            .order_by(OrderDetail.orderLineNumber)
        )
        orderdetails = orderdetails_result.scalars().all()
        
        # Attach order details to order
        order.orderdetails = list(orderdetails)
        
        logger.info(f"Retrieved order {order_number} with {len(orderdetails)} order details")
        return order
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving order {order_number} with order details: {e}")
        raise

async def get_orders_by_customer(db: AsyncSession, customer_number: int) -> List[Order]:
    """Get all orders for a specific customer."""
    try:
        logger.info(f"Retrieving orders for customer: {customer_number}")
        
        # Check if customer exists
        customer_check = await db.execute(
            select(Customer).where(Customer.customerNumber == customer_number)
        )
        if not customer_check.scalar_one_or_none():
            logger.warning(f"Customer not found: {customer_number}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with number {customer_number} not found"
            )
        
        # Get orders for this customer
        result = await db.execute(
            select(Order).where(Order.customerNumber == customer_number)
            .order_by(Order.orderNumber)
        )
        orders = result.scalars().all()
        
        logger.info(f"Retrieved {len(orders)} orders for customer {customer_number}")
        return orders
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving orders for customer {customer_number}: {e}")
        raise

async def get_orders_count(db: AsyncSession) -> int:
    """Get total count of orders."""
    try:
        logger.info("Getting total order count")
        result = await db.execute(select(func.count(Order.orderNumber)))
        count = result.scalar() or 0
        logger.info(f"Total order count: {count}")
        return count
    except Exception as e:
        logger.error(f"Error getting order count: {e}")
        raise
