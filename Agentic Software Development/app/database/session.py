import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
from app.core.logger import get_logger
from sqlalchemy import text  # <--- CRITICAL IMPORT

# Load environment variables
load_dotenv()

logger = get_logger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://app_user:secure_password_123@localhost:5432/classicmodels")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    future=True
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create Base class for models
Base = declarative_base()

async def get_db() -> AsyncSession:
    """
    Dependency to get async database session.
    
    Yields:
        AsyncSession: Database session for use in endpoints
    """
    db = AsyncSessionLocal()
    try:
        logger.info("Database connection established successfully")
        yield db
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        await db.rollback()
        raise
    finally:
        await db.close()
        logger.info("Database connection closed")

async def init_db():
    """
    Initialize database tables.
    Call this during application startup.
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

async def test_connection():
    """
    Test database connection.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database test connection successful")
        return True
    except Exception as e:
        logger.error(f"Database test connection failed: {e}")
        return False
