"""
CRUD operations for database entities.
"""

from .customer import (
    get_customer,
    get_customers,
    get_customer_with_orders,
    create_customer,
    update_customer,
    delete_customer
)
from .dashboard import (
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

__all__ = [
    "get_customer",
    "get_customers", 
    "get_customer_with_orders",
    "create_customer",
    "update_customer",
    "delete_customer",
    "get_customer_count",
    "get_order_count",
    "get_product_count",
    "get_employee_count",
    "get_office_count",
    "get_payment_count",
    "get_orderdetail_count",
    "get_productline_count",
    "get_all_counts_concurrent"
]
