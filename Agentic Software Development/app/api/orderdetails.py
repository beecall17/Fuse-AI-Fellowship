from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.crud.orderdetail import (
    get_orderdetails,
    get_orderdetail,
    create_orderdetail,
    update_orderdetail,
    delete_orderdetail,
    get_orderdetails_by_order,
    get_orderdetails_by_product,
    get_orderdetails_count
)
from app.schemas.orderdetail import (
    OrderDetailCreate,
    OrderDetailOut,
    OrderDetailUpdate,
    OrderDetailList
)
from app.core.logger import get_logger, log_api_request, log_api_response

router = APIRouter(prefix="/orderdetails", tags=["OrderDetails"])
logger = get_logger(__name__)

@router.get("/", response_model=OrderDetailList)
async def list_orderdetails(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """List all order details with pagination."""
    client_ip = request.client.host
    log_api_request(logger, "GET", f"/orderdetails/?skip={skip}&limit={limit}", client_ip)
    
    try:
        orderdetails = await get_orderdetails(db, skip=skip, limit=limit)
        total = await get_orderdetails_count(db)
        
        response = OrderDetailList(
            orderdetails=orderdetails,
            total=total,
            skip=skip,
            limit=limit
        )
        
        log_api_response(logger, "GET", f"/orderdetails/?skip={skip}&limit={limit}", 200)
        return response
    except HTTPException as e:
        log_api_response(logger, "GET", f"/orderdetails/?skip={skip}&limit={limit}", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in list_orderdetails: {e}")
        log_api_response(logger, "GET", f"/orderdetails/?skip={skip}&limit={limit}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{order_number}/{product_code}", response_model=OrderDetailOut)
async def get_orderdetail_by_composite_key(
    request: Request,
    order_number: int,
    product_code: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a single order detail by composite key (order number + product code)."""
    client_ip = request.client.host
    log_api_request(logger, "GET", f"/orderdetails/{order_number}/{product_code}", client_ip)
    
    try:
        orderdetail = await get_orderdetail(db, order_number, product_code)
        log_api_response(logger, "GET", f"/orderdetails/{order_number}/{product_code}", 200)
        return orderdetail
    except HTTPException as e:
        log_api_response(logger, "GET", f"/orderdetails/{order_number}/{product_code}", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in get_orderdetail_by_composite_key: {e}")
        log_api_response(logger, "GET", f"/orderdetails/{order_number}/{product_code}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/order/{order_number}", response_model=OrderDetailList)
async def get_orderdetails_by_order_number(
    request: Request,
    order_number: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all order details for a specific order."""
    client_ip = request.client.host
    log_api_request(logger, "GET", f"/orderdetails/order/{order_number}", client_ip)
    
    try:
        orderdetails = await get_orderdetails_by_order(db, order_number)
        
        response = OrderDetailList(
            orderdetails=orderdetails,
            total=len(orderdetails),
            skip=0,
            limit=len(orderdetails)
        )
        
        log_api_response(logger, "GET", f"/orderdetails/order/{order_number}", 200)
        return response
    except HTTPException as e:
        log_api_response(logger, "GET", f"/orderdetails/order/{order_number}", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in get_orderdetails_by_order_number: {e}")
        log_api_response(logger, "GET", f"/orderdetails/order/{order_number}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/product/{product_code}", response_model=OrderDetailList)
async def get_orderdetails_by_product_code(
    request: Request,
    product_code: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all order details for a specific product."""
    client_ip = request.client.host
    log_api_request(logger, "GET", f"/orderdetails/product/{product_code}", client_ip)
    
    try:
        orderdetails = await get_orderdetails_by_product(db, product_code)
        
        response = OrderDetailList(
            orderdetails=orderdetails,
            total=len(orderdetails),
            skip=0,
            limit=len(orderdetails)
        )
        
        log_api_response(logger, "GET", f"/orderdetails/product/{product_code}", 200)
        return response
    except HTTPException as e:
        log_api_response(logger, "GET", f"/orderdetails/product/{product_code}", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in get_orderdetails_by_product_code: {e}")
        log_api_response(logger, "GET", f"/orderdetails/product/{product_code}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/", response_model=OrderDetailOut, status_code=201)
async def create_new_orderdetail(
    request: Request,
    orderdetail_data: OrderDetailCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new order detail."""
    client_ip = request.client.host
    log_api_request(logger, "POST", "/orderdetails/", client_ip)
    
    try:
        orderdetail = await create_orderdetail(db, orderdetail_data)
        log_api_response(logger, "POST", "/orderdetails/", 201)
        return orderdetail
    except HTTPException as e:
        log_api_response(logger, "POST", "/orderdetails/", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in create_new_orderdetail: {e}")
        log_api_response(logger, "POST", "/orderdetails/", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{order_number}/{product_code}", response_model=OrderDetailOut)
async def update_orderdetail_by_composite_key(
    request: Request,
    order_number: int,
    product_code: str,
    orderdetail_data: OrderDetailUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an order detail by composite key."""
    client_ip = request.client.host
    log_api_request(logger, "PUT", f"/orderdetails/{order_number}/{product_code}", client_ip)
    
    try:
        orderdetail = await update_orderdetail(db, order_number, product_code, orderdetail_data)
        log_api_response(logger, "PUT", f"/orderdetails/{order_number}/{product_code}", 200)
        return orderdetail
    except HTTPException as e:
        log_api_response(logger, "PUT", f"/orderdetails/{order_number}/{product_code}", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in update_orderdetail_by_composite_key: {e}")
        log_api_response(logger, "PUT", f"/orderdetails/{order_number}/{product_code}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{order_number}/{product_code}", status_code=204)
async def delete_orderdetail_by_composite_key(
    request: Request,
    order_number: int,
    product_code: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete an order detail by composite key."""
    client_ip = request.client.host
    log_api_request(logger, "DELETE", f"/orderdetails/{order_number}/{product_code}", client_ip)
    
    try:
        await delete_orderdetail(db, order_number, product_code)
        log_api_response(logger, "DELETE", f"/orderdetails/{order_number}/{product_code}", 204)
        return None
    except HTTPException as e:
        log_api_response(logger, "DELETE", f"/orderdetails/{order_number}/{product_code}", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in delete_orderdetail_by_composite_key: {e}")
        log_api_response(logger, "DELETE", f"/orderdetails/{order_number}/{product_code}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")
