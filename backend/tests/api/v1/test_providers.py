"""
Test cases for Providers API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from backend.db.models.provider import Provider


class TestProviderEndpoints:
    """Test provider CRUD operations."""

    def test_get_providers_success(self, client: TestClient, auth_headers: dict, test_provider: Provider):
        """Test successful retrieval of providers list."""
        response = client.get("/api/providers/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        provider_names = [p["name"] for p in data]
        assert test_provider.name in provider_names

    def test_get_providers_unauthorized(self, client: TestClient):
        """Test providers list requires authentication."""
        response = client.get("/api/providers/")
        
        assert response.status_code == 401

    def test_get_provider_by_id_success(self, client: TestClient, auth_headers: dict, test_provider: Provider):
        """Test successful retrieval of provider by ID."""
        response = client.get(f"/api/providers/{test_provider.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_provider.id
        assert data["name"] == test_provider.name

    def test_get_provider_by_id_not_found(self, client: TestClient, auth_headers: dict):
        """Test get provider with invalid ID returns 404."""
        response = client.get("/api/providers/99999", headers=auth_headers)
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Provider not found"

    def test_create_provider_success(self, client: TestClient, admin_headers: dict):
        """Test successful creation of a provider by admin."""
        provider_data = {
            "name": "New Test Provider"
        }
        
        response = client.post("/api/providers/", json=provider_data, headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == provider_data["name"]
        assert "id" in data

    def test_create_provider_missing_name(self, client: TestClient, admin_headers: dict):
        """Test provider creation with missing name field returns 422."""
        invalid_data = {}
        
        response = client.post("/api/providers/", json=invalid_data, headers=admin_headers)
        
        assert response.status_code == 422
        error_detail = response.json()["detail"][0]
        assert error_detail["loc"] == ["body", "name"]
        assert error_detail["msg"] == "Field required"

    def test_create_provider_empty_name(self, client: TestClient, admin_headers: dict):
        """Test provider creation with empty name field returns 422."""
        invalid_data = {"name": ""}
        
        response = client.post("/api/providers/", json=invalid_data, headers=admin_headers)
        
        assert response.status_code == 422

    def test_create_provider_admin_required(self, client: TestClient, auth_headers: dict):
        """Test provider creation requires admin privileges."""
        provider_data = {
            "name": "Unauthorized Provider"
        }
        
        response = client.post("/api/providers/", json=provider_data, headers=auth_headers)
        
        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]

    def test_create_provider_unauthorized(self, client: TestClient):
        """Test provider creation without authentication returns 401."""
        provider_data = {
            "name": "Unauthorized Provider"
        }
        
        response = client.post("/api/providers/", json=provider_data)
        
        assert response.status_code == 401