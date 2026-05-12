from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.crud.customer import (
    get_customer, 
    get_customers, 
    get_customer_with_orders,
    create_customer, 
    update_customer, 
    delete_customer
)
from app.schemas.customer import (
    CustomerOut, 
    CustomerCreate, 
    CustomerUpdate, 
    CustomerWithOrders,
    CustomerList
)
from app.core.logger import get_logger, log_api_request, log_api_response

router = APIRouter(prefix="/customers", tags=["customers"])
logger = get_logger(__name__)

@router.get("/", response_model=CustomerList)
async def list_customers(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of customers to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of customers to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all customers with pagination.
    
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    """
    client_ip = request.client.host
    log_api_request(logger, "GET", f"/customers/?skip={skip}&limit={limit}", client_ip)
    
    try:
        customers, total = await get_customers(db, skip=skip, limit=limit)
        response_data = CustomerList(
            customers=customers,
            total=total,
            skip=skip,
            limit=limit
        )
        log_api_response(logger, "GET", f"/customers/?skip={skip}&limit={limit}", 200)
        return response_data
    except Exception as e:
        logger.error(f"Error listing customers: {e}")
        log_api_response(logger, "GET", f"/customers/?skip={skip}&limit={limit}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{customer_number}", response_model=CustomerOut)
async def get_customer_by_number(
    request: Request,
    customer_number: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific customer by customer number.
    
    - **customer_number**: The unique customer identifier
    """
    client_ip = request.client.host
    log_api_request(logger, "GET", f"/customers/{customer_number}", client_ip)
    
    try:
        customer = await get_customer(db, customer_number)
        if not customer:
            logger.warning(f"Customer not found: {customer_number}")
            log_api_response(logger, "GET", f"/customers/{customer_number}", 404)
            raise HTTPException(status_code=404, detail="Customer not found")
        
        log_api_response(logger, "GET", f"/customers/{customer_number}", 200)
        return customer
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting customer {customer_number}: {e}")
        log_api_response(logger, "GET", f"/customers/{customer_number}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{customer_number}/orders", response_model=CustomerWithOrders)
async def get_customer_with_orders_endpoint(
    request: Request,
    customer_number: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a customer with their orders and payments.
    
    - **customer_number**: The unique customer identifier
    """
    client_ip = request.client.host
    log_api_request(logger, "GET", f"/customers/{customer_number}/orders", client_ip)
    
    try:
        customer = await get_customer_with_orders(db, customer_number)
        if not customer:
            logger.warning(f"Customer not found: {customer_number}")
            log_api_response(logger, "GET", f"/customers/{customer_number}/orders", 404)
            raise HTTPException(status_code=404, detail="Customer not found")
        
        log_api_response(logger, "GET", f"/customers/{customer_number}/orders", 200)
        return customer
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting customer with orders {customer_number}: {e}")
        log_api_response(logger, "GET", f"/customers/{customer_number}/orders", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/", response_model=CustomerOut, status_code=201)
async def create_new_customer(
    request: Request,
    customer: CustomerCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new customer.
    
    - **customer**: Customer data to create
    """
    client_ip = request.client.host
    log_api_request(logger, "POST", "/customers/", client_ip)
    
    try:
        new_customer = await create_customer(db, customer)
        log_api_response(logger, "POST", "/customers/", 201)
        return new_customer
    except Exception as e:
        logger.error(f"Error creating customer: {e}")
        log_api_response(logger, "POST", "/customers/", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{customer_number}", response_model=CustomerOut)
async def update_existing_customer(
    request: Request,
    customer_number: int,
    customer_update: CustomerUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing customer.
    
    - **customer_number**: The unique customer identifier
    - **customer_update**: Updated customer data (all fields optional)
    """
    client_ip = request.client.host
    log_api_request(logger, "PUT", f"/customers/{customer_number}", client_ip)
    
    try:
        updated_customer = await update_customer(db, customer_number, customer_update)
        if not updated_customer:
            logger.warning(f"Cannot update - customer not found: {customer_number}")
            log_api_response(logger, "PUT", f"/customers/{customer_number}", 404)
            raise HTTPException(status_code=404, detail="Customer not found")
        
        log_api_response(logger, "PUT", f"/customers/{customer_number}", 200)
        return updated_customer
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating customer {customer_number}: {e}")
        log_api_response(logger, "PUT", f"/customers/{customer_number}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{customer_number}", status_code=204)
async def delete_existing_customer(
    request: Request,
    customer_number: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a customer.
    
    - **customer_number**: The unique customer identifier
    """
    client_ip = request.client.host
    log_api_request(logger, "DELETE", f"/customers/{customer_number}", client_ip)
    
    try:
        deleted = await delete_customer(db, customer_number)
        if not deleted:
            logger.warning(f"Cannot delete - customer not found: {customer_number}")
            log_api_response(logger, "DELETE", f"/customers/{customer_number}", 404)
            raise HTTPException(status_code=404, detail="Customer not found")
        
        log_api_response(logger, "DELETE", f"/customers/{customer_number}", 204)
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting customer {customer_number}: {e}")
        log_api_response(logger, "DELETE", f"/customers/{customer_number}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")
