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
├── __init__.py           # Test package initialization
├── conftest.py          # Shared test fixtures and configuration
└── test_health.py       # Health endpoint tests
```

## Current Test Coverage

The initial test suite includes:

1. **Health Check Tests** (`test_health.py`):
   - `test_health_check()` - Validates `/health` endpoint returns status "healthy" 
   - `test_root_endpoint()` - Validates root `/` endpoint returns API message

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
The current test setup uses FastAPI's TestClient without complex database interactions for basic endpoint testing.

## Adding New Tests

When adding new tests:

1. Create test files in `backend/tests/` with the prefix `test_`
2. Import necessary fixtures from `conftest.py`
3. Follow the naming convention `test_<functionality>`
4. Use the `client` fixture for HTTP endpoint testing

Example:
```python
def test_new_endpoint(client):
    response = client.get("/api/new-endpoint")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
```

## Integration with CI/CD

The command `docker-compose exec backend pytest` should be used in automated testing pipelines to ensure consistent test execution across environments.