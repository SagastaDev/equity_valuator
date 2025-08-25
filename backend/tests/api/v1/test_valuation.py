"""
Test cases for Valuation API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from backend.db.models.company import Company
from backend.db.models.valuation import ValuationResult
from datetime import date


class TestValuationEndpoints:
    """Test valuation CRUD operations."""

    def test_create_valuation_success(self, client: TestClient, auth_headers: dict, test_company: Company):
        """Test successful creation of a valuation result."""
        valuation_data = {
            "company_id": str(test_company.id),
            "as_of": str(date.today()),
            "results": {
                "dcf_value": 150.25,
                "pe_ratio": 25.5,
                "market_cap": 2500000000,
                "intrinsic_value": 145.00,
                "recommendation": "Buy"
            }
        }
        
        response = client.post("/api/valuation/", json=valuation_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["company_id"] == valuation_data["company_id"]
        assert data["results"]["dcf_value"] == 150.25
        assert "id" in data
        assert "user_id" in data

    def test_create_valuation_missing_company_id(self, client: TestClient, auth_headers: dict):
        """Test valuation creation with missing company_id returns 422."""
        invalid_data = {
            "as_of": str(date.today()),
            "results": {"dcf_value": 150.25}
        }
        
        response = client.post("/api/valuation/", json=invalid_data, headers=auth_headers)
        
        assert response.status_code == 422
        error_detail = response.json()["detail"][0]
        assert error_detail["loc"] == ["body", "company_id"]
        assert error_detail["msg"] == "Field required"

    def test_create_valuation_invalid_company_id(self, client: TestClient, auth_headers: dict):
        """Test valuation creation with invalid company_id format returns 422."""
        invalid_data = {
            "company_id": "not-a-uuid",
            "as_of": str(date.today()),
            "results": {"dcf_value": 150.25}
        }
        
        response = client.post("/api/valuation/", json=invalid_data, headers=auth_headers)
        
        assert response.status_code == 422

    def test_create_valuation_missing_as_of(self, client: TestClient, auth_headers: dict, test_company: Company):
        """Test valuation creation with missing as_of date returns 422."""
        invalid_data = {
            "company_id": str(test_company.id),
            "results": {"dcf_value": 150.25}
        }
        
        response = client.post("/api/valuation/", json=invalid_data, headers=auth_headers)
        
        assert response.status_code == 422
        error_detail = response.json()["detail"][0]
        assert error_detail["loc"] == ["body", "as_of"]

    def test_create_valuation_invalid_date_format(self, client: TestClient, auth_headers: dict, test_company: Company):
        """Test valuation creation with invalid date format returns 422."""
        invalid_data = {
            "company_id": str(test_company.id),
            "as_of": "not-a-date",
            "results": {"dcf_value": 150.25}
        }
        
        response = client.post("/api/valuation/", json=invalid_data, headers=auth_headers)
        
        assert response.status_code == 422

    def test_create_valuation_missing_results(self, client: TestClient, auth_headers: dict, test_company: Company):
        """Test valuation creation with missing results returns 422."""
        invalid_data = {
            "company_id": str(test_company.id),
            "as_of": str(date.today())
        }
        
        response = client.post("/api/valuation/", json=invalid_data, headers=auth_headers)
        
        assert response.status_code == 422
        error_detail = response.json()["detail"][0]
        assert error_detail["loc"] == ["body", "results"]

    def test_create_valuation_unauthorized(self, client: TestClient, test_company: Company):
        """Test valuation creation requires authentication."""
        valuation_data = {
            "company_id": str(test_company.id),
            "as_of": str(date.today()),
            "results": {"dcf_value": 150.25}
        }
        
        response = client.post("/api/valuation/", json=valuation_data)
        
        assert response.status_code == 401

    def test_get_valuations_by_company_success(self, client: TestClient, auth_headers: dict, test_company: Company, test_user, db_session):
        """Test successful retrieval of valuations by company."""
        # Create test valuation
        valuation = ValuationResult(
            company_id=test_company.id,
            user_id=test_user.id,
            as_of=date.today(),
            results={"dcf_value": 150.25, "pe_ratio": 25.5}
        )
        db_session.add(valuation)
        db_session.commit()
        
        response = client.get(f"/api/valuation/{test_company.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["company_id"] == str(test_company.id)
        assert data[0]["results"]["dcf_value"] == 150.25

    def test_get_valuations_by_company_empty_result(self, client: TestClient, auth_headers: dict):
        """Test get valuations for non-existent company returns empty list."""
        fake_uuid = "12345678-1234-1234-1234-123456789abc"
        response = client.get(f"/api/valuation/{fake_uuid}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_all_valuations_success(self, client: TestClient, auth_headers: dict, test_company: Company, test_user, db_session):
        """Test successful retrieval of all valuations."""
        # Create test valuation
        valuation = ValuationResult(
            company_id=test_company.id,
            user_id=test_user.id,
            as_of=date.today(),
            results={"dcf_value": 150.25}
        )
        db_session.add(valuation)
        db_session.commit()
        
        response = client.get("/api/valuation/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_all_valuations_with_pagination(self, client: TestClient, auth_headers: dict, test_company: Company, test_user, db_session):
        """Test all valuations retrieval with pagination parameters."""
        # Create multiple test valuations
        for i in range(3):
            valuation = ValuationResult(
                company_id=test_company.id,
                user_id=test_user.id,
                as_of=date.today(),
                results={"dcf_value": 150.25 + i}
            )
            db_session.add(valuation)
        db_session.commit()
        
        response = client.get("/api/valuation/?skip=0&limit=2", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 2

    def test_get_all_valuations_unauthorized(self, client: TestClient):
        """Test all valuations retrieval requires authentication."""
        response = client.get("/api/valuation/")
        
        assert response.status_code == 401