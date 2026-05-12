from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.database.session import init_db, test_connection
from app.api.customers import router as customers_router
from app.api.dashboard import router as dashboard_router
from app.api.products import router as products_router
from app.api.productlines import router as productlines_router
from app.api.offices import router as offices_router
from app.api.employees import router as employees_router
from app.api.orders import router as orders_router
from app.api.orderdetails import router as orderdetails_router
from app.api.payments import router as payments_router
from app.core.logger import get_logger

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting ClassicModels Full REST API application...")
    
    # Test database connection
    if not await test_connection():
        logger.error("Failed to connect to database. Application startup aborted.")
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    # Initialize database tables
    try:
        await init_db()
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    logger.info("ClassicModels Full REST API application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ClassicModels Full REST API application...")

# Create FastAPI application
app = FastAPI(
    title="ClassicModels Full REST API",
    description="A comprehensive REST API for all ClassicModels database tables with async SQLAlchemy and PostgreSQL",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(customers_router)
app.include_router(dashboard_router)
app.include_router(products_router)
app.include_router(productlines_router)
app.include_router(offices_router)
app.include_router(employees_router)
app.include_router(orders_router)
app.include_router(orderdetails_router)
app.include_router(payments_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    Returns the status of the application and database connection.
    """
    try:
        db_status = await test_connection()
        return {
            "status": "healthy" if db_status else "unhealthy",
            "database": "connected" if db_status else "disconnected",
            "message": "ClassicModels Full REST API is running" if db_status else "Database connection failed"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "message": "Health check failed"
        }

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "ClassicModels Full REST API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
