"""
Test cases for Companies API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from backend.db.models.company import Company
from backend.db.models.price import PriceData, PricePeriodType
from datetime import date, timedelta


class TestCompanyEndpoints:
    """Test company CRUD operations."""

    def test_list_companies_success(self, client: TestClient, auth_headers: dict, test_company: Company):
        """Test successful retrieval of companies list."""
        response = client.get("/api/companies/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["ticker"] == test_company.ticker
        assert data[0]["name"] == test_company.name

    def test_list_companies_unauthorized(self, client: TestClient):
        """Test companies list requires authentication."""
        response = client.get("/api/companies/")
        
        assert response.status_code == 401

    def test_list_companies_with_search(self, client: TestClient, auth_headers: dict, test_company: Company):
        """Test companies list with search functionality."""
        response = client.get("/api/companies/?search=AAPL", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["ticker"] == "AAPL"

    def test_list_companies_with_pagination(self, client: TestClient, auth_headers: dict, test_company: Company):
        """Test companies list with pagination parameters."""
        response = client.get("/api/companies/?skip=0&limit=10", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10

    def test_create_company_success(self, client: TestClient, auth_headers: dict):
        """Test successful creation of a company."""
        company_data = {
            "ticker": "MSFT",
            "name": "Microsoft Corporation",
            "country": "US",
            "currency": "USD"
        }
        
        response = client.post("/api/companies/", json=company_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["ticker"] == "MSFT"
        assert data["name"] == company_data["name"]
        assert data["country"] == company_data["country"]
        assert "id" in data

    def test_create_company_missing_required_field(self, client: TestClient, auth_headers: dict):
        """Test company creation with missing required field returns 422."""
        invalid_data = {
            "name": "Microsoft Corporation",
            "country": "US",
            "currency": "USD"
        }
        
        response = client.post("/api/companies/", json=invalid_data, headers=auth_headers)
        
        assert response.status_code == 422
        error_detail = response.json()["detail"][0]
        assert error_detail["loc"] == ["body", "ticker"]
        assert error_detail["msg"] == "Field required"

    def test_create_company_duplicate_ticker(self, client: TestClient, auth_headers: dict, test_company: Company):
        """Test creating company with duplicate ticker returns 400."""
        duplicate_data = {
            "ticker": test_company.ticker,
            "name": "Duplicate Company",
            "country": "US",
            "currency": "USD"
        }
        
        response = client.post("/api/companies/", json=duplicate_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_company_unauthorized(self, client: TestClient):
        """Test company creation requires authentication."""
        company_data = {
            "ticker": "MSFT",
            "name": "Microsoft Corporation"
        }
        
        response = client.post("/api/companies/", json=company_data)
        
        assert response.status_code == 401

    def test_get_company_success(self, client: TestClient, auth_headers: dict, test_company: Company):
        """Test successful retrieval of company details."""
        response = client.get(f"/api/companies/{test_company.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["company"]["id"] == str(test_company.id)
        assert data["company"]["ticker"] == test_company.ticker
        assert "price_data_summary" in data
        assert "total_records" in data

    def test_get_company_not_found(self, client: TestClient, auth_headers: dict):
        """Test get company with invalid ID returns 404."""
        fake_uuid = "12345678-1234-1234-1234-123456789abc"
        response = client.get(f"/api/companies/{fake_uuid}", headers=auth_headers)
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Company not found"

    def test_get_company_by_ticker_success(self, client: TestClient, auth_headers: dict, test_company: Company):
        """Test successful retrieval of company by ticker."""
        response = client.get(f"/api/companies/ticker/{test_company.ticker}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["company"]["ticker"] == test_company.ticker

    def test_get_company_by_ticker_not_found(self, client: TestClient, auth_headers: dict):
        """Test get company by invalid ticker returns 404."""
        response = client.get("/api/companies/ticker/INVALID", headers=auth_headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_update_company_success(self, client: TestClient, auth_headers: dict, test_company: Company):
        """Test successful update of company information."""
        update_data = {
            "name": "Apple Inc. Updated",
            "country": "United States"
        }
        
        response = client.put(f"/api/companies/{test_company.id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["country"] == update_data["country"]
        assert data["ticker"] == test_company.ticker  # Should remain unchanged

    def test_update_company_not_found(self, client: TestClient, auth_headers: dict):
        """Test update company with invalid ID returns 404."""
        fake_uuid = "12345678-1234-1234-1234-123456789abc"
        update_data = {"name": "Updated Name"}
        
        response = client.put(f"/api/companies/{fake_uuid}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Company not found"


class TestCompanyPriceEndpoints:
    """Test company price data endpoints."""

    def test_get_company_prices_success(self, client: TestClient, auth_headers: dict, test_company: Company, test_provider, db_session):
        """Test successful retrieval of price data."""
        # Create test price data
        test_price = PriceData(
            company_id=test_company.id,
            provider_id=test_provider.id,
            date=date.today(),
            period_type=PricePeriodType.DAILY,
            open=150.0,
            close=155.0,
            adj_close=155.0,
            volume=1000000
        )
        db_session.add(test_price)
        db_session.commit()
        
        response = client.get(f"/api/companies/{test_company.id}/prices", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["close"] == 155.0
        assert data[0]["provider_name"] == test_provider.name

    def test_get_company_prices_with_date_filter(self, client: TestClient, auth_headers: dict, test_company: Company, test_provider, db_session):
        """Test price data retrieval with date filters."""
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # Create price data for different dates
        for i, price_date in enumerate([yesterday, today]):
            test_price = PriceData(
                company_id=test_company.id,
                provider_id=test_provider.id,
                date=price_date,
                period_type=PricePeriodType.DAILY,
                close=150.0 + i
            )
            db_session.add(test_price)
        db_session.commit()
        
        response = client.get(
            f"/api/companies/{test_company.id}/prices",
            params={"start_date": str(today), "end_date": str(today)},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["date"] == str(today)

    def test_get_company_prices_by_ticker(self, client: TestClient, auth_headers: dict, test_company: Company):
        """Test price data retrieval by ticker."""
        response = client.get(f"/api/companies/ticker/{test_company.ticker}/prices", headers=auth_headers)
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_company_prices_invalid_company(self, client: TestClient, auth_headers: dict):
        """Test price data for invalid company returns 404."""
        fake_uuid = "12345678-1234-1234-1234-123456789abc"
        response = client.get(f"/api/companies/{fake_uuid}/prices", headers=auth_headers)
        
        assert response.status_code == 404


class TestDataIngestionEndpoints:
    """Test data ingestion endpoints (admin only)."""

    def test_ingest_data_admin_required(self, client: TestClient, auth_headers: dict):
        """Test data ingestion requires admin privileges."""
        ingestion_data = {
            "tickers": ["AAPL"],
            "provider_type": "kaggle"
        }
        
        response = client.post("/api/companies/ingest", json=ingestion_data, headers=auth_headers)
        
        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]

    def test_ingest_data_success_admin(self, client: TestClient, admin_headers: dict):
        """Test successful data ingestion with admin user."""
        ingestion_data = {
            "tickers": ["AAPL", "MSFT"],
            "provider_type": "kaggle"
        }
        
        response = client.post("/api/companies/ingest", json=ingestion_data, headers=admin_headers)
        
        # Should return 200 with background task started
        assert response.status_code == 200
        data = response.json()
        assert "successful_tickers" in data
        assert "errors" in data

    def test_ingest_data_invalid_provider(self, client: TestClient, admin_headers: dict):
        """Test ingestion with invalid provider type returns 400."""
        ingestion_data = {
            "tickers": ["AAPL"],
            "provider_type": "invalid_provider"
        }
        
        response = client.post("/api/companies/ingest", json=ingestion_data, headers=admin_headers)
        
        assert response.status_code == 400
        assert "Unsupported provider type" in response.json()["detail"]

    def test_ingest_data_missing_tickers(self, client: TestClient, admin_headers: dict):
        """Test ingestion with missing tickers field returns 422."""
        ingestion_data = {
            "provider_type": "kaggle"
        }
        
        response = client.post("/api/companies/ingest", json=ingestion_data, headers=admin_headers)
        
        assert response.status_code == 422
        error_detail = response.json()["detail"][0]
        assert error_detail["loc"] == ["body", "tickers"]

    def test_sync_ingest_success(self, client: TestClient, admin_headers: dict):
        """Test synchronous ingestion with small dataset."""
        ingestion_data = {
            "tickers": ["AAPL"],
            "provider_type": "kaggle"
        }
        
        response = client.post("/api/companies/ingest/sync", json=ingestion_data, headers=admin_headers)
        
        # May return 503 if provider connection fails, or 200 if successful
        assert response.status_code in [200, 503]

    def test_sync_ingest_too_many_tickers(self, client: TestClient, admin_headers: dict):
        """Test sync ingestion with too many tickers returns 400."""
        ingestion_data = {
            "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META"],  # 6 tickers
            "provider_type": "kaggle"
        }
        
        response = client.post("/api/companies/ingest/sync", json=ingestion_data, headers=admin_headers)
        
        assert response.status_code == 400
        assert "Use async endpoint" in response.json()["detail"]

    def test_get_available_providers(self, client: TestClient, auth_headers: dict):
        """Test retrieval of available data providers."""
        response = client.get("/api/companies/providers", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert isinstance(data["providers"], list)