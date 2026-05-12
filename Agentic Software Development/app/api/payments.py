from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.crud.payment import (
    get_payments,
    get_payment,
    create_payment,
    update_payment,
    delete_payment,
    get_payments_by_customer,
    get_payments_count
)
from app.schemas.payment import (
    PaymentCreate,
    PaymentOut,
    PaymentUpdate,
    PaymentList
)
from app.core.logger import get_logger, log_api_request, log_api_response

router = APIRouter(prefix="/payments", tags=["Payments"])
logger = get_logger(__name__)

@router.get("/", response_model=PaymentList)
async def list_payments(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """List all payments with pagination."""
    client_ip = request.client.host
    log_api_request(logger, "GET", f"/payments/?skip={skip}&limit={limit}", client_ip)
    
    try:
        payments = await get_payments(db, skip=skip, limit=limit)
        total = await get_payments_count(db)
        
        response = PaymentList(
            payments=payments,
            total=total,
            skip=skip,
            limit=limit
        )
        
        log_api_response(logger, "GET", f"/payments/?skip={skip}&limit={limit}", 200)
        return response
    except HTTPException as e:
        log_api_response(logger, "GET", f"/payments/?skip={skip}&limit={limit}", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in list_payments: {e}")
        log_api_response(logger, "GET", f"/payments/?skip={skip}&limit={limit}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{customer_number}/{check_number}", response_model=PaymentOut)
async def get_payment_by_composite_key(
    request: Request,
    customer_number: int,
    check_number: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a single payment by composite key (customer number + check number)."""
    client_ip = request.client.host
    log_api_request(logger, "GET", f"/payments/{customer_number}/{check_number}", client_ip)
    
    try:
        payment = await get_payment(db, customer_number, check_number)
        log_api_response(logger, "GET", f"/payments/{customer_number}/{check_number}", 200)
        return payment
    except HTTPException as e:
        log_api_response(logger, "GET", f"/payments/{customer_number}/{check_number}", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in get_payment_by_composite_key: {e}")
        log_api_response(logger, "GET", f"/payments/{customer_number}/{check_number}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/customer/{customer_number}", response_model=PaymentList)
async def get_payments_by_customer_number(
    request: Request,
    customer_number: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all payments for a specific customer."""
    client_ip = request.client.host
    log_api_request(logger, "GET", f"/payments/customer/{customer_number}", client_ip)
    
    try:
        payments = await get_payments_by_customer(db, customer_number)
        
        response = PaymentList(
            payments=payments,
            total=len(payments),
            skip=0,
            limit=len(payments)
        )
        
        log_api_response(logger, "GET", f"/payments/customer/{customer_number}", 200)
        return response
    except HTTPException as e:
        log_api_response(logger, "GET", f"/payments/customer/{customer_number}", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in get_payments_by_customer_number: {e}")
        log_api_response(logger, "GET", f"/payments/customer/{customer_number}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/", response_model=PaymentOut, status_code=201)
async def create_new_payment(
    request: Request,
    payment_data: PaymentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new payment."""
    client_ip = request.client.host
    log_api_request(logger, "POST", "/payments/", client_ip)
    
    try:
        payment = await create_payment(db, payment_data)
        log_api_response(logger, "POST", "/payments/", 201)
        return payment
    except HTTPException as e:
        log_api_response(logger, "POST", "/payments/", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in create_new_payment: {e}")
        log_api_response(logger, "POST", "/payments/", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{customer_number}/{check_number}", response_model=PaymentOut)
async def update_payment_by_composite_key(
    request: Request,
    customer_number: int,
    check_number: str,
    payment_data: PaymentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a payment by composite key."""
    client_ip = request.client.host
    log_api_request(logger, "PUT", f"/payments/{customer_number}/{check_number}", client_ip)
    
    try:
        payment = await update_payment(db, customer_number, check_number, payment_data)
        log_api_response(logger, "PUT", f"/payments/{customer_number}/{check_number}", 200)
        return payment
    except HTTPException as e:
        log_api_response(logger, "PUT", f"/payments/{customer_number}/{check_number}", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in update_payment_by_composite_key: {e}")
        log_api_response(logger, "PUT", f"/payments/{customer_number}/{check_number}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{customer_number}/{check_number}", status_code=204)
async def delete_payment_by_composite_key(
    request: Request,
    customer_number: int,
    check_number: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a payment by composite key."""
    client_ip = request.client.host
    log_api_request(logger, "DELETE", f"/payments/{customer_number}/{check_number}", client_ip)
    
    try:
        await delete_payment(db, customer_number, check_number)
        log_api_response(logger, "DELETE", f"/payments/{customer_number}/{check_number}", 204)
        return None
    except HTTPException as e:
        log_api_response(logger, "DELETE", f"/payments/{customer_number}/{check_number}", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in delete_payment_by_composite_key: {e}")
        log_api_response(logger, "DELETE", f"/payments/{customer_number}/{check_number}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")
