from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status
from app.models.office import Office
from app.models.employee import Employee
from app.schemas.office import OfficeCreate, OfficeUpdate
from app.core.logger import get_logger

logger = get_logger(__name__)

async def get_offices(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Office]:
    """Get all offices with pagination."""
    try:
        logger.info(f"Retrieving offices with skip={skip}, limit={limit}")
        result = await db.execute(
            select(Office)
            .offset(skip)
            .limit(limit)
            .order_by(Office.officeCode)
        )
        offices = result.scalars().all()
        logger.info(f"Retrieved {len(offices)} offices (skip={skip}, limit={limit})")
        return offices
    except Exception as e:
        logger.error(f"Error retrieving offices: {e}")
        raise

async def get_office(db: AsyncSession, office_code: str) -> Office:
    """Get a single office by office code."""
    try:
        logger.info(f"Retrieving office: {office_code}")
        result = await db.execute(
            select(Office).where(Office.officeCode == office_code)
        )
        office = result.scalar_one_or_none()
        
        if not office:
            logger.warning(f"Office not found: {office_code}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Office with code {office_code} not found"
            )
        
        logger.info(f"Retrieved office: {office_code}")
        return office
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving office {office_code}: {e}")
        raise

async def create_office(db: AsyncSession, office_data: OfficeCreate) -> Office:
    """Create a new office."""
    try:
        logger.info(f"Creating office: {office_data.officeCode}")
        
        # Check if office code already exists
        existing = await db.execute(
            select(Office).where(Office.officeCode == office_data.officeCode)
        )
        if existing.scalar_one_or_none():
            logger.warning(f"Office code already exists: {office_data.officeCode}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Office with code {office_data.officeCode} already exists"
            )
        
        # Create new office
        db_office = Office(**office_data.model_dump())
        db.add(db_office)
        await db.commit()
        await db.refresh(db_office)
        
        logger.info(f"Created office: {office_data.officeCode}")
        return db_office
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating office {office_data.officeCode}: {e}")
        raise

async def update_office(db: AsyncSession, office_code: str, office_data: OfficeUpdate) -> Office:
    """Update an existing office."""
    try:
        logger.info(f"Updating office: {office_code}")
        
        # Get existing office
        result = await db.execute(
            select(Office).where(Office.officeCode == office_code)
        )
        office = result.scalar_one_or_none()
        
        if not office:
            logger.warning(f"Office not found for update: {office_code}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Office with code {office_code} not found"
            )
        
        # Update office with provided fields
        update_data = office_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(office, field, value)
        
        await db.commit()
        await db.refresh(office)
        
        logger.info(f"Updated office: {office_code}")
        return office
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating office {office_code}: {e}")
        raise

async def delete_office(db: AsyncSession, office_code: str) -> bool:
    """Delete an office."""
    try:
        logger.info(f"Deleting office: {office_code}")
        
        # Get existing office
        result = await db.execute(
            select(Office).where(Office.officeCode == office_code)
        )
        office = result.scalar_one_or_none()
        
        if not office:
            logger.warning(f"Office not found for deletion: {office_code}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Office with code {office_code} not found"
            )
        
        # Check if office has employees
        employees_check = await db.execute(
            select(Employee).where(Employee.officeCode == office_code)
        )
        if employees_check.scalar_one_or_none():
            logger.warning(f"Cannot delete office {office_code}: has employees")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot delete office {office_code}: it has associated employees"
            )
        
        await db.delete(office)
        await db.commit()
        
        logger.info(f"Deleted office: {office_code}")
        return True
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting office {office_code}: {e}")
        raise

async def get_office_with_employees(db: AsyncSession, office_code: str) -> Office:
    """Get an office with all its employees."""
    try:
        logger.info(f"Retrieving office with employees: {office_code}")
        
        # Get office
        office = await get_office(db, office_code)
        
        # Get employees for this office
        employees_result = await db.execute(
            select(Employee).where(Employee.officeCode == office_code)
            .order_by(Employee.lastName, Employee.firstName)
        )
        employees = employees_result.scalars().all()
        
        # Attach employees to office
        office.employees = list(employees)
        
        logger.info(f"Retrieved office {office_code} with {len(employees)} employees")
        return office
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving office {office_code} with employees: {e}")
        raise

async def get_offices_count(db: AsyncSession) -> int:
    """Get total count of offices."""
    try:
        logger.info("Getting total office count")
        result = await db.execute(select(func.count(Office.officeCode)))
        count = result.scalar() or 0
        logger.info(f"Total office count: {count}")
        return count
    except Exception as e:
        logger.error(f"Error getting office count: {e}")
        raise
