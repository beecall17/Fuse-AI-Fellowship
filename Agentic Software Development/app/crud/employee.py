from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status
from app.models.employee import Employee
from app.models.office import Office
from app.models.customer import Customer
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.core.logger import get_logger

logger = get_logger(__name__)

async def get_employees(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Employee]:
    """Get all employees with pagination."""
    try:
        logger.info(f"Retrieving employees with skip={skip}, limit={limit}")
        result = await db.execute(
            select(Employee)
            .offset(skip)
            .limit(limit)
            .order_by(Employee.employeeNumber)
        )
        employees = result.scalars().all()
        logger.info(f"Retrieved {len(employees)} employees (skip={skip}, limit={limit})")
        return employees
    except Exception as e:
        logger.error(f"Error retrieving employees: {e}")
        raise

async def get_employee(db: AsyncSession, employee_number: int) -> Employee:
    """Get a single employee by employee number."""
    try:
        logger.info(f"Retrieving employee: {employee_number}")
        result = await db.execute(
            select(Employee).where(Employee.employeeNumber == employee_number)
        )
        employee = result.scalar_one_or_none()
        
        if not employee:
            logger.warning(f"Employee not found: {employee_number}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with number {employee_number} not found"
            )
        
        logger.info(f"Retrieved employee: {employee_number}")
        return employee
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving employee {employee_number}: {e}")
        raise

async def create_employee(db: AsyncSession, employee_data: EmployeeCreate) -> Employee:
    """Create a new employee."""
    try:
        logger.info(f"Creating employee: {employee_data.employeeNumber}")
        
        # Check if employee number already exists
        existing = await db.execute(
            select(Employee).where(Employee.employeeNumber == employee_data.employeeNumber)
        )
        if existing.scalar_one_or_none():
            logger.warning(f"Employee number already exists: {employee_data.employeeNumber}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Employee with number {employee_data.employeeNumber} already exists"
            )
        
        # Check if email already exists
        email_check = await db.execute(
            select(Employee).where(Employee.email == employee_data.email)
        )
        if email_check.scalar_one_or_none():
            logger.warning(f"Email already exists: {employee_data.email}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Email {employee_data.email} already exists"
            )
        
        # Check if office exists
        office_check = await db.execute(
            select(Office).where(Office.officeCode == employee_data.officeCode)
        )
        if not office_check.scalar_one_or_none():
            logger.warning(f"Office not found: {employee_data.officeCode}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Office with code {employee_data.officeCode} does not exist"
            )
        
        # Check if reportsTo exists (if provided)
        if employee_data.reportsTo:
            reports_check = await db.execute(
                select(Employee).where(Employee.employeeNumber == employee_data.reportsTo)
            )
            if not reports_check.scalar_one_or_none():
                logger.warning(f"ReportsTo employee not found: {employee_data.reportsTo}")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Employee with number {employee_data.reportsTo} does not exist"
                )
        
        # Create new employee
        db_employee = Employee(**employee_data.model_dump())
        db.add(db_employee)
        await db.commit()
        await db.refresh(db_employee)
        
        logger.info(f"Created employee: {employee_data.employeeNumber}")
        return db_employee
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating employee {employee_data.employeeNumber}: {e}")
        raise

async def update_employee(db: AsyncSession, employee_number: int, employee_data: EmployeeUpdate) -> Employee:
    """Update an existing employee."""
    try:
        logger.info(f"Updating employee: {employee_number}")
        
        # Get existing employee
        result = await db.execute(
            select(Employee).where(Employee.employeeNumber == employee_number)
        )
        employee = result.scalar_one_or_none()
        
        if not employee:
            logger.warning(f"Employee not found for update: {employee_number}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with number {employee_number} not found"
            )
        
        # Update employee with provided fields
        update_data = employee_data.model_dump(exclude_unset=True)
        
        # Validate foreign keys if they're being updated
        if 'officeCode' in update_data:
            office_check = await db.execute(
                select(Office).where(Office.officeCode == update_data['officeCode'])
            )
            if not office_check.scalar_one_or_none():
                logger.warning(f"Office not found: {update_data['officeCode']}")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Office with code {update_data['officeCode']} does not exist"
                )
        
        if 'reportsTo' in update_data and update_data['reportsTo']:
            reports_check = await db.execute(
                select(Employee).where(Employee.employeeNumber == update_data['reportsTo'])
            )
            if not reports_check.scalar_one_or_none():
                logger.warning(f"ReportsTo employee not found: {update_data['reportsTo']}")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Employee with number {update_data['reportsTo']} does not exist"
                )
        
        if 'email' in update_data:
            email_check = await db.execute(
                select(Employee).where(
                    Employee.email == update_data['email'],
                    Employee.employeeNumber != employee_number
                )
            )
            if email_check.scalar_one_or_none():
                logger.warning(f"Email already exists: {update_data['email']}")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Email {update_data['email']} already exists"
                )
        
        for field, value in update_data.items():
            setattr(employee, field, value)
        
        await db.commit()
        await db.refresh(employee)
        
        logger.info(f"Updated employee: {employee_number}")
        return employee
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating employee {employee_number}: {e}")
        raise

async def delete_employee(db: AsyncSession, employee_number: int) -> bool:
    """Delete an employee."""
    try:
        logger.info(f"Deleting employee: {employee_number}")
        
        # Get existing employee
        result = await db.execute(
            select(Employee).where(Employee.employeeNumber == employee_number)
        )
        employee = result.scalar_one_or_none()
        
        if not employee:
            logger.warning(f"Employee not found for deletion: {employee_number}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with number {employee_number} not found"
            )
        
        # Check if employee has direct reports
        reports_check = await db.execute(
            select(Employee).where(Employee.reportsTo == employee_number)
        )
        if reports_check.scalar_one_or_none():
            logger.warning(f"Cannot delete employee {employee_number}: has direct reports")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot delete employee {employee_number}: they have direct reports"
            )
        
        # Check if employee is assigned as sales rep to customers
        customers_check = await db.execute(
            select(Customer).where(Customer.salesRepEmployeeNumber == employee_number)
        )
        if customers_check.scalar_one_or_none():
            logger.warning(f"Cannot delete employee {employee_number}: has customers")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot delete employee {employee_number}: they are assigned as sales rep to customers"
            )
        
        await db.delete(employee)
        await db.commit()
        
        logger.info(f"Deleted employee: {employee_number}")
        return True
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting employee {employee_number}: {e}")
        raise

async def get_employee_with_customers(db: AsyncSession, employee_number: int) -> Employee:
    """Get an employee with all their customers."""
    try:
        logger.info(f"Retrieving employee with customers: {employee_number}")
        
        # Get employee
        employee = await get_employee(db, employee_number)
        
        # Get customers for this employee
        customers_result = await db.execute(
            select(Customer).where(Customer.salesRepEmployeeNumber == employee_number)
            .order_by(Customer.customerName)
        )
        customers = customers_result.scalars().all()
        
        # Attach customers to employee
        employee.customers = list(customers)
        
        logger.info(f"Retrieved employee {employee_number} with {len(customers)} customers")
        return employee
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving employee {employee_number} with customers: {e}")
        raise

async def get_employee_with_reports(db: AsyncSession, employee_number: int) -> Employee:
    """Get an employee with all employees who report to them."""
    try:
        logger.info(f"Retrieving employee with reports: {employee_number}")
        
        # Get employee
        employee = await get_employee(db, employee_number)
        
        # Get employees who report to this employee
        reports_result = await db.execute(
            select(Employee).where(Employee.reportsTo == employee_number)
            .order_by(Employee.lastName, Employee.firstName)
        )
        reports = reports_result.scalars().all()
        
        # Attach reports to employee
        employee.reports = list(reports)
        
        logger.info(f"Retrieved employee {employee_number} with {len(reports)} direct reports")
        return employee
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving employee {employee_number} with reports: {e}")
        raise

async def get_employees_count(db: AsyncSession) -> int:
    """Get total count of employees."""
    try:
        logger.info("Getting total employee count")
        result = await db.execute(select(func.count(Employee.employeeNumber)))
        count = result.scalar() or 0
        logger.info(f"Total employee count: {count}")
        return count
    except Exception as e:
        logger.error(f"Error getting employee count: {e}")
        raise
