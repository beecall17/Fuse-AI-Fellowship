# Customer API Dashboard

A high-performance FastAPI application with concurrent dashboard endpoints for retrieving database record counts.

## Project Overview

This project implements a comprehensive Customer API with dashboard functionality following Twelve-Factor App principles. The application features:

- **Customer CRUD Operations**: Complete Create, Read, Update, Delete operations for customer management
- **Dashboard API**: Concurrent endpoints for retrieving record counts from 8 database tables
- **High Performance**: Uses `asyncio.gather()` for simultaneous database queries
- **Modern Architecture**: Layered design with proper separation of concerns
- **Comprehensive Logging**: Full observability across all application layers

### Key Features

#### Customer Management
- List customers with pagination
- Get customer by ID
- Create new customers
- Update existing customers
- Delete customers (with foreign key constraint handling)
- Get customers with their orders

#### Dashboard Analytics
- 8 individual count endpoints (`/dashboard/{table}/count`)
- Concurrent aggregated endpoint (`/dashboard/overall_counts`)
- Performance optimization through async concurrency
- Real-time database statistics

### Technology Stack

- **Backend**: FastAPI 0.104.1
- **Database**: PostgreSQL 16 with asyncpg driver
- **ORM**: SQLAlchemy 2.0 with async support
- **Validation**: Pydantic 2.5 with field_validator
- **Containerization**: Docker & Docker Compose
- **Environment**: Python 3.14

## Project Setup

### Prerequisites

- Python 3.14+
- Docker & Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/beecall17/Fuse-AI-Fellowship.git
   cd "Agentic Software Development"
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your database configuration
   # Default configuration works with Docker setup
   ```

5. **Start PostgreSQL with Docker**
   ```bash
   docker-compose up -d
   ```

6. **Run the application**
   ```bash
   python main.py
   ```

### Environment Configuration

The application uses environment variables for configuration:

```bash
# Database Configuration in .env file
POSTGRES_DB=classicmodels
POSTGRES_USER=app_user
POSTGRES_PASSWORD=secure_password_123
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DATABASE_URL=postgresql+asyncpg://app_user:secure_password_123@localhost:5432/classicmodels

# Docker Configuration
POSTGRES_CONTAINER_NAME=classicmodels_db
POSTGRES_VERSION=16
```

## API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### Customer Management
- `GET /customers/` - List customers with pagination
- `GET /customers/{customer_id}` - Get customer by ID
- `POST /customers/` - Create new customer
- `PUT /customers/{customer_id}` - Update customer
- `DELETE /customers/{customer_id}` - Delete customer
- `GET /customers/{customer_id}/orders` - Get customer with orders

#### Dashboard Analytics
- `GET /dashboard/customers/count` - Customer count
- `GET /dashboard/orders/count` - Order count
- `GET /dashboard/products/count` - Product count
- `GET /dashboard/employees/count` - Employee count
- `GET /dashboard/offices/count` - Office count
- `GET /dashboard/payments/count` - Payment count
- `GET /dashboard/orderdetails/count` - Order detail count
- `GET /dashboard/productlines/count` - Product line count
- `GET /dashboard/overall_counts` - **Concurrent** counts from all tables

#### System
- `GET /health` - Health check
- `GET /` - Root endpoint
- `GET /docs` - Interactive API documentation

### Performance

The concurrent `/dashboard/overall_counts` endpoint demonstrates significant performance improvements:

- **Sequential Approach**: ~8x individual query time
- **Concurrent Approach**: ~1x query time (all queries simultaneous)
- **Expected Speedup**: 4-8x faster depending on database load

## Project Structure

```
Agentic Software Development/
├── app/
│   ├── __init__.py
│   ├── api/                    # FastAPI routers
│   │   ├── __init__.py
│   │   ├── customers.py         # Customer endpoints
│   │   └── dashboard.py         # Dashboard endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   └── logger.py           # Centralized logging
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── customer.py          # Customer CRUD operations
│   │   └── dashboard.py        # Dashboard count operations
│   ├── database/
│   │   ├── __init__.py
│   │   └── session.py          # Database session management
│   ├── models/
│   │   ├── __init__.py
│   │   ├── customer.py          # Customer model
│   │   ├── order.py            # Order model
│   │   ├── product.py          # Product model
│   │   ├── employee.py         # Employee model
│   │   ├── office.py           # Office model
│   │   ├── payment.py          # Payment model
│   │   ├── orderdetail.py       # OrderDetail model
│   │   └── productline.py      # ProductLine model
│   └── schemas/
│       ├── __init__.py
│       ├── customer.py          # Customer validation schemas
│       └── dashboard.py        # Dashboard response schemas
├── scripts/
│   └── seed.sql               # Database seed data
├── logs/
│   └── app.log               # Application logs
├── docker-compose.yml          # PostgreSQL service
├── .env.example              # Environment template
├── .env                     # Environment variables (gitignored)
├── requirements.txt           # Python dependencies
├── main.py                  # Application entry point
└── README.md                # This file
```

## Development

### Testing

1. **Start the API server**
   ```bash
   python main.py
   ```

2. **Test endpoints**
   ```bash
   # Test dashboard endpoints
   curl http://localhost:8000/dashboard/overall_counts
   
   # Test customer endpoints
   curl http://localhost:8000/customers/
   ```

3. **Interactive documentation**
   - Visit `http://localhost:8000/docs` for Swagger UI
   - Visit `http://localhost:8000/redoc` for ReDoc documentation

### Logging

The application provides comprehensive logging:
- **Request/Response Logging**: All API calls with status codes
- **Database Operations**: Query execution timing and errors
- **Performance Metrics**: Concurrent operation timing
- **Error Tracking**: Detailed exception logging

Logs are stored in `logs/app.log` with format:
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## Database Schema

The application uses the ClassicModels database with 8 tables:

- **customers** - Customer information
- **orders** - Customer orders
- **products** - Product catalog
- **employees** - Employee data
- **offices** - Office locations
- **payments** - Payment records
- **orderdetails** - Order line items
- **productlines** - Product categories

All tables are properly related with foreign key constraints and SQLAlchemy relationships.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of the Fuse AI Fellowship program.