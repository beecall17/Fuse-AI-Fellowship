from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.crud.office import (
    get_offices,
    get_office,
    create_office,
    update_office,
    delete_office,
    get_office_with_employees,
    get_offices_count
)
from app.schemas.office import (
    OfficeCreate,
    OfficeOut,
    OfficeUpdate,
    OfficeWithEmployees,
    OfficeList
)
from app.core.logger import get_logger, log_api_request, log_api_response

router = APIRouter(prefix="/offices", tags=["Offices"])
logger = get_logger(__name__)

@router.get("/", response_model=OfficeList)
async def list_offices(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """List all offices with pagination."""
    client_ip = request.client.host
    log_api_request(logger, "GET", f"/offices/?skip={skip}&limit={limit}", client_ip)
    
    try:
        offices = await get_offices(db, skip=skip, limit=limit)
        total = await get_offices_count(db)
        
        response = OfficeList(
            offices=offices,
            total=total,
            skip=skip,
            limit=limit
        )
        
        log_api_response(logger, "GET", f"/offices/?skip={skip}&limit={limit}", 200)
        return response
    except HTTPException as e:
        log_api_response(logger, "GET", f"/offices/?skip={skip}&limit={limit}", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in list_offices: {e}")
        log_api_response(logger, "GET", f"/offices/?skip={skip}&limit={limit}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{office_code}", response_model=OfficeOut)
async def get_office_by_code(
    request: Request,
    office_code: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a single office by office code."""
    client_ip = request.client.host
    log_api_request(logger, "GET", f"/offices/{office_code}", client_ip)
    
    try:
        office = await get_office(db, office_code)
        log_api_response(logger, "GET", f"/offices/{office_code}", 200)
        return office
    except HTTPException as e:
        log_api_response(logger, "GET", f"/offices/{office_code}", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in get_office_by_code: {e}")
        log_api_response(logger, "GET", f"/offices/{office_code}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{office_code}/employees", response_model=OfficeWithEmployees)
async def get_office_with_employees(
    request: Request,
    office_code: str,
    db: AsyncSession = Depends(get_db)
):
    """Get an office with all its employees."""
    client_ip = request.client.host
    log_api_request(logger, "GET", f"/offices/{office_code}/employees", client_ip)
    
    try:
        office = await get_office_with_employees(db, office_code)
        log_api_response(logger, "GET", f"/offices/{office_code}/employees", 200)
        return office
    except HTTPException as e:
        log_api_response(logger, "GET", f"/offices/{office_code}/employees", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in get_office_with_employees: {e}")
        log_api_response(logger, "GET", f"/offices/{office_code}/employees", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/", response_model=OfficeOut, status_code=201)
async def create_new_office(
    request: Request,
    office_data: OfficeCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new office."""
    client_ip = request.client.host
    log_api_request(logger, "POST", "/offices/", client_ip)
    
    try:
        office = await create_office(db, office_data)
        log_api_response(logger, "POST", "/offices/", 201)
        return office
    except HTTPException as e:
        log_api_response(logger, "POST", "/offices/", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in create_new_office: {e}")
        log_api_response(logger, "POST", "/offices/", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{office_code}", response_model=OfficeOut)
async def update_office_by_code(
    request: Request,
    office_code: str,
    office_data: OfficeUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an office by its code."""
    client_ip = request.client.host
    log_api_request(logger, "PUT", f"/offices/{office_code}", client_ip)
    
    try:
        office = await update_office(db, office_code, office_data)
        log_api_response(logger, "PUT", f"/offices/{office_code}", 200)
        return office
    except HTTPException as e:
        log_api_response(logger, "PUT", f"/offices/{office_code}", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in update_office_by_code: {e}")
        log_api_response(logger, "PUT", f"/offices/{office_code}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{office_code}", status_code=204)
async def delete_office_by_code(
    request: Request,
    office_code: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete an office by its code."""
    client_ip = request.client.host
    log_api_request(logger, "DELETE", f"/offices/{office_code}", client_ip)
    
    try:
        await delete_office(db, office_code)
        log_api_response(logger, "DELETE", f"/offices/{office_code}", 204)
        return None
    except HTTPException as e:
        log_api_response(logger, "DELETE", f"/offices/{office_code}", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in delete_office_by_code: {e}")
        log_api_response(logger, "DELETE", f"/offices/{office_code}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")
