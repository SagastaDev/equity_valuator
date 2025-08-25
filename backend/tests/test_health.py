"""
Test cases for health check endpoint.
"""
import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test if the /health endpoint is operational."""
    # Act: Send a request to the endpoint
    response = client.get("/health")

    # Assert: Verify the response
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint(client: TestClient):
    """Test if the root endpoint is operational."""
    # Act: Send a request to the root endpoint
    response = client.get("/")

    # Assert: Verify the response
    assert response.status_code == 200
    assert response.json() == {"message": "Equity Valuation System API"}