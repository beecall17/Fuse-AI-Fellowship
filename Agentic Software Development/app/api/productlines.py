from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.crud.productline import (
    get_productlines,
    get_productline,
    create_productline,
    update_productline,
    delete_productline,
    get_productline_with_products,
    get_productlines_count
)
from app.schemas.productline import (
    ProductLineCreate,
    ProductLineOut,
    ProductLineUpdate,
    ProductLineWithProducts,
    ProductLineList
)
from app.core.logger import get_logger, log_api_request, log_api_response

router = APIRouter(prefix="/productlines", tags=["ProductLines"])
logger = get_logger(__name__)

@router.get("/", response_model=ProductLineList)
async def list_productlines(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """List all product lines with pagination."""
    client_ip = request.client.host
    log_api_request(logger, "GET", f"/productlines/?skip={skip}&limit={limit}", client_ip)
    
    try:
        productlines = await get_productlines(db, skip=skip, limit=limit)
        total = await get_productlines_count(db)
        
        response = ProductLineList(
            productlines=productlines,
            total=total,
            skip=skip,
            limit=limit
        )
        
        log_api_response(logger, "GET", f"/productlines/?skip={skip}&limit={limit}", 200)
        return response
    except HTTPException as e:
        log_api_response(logger, "GET", f"/productlines/?skip={skip}&limit={limit}", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in list_productlines: {e}")
        log_api_response(logger, "GET", f"/productlines/?skip={skip}&limit={limit}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{product_line}", response_model=ProductLineOut)
async def get_productline_by_name(
    request: Request,
    product_line: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a single product line by name."""
    client_ip = request.client.host
    log_api_request(logger, "GET", f"/productlines/{product_line}", client_ip)
    
    try:
        productline = await get_productline(db, product_line)
        log_api_response(logger, "GET", f"/productlines/{product_line}", 200)
        return productline
    except HTTPException as e:
        log_api_response(logger, "GET", f"/productlines/{product_line}", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in get_productline_by_name: {e}")
        log_api_response(logger, "GET", f"/productlines/{product_line}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{product_line}/products", response_model=ProductLineWithProducts)
async def get_productline_with_products(
    request: Request,
    product_line: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a product line with all its products."""
    client_ip = request.client.host
    log_api_request(logger, "GET", f"/productlines/{product_line}/products", client_ip)
    
    try:
        productline = await get_productline_with_products(db, product_line)
        log_api_response(logger, "GET", f"/productlines/{product_line}/products", 200)
        return productline
    except HTTPException as e:
        log_api_response(logger, "GET", f"/productlines/{product_line}/products", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in get_productline_with_products: {e}")
        log_api_response(logger, "GET", f"/productlines/{product_line}/products", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/", response_model=ProductLineOut, status_code=201)
async def create_new_productline(
    request: Request,
    productline_data: ProductLineCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new product line."""
    client_ip = request.client.host
    log_api_request(logger, "POST", "/productlines/", client_ip)
    
    try:
        productline = await create_productline(db, productline_data)
        log_api_response(logger, "POST", "/productlines/", 201)
        return productline
    except HTTPException as e:
        log_api_response(logger, "POST", "/productlines/", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in create_new_productline: {e}")
        log_api_response(logger, "POST", "/productlines/", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{product_line}", response_model=ProductLineOut)
async def update_productline_by_name(
    request: Request,
    product_line: str,
    productline_data: ProductLineUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a product line by name."""
    client_ip = request.client.host
    log_api_request(logger, "PUT", f"/productlines/{product_line}", client_ip)
    
    try:
        productline = await update_productline(db, product_line, productline_data)
        log_api_response(logger, "PUT", f"/productlines/{product_line}", 200)
        return productline
    except HTTPException as e:
        log_api_response(logger, "PUT", f"/productlines/{product_line}", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in update_productline_by_name: {e}")
        log_api_response(logger, "PUT", f"/productlines/{product_line}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{product_line}", status_code=204)
async def delete_productline_by_name(
    request: Request,
    product_line: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a product line by name."""
    client_ip = request.client.host
    log_api_request(logger, "DELETE", f"/productlines/{product_line}", client_ip)
    
    try:
        await delete_productline(db, product_line)
        log_api_response(logger, "DELETE", f"/productlines/{product_line}", 204)
        return None
    except HTTPException as e:
        log_api_response(logger, "DELETE", f"/productlines/{product_line}", e.status_code)
        raise
    except Exception as e:
        logger.error(f"Error in delete_productline_by_name: {e}")
        log_api_response(logger, "DELETE", f"/productlines/{product_line}", 500)
        raise HTTPException(status_code=500, detail="Internal server error")
