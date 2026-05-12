from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.crud.order import (
    get_orders,
    get_order,
    create_order,
    update_order,
    delete_order,
    get_order_with_orderdetails,
    get_orders_by_customer,
    get_orders_count
)
from app.schemas.order import (
    OrderCreate,
    OrderOut,
    OrderUpdate,
    OrderWithOrderDetails,
    OrderList
)
from app.core.logger import get_logger, log_api_request, log_api_response

router = APIRouter(prefix="/orders", tags=["Orders"])
logger = get_logger(__name__)

@router.get("/", response_model=OrderList)
async def list_orders(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """List all orders with pagination."""
    client_ip = request.client.host
    log_api_request(logger, "GET", f"/orders/?skip={skip}&limit={limit}", client_ip)
    
    try:
        orders = await get_orders(db, skip=skip, limit=limit)
        total = await get_orders_count(db)
        
        response = OrderList(
            orders=orders,
            total=total,
            skip=skip,
            limit=limit
        )
        
        log_api_response(logger, "GET", f"/orders/?skip={skip}&limit={limit}", 200)
        return response
    except HTTPException as e:
        log_api_response(logger, "GET", f"/orders/?skip={skip}&limit={limit}", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in list_orders: {e}")
        log_api_response(logger, "GET", f"/orders/?skip={skip}&limit={limit}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{order_number}", response_model=OrderOut)
async def get_order_by_number(
    request: Request,
    order_number: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a single order by order number."""
    client_ip = request.client.host
    log_api_request(logger, "GET", f"/orders/{order_number}", client_ip)
    
    try:
        order = await get_order(db, order_number)
        log_api_response(logger, "GET", f"/orders/{order_number}", 200)
        return order
    except HTTPException as e:
        log_api_response(logger, "GET", f"/orders/{order_number}", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in get_order_by_number: {e}")
        log_api_response(logger, "GET", f"/orders/{order_number}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{order_number}/orderdetails", response_model=OrderWithOrderDetails)
async def get_order_with_orderdetails(
    request: Request,
    order_number: int,
    db: AsyncSession = Depends(get_db)
):
    """Get an order with all its line items (products ordered)."""
    client_ip = request.client.host
    log_api_request(logger, "GET", f"/orders/{order_number}/orderdetails", client_ip)
    
    try:
        order = await get_order_with_orderdetails(db, order_number)
        log_api_response(logger, "GET", f"/orders/{order_number}/orderdetails", 200)
        return order
    except HTTPException as e:
        log_api_response(logger, "GET", f"/orders/{order_number}/orderdetails", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in get_order_with_orderdetails: {e}")
        log_api_response(logger, "GET", f"/orders/{order_number}/orderdetails", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/customer/{customer_number}", response_model=OrderList)
async def get_orders_by_customer_number(
    request: Request,
    customer_number: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all orders for a specific customer."""
    client_ip = request.client.host
    log_api_request(logger, "GET", f"/orders/customer/{customer_number}", client_ip)
    
    try:
        orders = await get_orders_by_customer(db, customer_number)
        
        response = OrderList(
            orders=orders,
            total=len(orders),
            skip=0,
            limit=len(orders)
        )
        
        log_api_response(logger, "GET", f"/orders/customer/{customer_number}", 200)
        return response
    except HTTPException as e:
        log_api_response(logger, "GET", f"/orders/customer/{customer_number}", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in get_orders_by_customer_number: {e}")
        log_api_response(logger, "GET", f"/orders/customer/{customer_number}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/", response_model=OrderOut, status_code=201)
async def create_new_order(
    request: Request,
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new order."""
    client_ip = request.client.host
    log_api_request(logger, "POST", "/orders/", client_ip)
    
    try:
        order = await create_order(db, order_data)
        log_api_response(logger, "POST", "/orders/", 201)
        return order
    except HTTPException as e:
        log_api_response(logger, "POST", "/orders/", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in create_new_order: {e}")
        log_api_response(logger, "POST", "/orders/", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{order_number}", response_model=OrderOut)
async def update_order_by_number(
    request: Request,
    order_number: int,
    order_data: OrderUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an order by its number."""
    client_ip = request.client.host
    log_api_request(logger, "PUT", f"/orders/{order_number}", client_ip)
    
    try:
        order = await update_order(db, order_number, order_data)
        log_api_response(logger, "PUT", f"/orders/{order_number}", 200)
        return order
    except HTTPException as e:
        log_api_response(logger, "PUT", f"/orders/{order_number}", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in update_order_by_number: {e}")
        log_api_response(logger, "PUT", f"/orders/{order_number}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{order_number}", status_code=204)
async def delete_order_by_number(
    request: Request,
    order_number: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete an order by its number."""
    client_ip = request.client.host
    log_api_request(logger, "DELETE", f"/orders/{order_number}", client_ip)
    
    try:
        await delete_order(db, order_number)
        log_api_response(logger, "DELETE", f"/orders/{order_number}", 204)
        return None
    except HTTPException as e:
        log_api_response(logger, "DELETE", f"/orders/{order_number}", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in delete_order_by_number: {e}")
        log_api_response(logger, "DELETE", f"/orders/{order_number}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")
