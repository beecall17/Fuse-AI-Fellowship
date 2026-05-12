from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.crud.product import (
    get_products,
    get_product,
    create_product,
    update_product,
    delete_product,
    get_product_with_orderdetails,
    get_products_count
)
from app.schemas.product import (
    ProductCreate,
    ProductOut,
    ProductUpdate,
    ProductWithOrderDetails,
    ProductList
)
from app.core.logger import get_logger, log_api_request, log_api_response

router = APIRouter(prefix="/products", tags=["Products"])
logger = get_logger(__name__)

@router.get("/", response_model=ProductList)
async def list_products(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """List all products with pagination."""
    client_ip = request.client.host
    log_api_request(logger, "GET", f"/products/?skip={skip}&limit={limit}", client_ip)
    
    try:
        products = await get_products(db, skip=skip, limit=limit)
        total = await get_products_count(db)
        
        response = ProductList(
            products=products,
            total=total,
            skip=skip,
            limit=limit
        )
        
        log_api_response(logger, "GET", f"/products/?skip={skip}&limit={limit}", 200)
        return response
    except HTTPException as e:
        log_api_response(logger, "GET", f"/products/?skip={skip}&limit={limit}", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in list_products: {e}")
        log_api_response(logger, "GET", f"/products/?skip={skip}&limit={limit}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{product_code}", response_model=ProductOut)
async def get_product_by_code(
    request: Request,
    product_code: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a single product by its product code."""
    client_ip = request.client.host
    log_api_request(logger, "GET", f"/products/{product_code}", client_ip)
    
    try:
        product = await get_product(db, product_code)
        log_api_response(logger, "GET", f"/products/{product_code}", 200)
        return product
    except HTTPException as e:
        log_api_response(logger, "GET", f"/products/{product_code}", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in get_product_by_code: {e}")
        log_api_response(logger, "GET", f"/products/{product_code}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{product_code}/orderdetails", response_model=ProductWithOrderDetails)
async def get_product_with_orderdetails(
    request: Request,
    product_code: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a product with all its order details."""
    client_ip = request.client.host
    log_api_request(logger, "GET", f"/products/{product_code}/orderdetails", client_ip)
    
    try:
        product = await get_product_with_orderdetails(db, product_code)
        log_api_response(logger, "GET", f"/products/{product_code}/orderdetails", 200)
        return product
    except HTTPException as e:
        log_api_response(logger, "GET", f"/products/{product_code}/orderdetails", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in get_product_with_orderdetails: {e}")
        log_api_response(logger, "GET", f"/products/{product_code}/orderdetails", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/", response_model=ProductOut, status_code=201)
async def create_new_product(
    request: Request,
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new product."""
    client_ip = request.client.host
    log_api_request(logger, "POST", "/products/", client_ip)
    
    try:
        product = await create_product(db, product_data)
        log_api_response(logger, "POST", "/products/", 201)
        return product
    except HTTPException as e:
        log_api_response(logger, "POST", "/products/", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in create_new_product: {e}")
        log_api_response(logger, "POST", "/products/", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{product_code}", response_model=ProductOut)
async def update_product_by_code(
    request: Request,
    product_code: str,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a product by its code."""
    client_ip = request.client.host
    log_api_request(logger, "PUT", f"/products/{product_code}", client_ip)
    
    try:
        product = await update_product(db, product_code, product_data)
        log_api_response(logger, "PUT", f"/products/{product_code}", 200)
        return product
    except HTTPException as e:
        log_api_response(logger, "PUT", f"/products/{product_code}", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in update_product_by_code: {e}")
        log_api_response(logger, "PUT", f"/products/{product_code}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{product_code}", status_code=204)
async def delete_product_by_code(
    request: Request,
    product_code: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a product by its code."""
    client_ip = request.client.host
    log_api_request(logger, "DELETE", f"/products/{product_code}", client_ip)
    
    try:
        await delete_product(db, product_code)
        log_api_response(logger, "DELETE", f"/products/{product_code}", 204)
        return None
    except HTTPException as e:
        log_api_response(logger, "DELETE", f"/products/{product_code}", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in delete_product_by_code: {e}")
        log_api_response(logger, "DELETE", f"/products/{product_code}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")
