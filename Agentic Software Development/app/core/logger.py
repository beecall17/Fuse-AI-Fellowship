import logging
import os
from datetime import datetime
from typing import Optional

# Global registry to prevent duplicate handlers
_logger_registry = set()

def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance with centralized settings.
    
    Args:
        name: Name of the module requesting the logger
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if name not in _logger_registry:
        logger.setLevel(logging.INFO)
        
        # Clear existing handlers to avoid duplicates
        logger.handlers.clear()
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Create formatters
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler for logs
        file_handler = logging.FileHandler('logs/app.log')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        # Mark as configured
        _logger_registry.add(name)
    
    return logger

def log_api_request(logger: logging.Logger, method: str, path: str, client_ip: Optional[str] = None):
    """Log incoming API requests"""
    client_info = f" from {client_ip}" if client_ip else ""
    logger.info(f"API Request: {method} {path}{client_info}")

def log_api_response(logger: logging.Logger, method: str, path: str, status_code: int):
    """Log API responses"""
    logger.info(f"API Response: {method} {path} - Status: {status_code}")

def log_database_operation(logger: logging.Logger, operation: str, table: str, details: Optional[str] = None):
    """Log database operations"""
    details_str = f" - {details}" if details else ""
    logger.info(f"DB Operation: {operation} on {table}{details_str}")

def log_validation_error(logger: logging.Logger, field: str, value: str, error: str):
    """Log validation errors"""
    logger.warning(f"Validation Error - Field: {field}, Value: {value}, Error: {error}")
