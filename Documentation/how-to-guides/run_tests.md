# How to Run Backend Tests

This guide explains how to run the backend test suite for the Equity Valuation System.

## Overview

The backend test suite uses `pytest` as the testing framework and is designed to run within the Docker container environment. The tests validate the functionality of API endpoints and ensure code quality.

## Prerequisites

- Docker and Docker Compose installed
- Backend container must be built with testing dependencies

## Running the Test Suite

### Option 1: Run tests in Docker container (Recommended)

This is the primary method for running tests and must be used for consistency with the development environment.

```bash
# Start the backend container (if not already running)
docker-compose up -d backend

# Run the complete test suite
docker-compose exec backend pytest

# Run tests with verbose output
docker-compose exec backend pytest -v

# Run specific test file
docker-compose exec backend pytest backend/tests/test_health.py

# Run specific test function
docker-compose exec backend pytest backend/tests/test_health.py::test_health_check
```

### Test Structure

The test suite is organized as follows:

```
backend/tests/
├── __init__.py              # Test package initialization
├── conftest.py             # Shared test fixtures and configuration
├── test_health.py          # Health endpoint tests
├── api/                    # API integration tests
│   ├── __init__.py
│   └── v1/                 # API version 1 tests
│       ├── __init__.py
│       ├── test_companies.py    # Companies API tests
│       ├── test_providers.py    # Providers API tests
│       ├── test_transform.py    # Transform API tests
│       └── test_valuation.py    # Valuation API tests
└── services/               # Service layer unit tests
    ├── __init__.py
    ├── test_transform_engine.py    # Transform engine tests
    └── test_formula_evaluator.py  # Formula evaluator tests
```

## Current Test Coverage

The comprehensive test suite includes:

1. **Health Check Tests** (`test_health.py`):
   - `test_health_check()` - Validates `/health` endpoint returns status "healthy" 
   - `test_root_endpoint()` - Validates root `/` endpoint returns API message

2. **API Integration Tests** (`api/v1/`):
   - **Companies API** (`test_companies.py`): Complete CRUD operations, authentication, search, pagination, price data endpoints, and admin-only data ingestion
   - **Providers API** (`test_providers.py`): Provider management endpoints with admin permissions
   - **Valuation API** (`test_valuation.py`): Valuation CRUD operations with proper data validation
   - **Transform API** (`test_transform.py`): Field mapping operations, canonical fields, raw fields, transform testing, and backup functionality

3. **Service Layer Unit Tests** (`services/`):
   - **Transform Engine** (`test_transform_engine.py`): Mathematical operations, functions, nested expressions, error handling, and validation
   - **Formula Evaluator** (`test_formula_evaluator.py`): Data transformation, computed fields calculation, and error recovery

**Coverage Statistics**: 105+ test cases covering both happy path and error scenarios, with comprehensive authentication testing and role-based access control validation.

## Test Configuration

- **pytest.ini**: Contains pytest configuration in `backend/pytest.ini`
- **Fixtures**: Shared test fixtures defined in `backend/tests/conftest.py`
- **Test Client**: Uses FastAPI's TestClient for HTTP testing

## Expected Output

When tests pass successfully, you should see output similar to:

```
============================= test session starts ==============================
platform linux -- Python 3.11.13, pytest-7.4.3, pluggy-1.6.0
rootdir: /app
plugins: asyncio-0.21.1, anyio-3.7.1
asyncio: mode=Mode.STRICT
collected 2 items

backend/tests/test_health.py ..                                          [100%]

======================== 2 passed, 13 warnings in 2.03s ========================
```

## Troubleshooting

### Container Not Found
If you get an error about the backend container not being found:
```bash
docker-compose up -d backend
```

### Permission Errors
Tests should run within the Docker container to avoid permission issues with the host system.

### Database Issues
The test setup uses PostgreSQL with isolated test database (`equity_valuation_test`) to ensure tests don't interfere with development data. Database fixtures handle automatic cleanup.

## Adding New Tests

When adding new tests:

1. **API Tests**: Create files in `backend/tests/api/v1/` with the prefix `test_`
2. **Service Tests**: Create files in `backend/tests/services/` with the prefix `test_`
3. Import necessary fixtures from `conftest.py` (client, auth_headers, admin_headers, test_user, etc.)
4. Follow the naming convention `test_<functionality>`
5. Use appropriate fixtures for testing scenarios

**API Test Example:**
```python
def test_new_endpoint_success(client, auth_headers):
    response = client.get("/api/new-endpoint", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_new_endpoint_unauthorized(client):
    response = client.get("/api/new-endpoint")
    assert response.status_code == 401
```

**Service Test Example:**
```python
from unittest.mock import Mock
from backend.services.my_service import MyService

def test_service_calculation():
    service = MyService()
    result = service.calculate_value(100, 0.1)
    assert result == 110.0
```

**Available Fixtures:**
- `client`: FastAPI test client
- `auth_headers`: Authentication headers for regular user
- `admin_headers`: Authentication headers for admin user
- `test_user`, `admin_user`: Test user objects
- `test_company`, `test_provider`: Test data objects
- `canonical_fields`: Test canonical field objects
- `db_session`: Database session for test data setup

## Integration with CI/CD

The command `docker-compose exec backend pytest` should be used in automated testing pipelines to ensure consistent test execution across environments.