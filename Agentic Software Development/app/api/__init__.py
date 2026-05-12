"""
FastAPI routers and endpoints.
"""

from .customers import router as customers_router
from .dashboard import router as dashboard_router

__all__ = [
    "customers_router",
    "dashboard_router"
]
