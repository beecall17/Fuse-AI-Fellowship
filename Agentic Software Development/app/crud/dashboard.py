from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from app.models.customer import Customer
from app.models.order import Order
from app.models.product import Product
from app.models.employee import Employee
from app.models.office import Office
from app.models.payment import Payment
from app.models.orderdetail import OrderDetail
from app.models.productline import ProductLine
from app.core.logger import get_logger

logger = get_logger(__name__)

async def get_customer_count(db: AsyncSession) -> int:
    """Get total number of customers."""
    try:
        logger.info("Starting customer count query")
        result = await db.execute(select(func.count(Customer.customerNumber)))
        count = result.scalar() or 0
        logger.info(f"Customer count query completed: {count} records")
        return count
    except Exception as e:
        logger.error(f"Error getting customer count: {e}")
        raise

async def get_order_count(db: AsyncSession) -> int:
    """Get total number of orders."""
    try:
        logger.info("Starting order count query")
        result = await db.execute(select(func.count(Order.orderNumber)))
        count = result.scalar() or 0
        logger.info(f"Order count query completed: {count} records")
        return count
    except Exception as e:
        logger.error(f"Error getting order count: {e}")
        raise

async def get_product_count(db: AsyncSession) -> int:
    """Get total number of products."""
    try:
        logger.info("Starting product count query")
        result = await db.execute(select(func.count(Product.productCode)))
        count = result.scalar() or 0
        logger.info(f"Product count query completed: {count} records")
        return count
    except Exception as e:
        logger.error(f"Error getting product count: {e}")
        raise

async def get_employee_count(db: AsyncSession) -> int:
    """Get total number of employees."""
    try:
        logger.info("Starting employee count query")
        result = await db.execute(select(func.count(Employee.employeeNumber)))
        count = result.scalar() or 0
        logger.info(f"Employee count query completed: {count} records")
        return count
    except Exception as e:
        logger.error(f"Error getting employee count: {e}")
        raise

async def get_office_count(db: AsyncSession) -> int:
    """Get total number of offices."""
    try:
        logger.info("Starting office count query")
        result = await db.execute(select(func.count(Office.officeCode)))
        count = result.scalar() or 0
        logger.info(f"Office count query completed: {count} records")
        return count
    except Exception as e:
        logger.error(f"Error getting office count: {e}")
        raise

async def get_payment_count(db: AsyncSession) -> int:
    """Get total number of payments."""
    try:
        logger.info("Starting payment count query")
        result = await db.execute(select(func.count(Payment.customerNumber)))
        count = result.scalar() or 0
        logger.info(f"Payment count query completed: {count} records")
        return count
    except Exception as e:
        logger.error(f"Error getting payment count: {e}")
        raise

async def get_orderdetail_count(db: AsyncSession) -> int:
    """Get total number of order details."""
    try:
        logger.info("Starting orderdetail count query")
        result = await db.execute(select(func.count(OrderDetail.orderNumber)))
        count = result.scalar() or 0
        logger.info(f"OrderDetail count query completed: {count} records")
        return count
    except Exception as e:
        logger.error(f"Error getting orderdetail count: {e}")
        raise

async def get_productline_count(db: AsyncSession) -> int:
    """Get total number of product lines."""
    try:
        logger.info("Starting productline count query")
        result = await db.execute(select(func.count(ProductLine.productLine)))
        count = result.scalar() or 0
        logger.info(f"ProductLine count query completed: {count} records")
        return count
    except Exception as e:
        logger.error(f"Error getting productline count: {e}")
        raise

async def get_all_counts_concurrent(db: AsyncSession) -> Dict[str, int]:
    """
    Get counts from all tables concurrently using asyncio.gather().
    This is the main function for the dashboard endpoint.
    """
    import time
    import asyncio
    
    start_time = time.time()
    logger.info("Starting concurrent count queries for all tables")
    
    try:
        # Start all queries concurrently
        tasks = [
            get_customer_count(db),
            get_order_count(db),
            get_product_count(db),
            get_employee_count(db),
            get_office_count(db),
            get_payment_count(db),
            get_orderdetail_count(db),
            get_productline_count(db)
        ]
        
        # Wait for all queries to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        counts = {
            "customers": results[0] if not isinstance(results[0], Exception) else 0,
            "orders": results[1] if not isinstance(results[1], Exception) else 0,
            "products": results[2] if not isinstance(results[2], Exception) else 0,
            "employees": results[3] if not isinstance(results[3], Exception) else 0,
            "offices": results[4] if not isinstance(results[4], Exception) else 0,
            "payments": results[5] if not isinstance(results[5], Exception) else 0,
            "orderdetails": results[6] if not isinstance(results[6], Exception) else 0,
            "productlines": results[7] if not isinstance(results[7], Exception) else 0
        }
        
        # Log any exceptions that occurred
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                table_names = ["customers", "orders", "products", "employees", "offices", "payments", "orderdetails", "productlines"]
                logger.error(f"Error in {table_names[i]} count query: {result}")
        
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Concurrent count queries completed in {execution_time:.3f} seconds")
        
        return counts
        
    except Exception as e:
        logger.error(f"Error in concurrent count queries: {e}")
        raise
