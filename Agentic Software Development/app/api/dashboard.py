from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.crud.dashboard import (
    get_customer_count,
    get_order_count,
    get_product_count,
    get_employee_count,
    get_office_count,
    get_payment_count,
    get_orderdetail_count,
    get_productline_count,
    get_all_counts_concurrent
)
from app.schemas.dashboard import CountResponse, OverallCounts
from app.core.logger import get_logger, log_api_request, log_api_response

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
logger = get_logger(__name__)

@router.get("/customers/count", response_model=CountResponse)
async def get_customers_count(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Get total number of customers."""
    client_ip = request.client.host
    log_api_request(logger, "GET", "/dashboard/customers/count", client_ip)
    
    try:
        count = await get_customer_count(db)
        response = CountResponse(count=count, table="customers")
        log_api_response(logger, "GET", "/dashboard/customers/count", 200)
        return response
    except Exception as e:
        logger.error(f"Error in customers count endpoint: {e}")
        log_api_response(logger, "GET", "/dashboard/customers/count", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/orders/count", response_model=CountResponse)
async def get_orders_count(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Get total number of orders."""
    client_ip = request.client.host
    log_api_request(logger, "GET", "/dashboard/orders/count", client_ip)
    
    try:
        count = await get_order_count(db)
        response = CountResponse(count=count, table="orders")
        log_api_response(logger, "GET", "/dashboard/orders/count", 200)
        return response
    except Exception as e:
        logger.error(f"Error in orders count endpoint: {e}")
        log_api_response(logger, "GET", "/dashboard/orders/count", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/products/count", response_model=CountResponse)
async def get_products_count(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Get total number of products."""
    client_ip = request.client.host
    log_api_request(logger, "GET", "/dashboard/products/count", client_ip)
    
    try:
        count = await get_product_count(db)
        response = CountResponse(count=count, table="products")
        log_api_response(logger, "GET", "/dashboard/products/count", 200)
        return response
    except Exception as e:
        logger.error(f"Error in products count endpoint: {e}")
        log_api_response(logger, "GET", "/dashboard/products/count", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/employees/count", response_model=CountResponse)
async def get_employees_count(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Get total number of employees."""
    client_ip = request.client.host
    log_api_request(logger, "GET", "/dashboard/employees/count", client_ip)
    
    try:
        count = await get_employee_count(db)
        response = CountResponse(count=count, table="employees")
        log_api_response(logger, "GET", "/dashboard/employees/count", 200)
        return response
    except Exception as e:
        logger.error(f"Error in employees count endpoint: {e}")
        log_api_response(logger, "GET", "/dashboard/employees/count", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/offices/count", response_model=CountResponse)
async def get_offices_count(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Get total number of offices."""
    client_ip = request.client.host
    log_api_request(logger, "GET", "/dashboard/offices/count", client_ip)
    
    try:
        count = await get_office_count(db)
        response = CountResponse(count=count, table="offices")
        log_api_response(logger, "GET", "/dashboard/offices/count", 200)
        return response
    except Exception as e:
        logger.error(f"Error in offices count endpoint: {e}")
        log_api_response(logger, "GET", "/dashboard/offices/count", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/payments/count", response_model=CountResponse)
async def get_payments_count(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Get total number of payments."""
    client_ip = request.client.host
    log_api_request(logger, "GET", "/dashboard/payments/count", client_ip)
    
    try:
        count = await get_payment_count(db)
        response = CountResponse(count=count, table="payments")
        log_api_response(logger, "GET", "/dashboard/payments/count", 200)
        return response
    except Exception as e:
        logger.error(f"Error in payments count endpoint: {e}")
        log_api_response(logger, "GET", "/dashboard/payments/count", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/orderdetails/count", response_model=CountResponse)
async def get_orderdetails_count(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Get total number of order details."""
    client_ip = request.client.host
    log_api_request(logger, "GET", "/dashboard/orderdetails/count", client_ip)
    
    try:
        count = await get_orderdetail_count(db)
        response = CountResponse(count=count, table="orderdetails")
        log_api_response(logger, "GET", "/dashboard/orderdetails/count", 200)
        return response
    except Exception as e:
        logger.error(f"Error in orderdetails count endpoint: {e}")
        log_api_response(logger, "GET", "/dashboard/orderdetails/count", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/productlines/count", response_model=CountResponse)
async def get_productlines_count(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Get total number of product lines."""
    client_ip = request.client.host
    log_api_request(logger, "GET", "/dashboard/productlines/count", client_ip)
    
    try:
        count = await get_productline_count(db)
        response = CountResponse(count=count, table="productlines")
        log_api_response(logger, "GET", "/dashboard/productlines/count", 200)
        return response
    except Exception as e:
        logger.error(f"Error in productlines count endpoint: {e}")
        log_api_response(logger, "GET", "/dashboard/productlines/count", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/overall_counts", response_model=OverallCounts)
async def get_overall_counts(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Get counts from all tables concurrently.
    This endpoint uses asyncio.gather() to run all queries simultaneously
    for maximum performance.
    """
    client_ip = request.client.host
    log_api_request(logger, "GET", "/dashboard/overall_counts", client_ip)
    
    try:
        logger.info("Starting concurrent overall counts request")
        counts = await get_all_counts_concurrent(db)
        
        response = OverallCounts(**counts)
        log_api_response(logger, "GET", "/dashboard/overall_counts", 200)
        return response
    except Exception as e:
        logger.error(f"Error in overall_counts endpoint: {e}")
        log_api_response(logger, "GET", "/dashboard/overall_counts", 500)
        raise HTTPException(status_code=500, detail="Internal server error")
