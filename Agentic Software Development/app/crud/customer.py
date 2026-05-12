from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, update
from sqlalchemy.orm import selectinload
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.core.logger import get_logger

logger = get_logger(__name__)

async def get_customer(db: AsyncSession, customer_number: int) -> Optional[Customer]:
    """
    Get a single customer by customerNumber.
    
    Args:
        db: Async database session
        customer_number: Customer number to retrieve
        
    Returns:
        Customer object if found, None otherwise
    """
    try:
        result = await db.execute(
            select(Customer).where(Customer.customerNumber == customer_number)
        )
        customer = result.scalar_one_or_none()
        
        if customer:
            logger.info(f"Retrieved customer: {customer_number}")
        else:
            logger.warning(f"Customer not found: {customer_number}")
            
        return customer
    except Exception as e:
        logger.error(f"Error retrieving customer {customer_number}: {e}")
        raise

async def get_customers(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100
) -> Tuple[List[Customer], int]:
    """
    Get all customers with pagination.
    
    Args:
        db: Async database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        Tuple of (list of customers, total count)
    """
    try:
        # Get total count
        count_result = await db.execute(select(func.count(Customer.customerNumber)))
        total = count_result.scalar()
        
        # Get paginated results
        result = await db.execute(
            select(Customer)
            .offset(skip)
            .limit(limit)
            .order_by(Customer.customerNumber)
        )
        customers = result.scalars().all()
        
        logger.info(f"Retrieved {len(customers)} customers (skip={skip}, limit={limit}, total={total})")
        return list(customers), total
    except Exception as e:
        logger.error(f"Error retrieving customers: {e}")
        raise

async def get_customer_with_orders(
    db: AsyncSession, 
    customer_number: int
) -> Optional[Customer]:
    """
    Get a customer with their orders and payments.
    
    Args:
        db: Async database session
        customer_number: Customer number to retrieve
        
    Returns:
        Customer object with related data if found, None otherwise
    """
    try:
        result = await db.execute(
            select(Customer)
            .options(
                selectinload(Customer.orders),
                selectinload(Customer.payments)
            )
            .where(Customer.customerNumber == customer_number)
        )
        customer = result.scalar_one_or_none()
        
        if customer:
            logger.info(f"Retrieved customer with orders: {customer_number}")
        else:
            logger.warning(f"Customer not found: {customer_number}")
            
        return customer
    except Exception as e:
        logger.error(f"Error retrieving customer with orders {customer_number}: {e}")
        raise

async def create_customer(
    db: AsyncSession, 
    customer: CustomerCreate
) -> Customer:
    """
    Create a new customer.
    
    Args:
        db: Async database session
        customer: Customer data to create
        
    Returns:
        Created customer object
    """
    try:
        # Get the next customer number
        max_result = await db.execute(select(func.max(Customer.customerNumber)))
        max_number = max_result.scalar() or 0
        new_customer_number = max_number + 1
        
        # Create customer object
        db_customer = Customer(
            customerNumber=new_customer_number,
            **customer.dict()
        )
        
        db.add(db_customer)
        await db.commit()
        await db.refresh(db_customer)
        
        logger.info(f"Created customer: {new_customer_number}")
        return db_customer
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating customer: {e}")
        raise

async def update_customer(
    db: AsyncSession, 
    customer_number: int, 
    customer_update: CustomerUpdate
) -> Optional[Customer]:
    """
    Update an existing customer.
    
    Args:
        db: Async database session
        customer_number: Customer number to update
        customer_update: Updated customer data
        
    Returns:
        Updated customer object if found, None otherwise
    """
    try:
        # Check if customer exists
        existing_customer = await get_customer(db, customer_number)
        if not existing_customer:
            logger.warning(f"Cannot update - customer not found: {customer_number}")
            return None
        
        # Update only provided fields
        update_data = customer_update.dict(exclude_unset=True)
        if not update_data:
            logger.info(f"No fields to update for customer: {customer_number}")
            return existing_customer
        
        await db.execute(
            update(Customer)
            .where(Customer.customerNumber == customer_number)
            .values(**update_data)
        )
        await db.commit()
        
        # Get updated customer
        updated_customer = await get_customer(db, customer_number)
        logger.info(f"Updated customer: {customer_number}")
        return updated_customer
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating customer {customer_number}: {e}")
        raise

async def delete_customer(
    db: AsyncSession, 
    customer_number: int
) -> bool:
    """
    Delete a customer.
    
    Args:
        db: Async database session
        customer_number: Customer number to delete
        
    Returns:
        True if deleted, False if not found
    """
    try:
        # Check if customer exists
        existing_customer = await get_customer(db, customer_number)
        if not existing_customer:
            logger.warning(f"Cannot delete - customer not found: {customer_number}")
            return False
        
        result = await db.execute(
            delete(Customer).where(Customer.customerNumber == customer_number)
        )
        await db.commit()
        
        logger.info(f"Deleted customer: {customer_number}")
        return result.rowcount > 0
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting customer {customer_number}: {e}")
        raise
