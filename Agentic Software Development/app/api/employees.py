from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.crud.employee import (
    get_employees,
    get_employee,
    create_employee,
    update_employee,
    delete_employee,
    get_employee_with_customers,
    get_employee_with_reports,
    get_employees_count
)
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeOut,
    EmployeeUpdate,
    EmployeeWithCustomers,
    EmployeeWithReports,
    EmployeeList
)
from app.core.logger import get_logger, log_api_request, log_api_response

router = APIRouter(prefix="/employees", tags=["Employees"])
logger = get_logger(__name__)

@router.get("/", response_model=EmployeeList)
async def list_employees(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """List all employees with pagination."""
    client_ip = request.client.host
    log_api_request(logger, "GET", f"/employees/?skip={skip}&limit={limit}", client_ip)
    
    try:
        employees = await get_employees(db, skip=skip, limit=limit)
        total = await get_employees_count(db)
        
        response = EmployeeList(
            employees=employees,
            total=total,
            skip=skip,
            limit=limit
        )
        
        log_api_response(logger, "GET", f"/employees/?skip={skip}&limit={limit}", 200)
        return response
    except HTTPException as e:
        log_api_response(logger, "GET", f"/employees/?skip={skip}&limit={limit}", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in list_employees: {e}")
        log_api_response(logger, "GET", f"/employees/?skip={skip}&limit={limit}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{employee_number}", response_model=EmployeeOut)
async def get_employee_by_number(
    request: Request,
    employee_number: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a single employee by employee number."""
    client_ip = request.client.host
    log_api_request(logger, "GET", f"/employees/{employee_number}", client_ip)
    
    try:
        employee = await get_employee(db, employee_number)
        log_api_response(logger, "GET", f"/employees/{employee_number}", 200)
        return employee
    except HTTPException as e:
        log_api_response(logger, "GET", f"/employees/{employee_number}", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in get_employee_by_number: {e}")
        log_api_response(logger, "GET", f"/employees/{employee_number}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{employee_number}/customers", response_model=EmployeeWithCustomers)
async def get_employee_with_customers(
    request: Request,
    employee_number: int,
    db: AsyncSession = Depends(get_db)
):
    """Get an employee with all their customers."""
    client_ip = request.client.host
    log_api_request(logger, "GET", f"/employees/{employee_number}/customers", client_ip)
    
    try:
        employee = await get_employee_with_customers(db, employee_number)
        log_api_response(logger, "GET", f"/employees/{employee_number}/customers", 200)
        return employee
    except HTTPException as e:
        log_api_response(logger, "GET", f"/employees/{employee_number}/customers", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in get_employee_with_customers: {e}")
        log_api_response(logger, "GET", f"/employees/{employee_number}/customers", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{employee_number}/reports", response_model=EmployeeWithReports)
async def get_employee_with_reports(
    request: Request,
    employee_number: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all employees who report to this employee."""
    client_ip = request.client.host
    log_api_request(logger, "GET", f"/employees/{employee_number}/reports", client_ip)
    
    try:
        employee = await get_employee_with_reports(db, employee_number)
        log_api_response(logger, "GET", f"/employees/{employee_number}/reports", 200)
        return employee
    except HTTPException as e:
        log_api_response(logger, "GET", f"/employees/{employee_number}/reports", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in get_employee_with_reports: {e}")
        log_api_response(logger, "GET", f"/employees/{employee_number}/reports", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/", response_model=EmployeeOut, status_code=201)
async def create_new_employee(
    request: Request,
    employee_data: EmployeeCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new employee."""
    client_ip = request.client.host
    log_api_request(logger, "POST", "/employees/", client_ip)
    
    try:
        employee = await create_employee(db, employee_data)
        log_api_response(logger, "POST", "/employees/", 201)
        return employee
    except HTTPException as e:
        log_api_response(logger, "POST", "/employees/", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in create_new_employee: {e}")
        log_api_response(logger, "POST", "/employees/", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{employee_number}", response_model=EmployeeOut)
async def update_employee_by_number(
    request: Request,
    employee_number: int,
    employee_data: EmployeeUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an employee by their number."""
    client_ip = request.client.host
    log_api_request(logger, "PUT", f"/employees/{employee_number}", client_ip)
    
    try:
        employee = await update_employee(db, employee_number, employee_data)
        log_api_response(logger, "PUT", f"/employees/{employee_number}", 200)
        return employee
    except HTTPException as e:
        log_api_response(logger, "PUT", f"/employees/{employee_number}", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in update_employee_by_number: {e}")
        log_api_response(logger, "PUT", f"/employees/{employee_number}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{employee_number}", status_code=204)
async def delete_employee_by_number(
    request: Request,
    employee_number: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete an employee by their number."""
    client_ip = request.client.host
    log_api_request(logger, "DELETE", f"/employees/{employee_number}", client_ip)
    
    try:
        await delete_employee(db, employee_number)
        log_api_response(logger, "DELETE", f"/employees/{employee_number}", 204)
        return None
    except HTTPException as e:
        log_api_response(logger, "DELETE", f"/employees/{employee_number}", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in delete_employee_by_number: {e}")
        log_api_response(logger, "DELETE", f"/employees/{employee_number}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")
