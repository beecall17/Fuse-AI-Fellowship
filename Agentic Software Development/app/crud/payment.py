from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from fastapi import HTTPException, status
from app.models.payment import Payment
from app.models.customer import Customer
from app.schemas.payment import PaymentCreate, PaymentUpdate
from app.core.logger import get_logger

logger = get_logger(__name__)

async def get_payments(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Payment]:
    """Get all payments with pagination."""
    try:
        logger.info(f"Retrieving payments with skip={skip}, limit={limit}")
        result = await db.execute(
            select(Payment)
            .offset(skip)
            .limit(limit)
            .order_by(Payment.customerNumber, Payment.checkNumber)
        )
        payments = result.scalars().all()
        logger.info(f"Retrieved {len(payments)} payments (skip={skip}, limit={limit})")
        return payments
    except Exception as e:
        logger.error(f"Error retrieving payments: {e}")
        raise

async def get_payment(db: AsyncSession, customer_number: int, check_number: str) -> Payment:
    """Get a single payment by composite key."""
    try:
        logger.info(f"Retrieving payment: customer={customer_number}, check={check_number}")
        result = await db.execute(
            select(Payment).where(
                and_(
                    Payment.customerNumber == customer_number,
                    Payment.checkNumber == check_number
                )
            )
        )
        payment = result.scalar_one_or_none()
        
        if not payment:
            logger.warning(f"Payment not found: customer={customer_number}, check={check_number}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment with customer {customer_number} and check {check_number} not found"
            )
        
        logger.info(f"Retrieved payment: customer={customer_number}, check={check_number}")
        return payment
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving payment customer={customer_number}, check={check_number}: {e}")
        raise

async def create_payment(db: AsyncSession, payment_data: PaymentCreate) -> Payment:
    """Create a new payment."""
    try:
        logger.info(f"Creating payment: customer={payment_data.customerNumber}, check={payment_data.checkNumber}")
        
        # Check if payment already exists (composite key)
        existing = await db.execute(
            select(Payment).where(
                and_(
                    Payment.customerNumber == payment_data.customerNumber,
                    Payment.checkNumber == payment_data.checkNumber
                )
            )
        )
        if existing.scalar_one_or_none():
            logger.warning(f"Payment already exists: customer={payment_data.customerNumber}, check={payment_data.checkNumber}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Payment with customer {payment_data.customerNumber} and check {payment_data.checkNumber} already exists"
            )
        
        # Check if customer exists
        customer_check = await db.execute(
            select(Customer).where(Customer.customerNumber == payment_data.customerNumber)
        )
        if not customer_check.scalar_one_or_none():
            logger.warning(f"Customer not found: {payment_data.customerNumber}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Customer with number {payment_data.customerNumber} does not exist"
            )
        
        # Create new payment
        db_payment = Payment(**payment_data.model_dump())
        db.add(db_payment)
        await db.commit()
        await db.refresh(db_payment)
        
        logger.info(f"Created payment: customer={payment_data.customerNumber}, check={payment_data.checkNumber}")
        return db_payment
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating payment customer={payment_data.customerNumber}, check={payment_data.checkNumber}: {e}")
        raise

async def update_payment(db: AsyncSession, customer_number: int, check_number: str, payment_data: PaymentUpdate) -> Payment:
    """Update an existing payment."""
    try:
        logger.info(f"Updating payment: customer={customer_number}, check={check_number}")
        
        # Get existing payment
        payment = await get_payment(db, customer_number, check_number)
        
        # Update payment with provided fields
        update_data = payment_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(payment, field, value)
        
        await db.commit()
        await db.refresh(payment)
        
        logger.info(f"Updated payment: customer={customer_number}, check={check_number}")
        return payment
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating payment customer={customer_number}, check={check_number}: {e}")
        raise

async def delete_payment(db: AsyncSession, customer_number: int, check_number: str) -> bool:
    """Delete a payment."""
    try:
        logger.info(f"Deleting payment: customer={customer_number}, check={check_number}")
        
        # Get existing payment
        payment = await get_payment(db, customer_number, check_number)
        
        await db.delete(payment)
        await db.commit()
        
        logger.info(f"Deleted payment: customer={customer_number}, check={check_number}")
        return True
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting payment customer={customer_number}, check={check_number}: {e}")
        raise

async def get_payments_by_customer(db: AsyncSession, customer_number: int) -> List[Payment]:
    """Get all payments for a specific customer."""
    try:
        logger.info(f"Retrieving payments for customer: {customer_number}")
        
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
        
        # Get payments for this customer
        result = await db.execute(
            select(Payment).where(Payment.customerNumber == customer_number)
            .order_by(Payment.paymentDate.desc())
        )
        payments = result.scalars().all()
        
        logger.info(f"Retrieved {len(payments)} payments for customer {customer_number}")
        return payments
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving payments for customer {customer_number}: {e}")
        raise

async def get_payments_count(db: AsyncSession) -> int:
    """Get total count of payments."""
    try:
        logger.info("Getting total payment count")
        result = await db.execute(select(func.count()))
        count = result.scalar() or 0
        logger.info(f"Total payment count: {count}")
        return count
    except Exception as e:
        logger.error(f"Error getting payment count: {e}")
        raise
