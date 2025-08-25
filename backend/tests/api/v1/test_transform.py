"""
Test cases for Transform API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from backend.db.models.mapping import MappedField, RawDataEntry, ValueType, PeriodType
from backend.db.models.field import CanonicalField
from backend.db.models.provider import Provider
from backend.db.models.company import Company
from datetime import date


class TestTransformMappingEndpoints:
    """Test transform mapping CRUD operations."""

    def test_create_mapping_success(self, client: TestClient, admin_headers: dict, test_provider: Provider, canonical_fields: list):
        """Test successful creation of a field mapping by admin."""
        mapping_data = {
            "provider_id": test_provider.id,
            "canonical_id": canonical_fields[0].id,
            "raw_field_name": "total_revenue_raw",
            "transform_expression": {
                "op": "multiply",
                "args": [
                    {"field": "revenue_raw"},
                    {"value": 1000}
                ]
            }
        }
        
        response = client.post("/api/transform/mappings", json=mapping_data, headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["provider_id"] == test_provider.id
        assert data["canonical_id"] == canonical_fields[0].id
        assert data["raw_field_name"] == "total_revenue_raw"
        assert "id" in data

    def test_create_mapping_missing_provider_id(self, client: TestClient, admin_headers: dict, canonical_fields: list):
        """Test mapping creation with missing provider_id returns 422."""
        invalid_data = {
            "canonical_id": canonical_fields[0].id,
            "raw_field_name": "revenue_raw"
        }
        
        response = client.post("/api/transform/mappings", json=invalid_data, headers=admin_headers)
        
        assert response.status_code == 422
        error_detail = response.json()["detail"][0]
        assert error_detail["loc"] == ["body", "provider_id"]
        assert error_detail["msg"] == "Field required"

    def test_create_mapping_missing_canonical_id(self, client: TestClient, admin_headers: dict, test_provider: Provider):
        """Test mapping creation with missing canonical_id returns 422."""
        invalid_data = {
            "provider_id": test_provider.id,
            "raw_field_name": "revenue_raw"
        }
        
        response = client.post("/api/transform/mappings", json=invalid_data, headers=admin_headers)
        
        assert response.status_code == 422
        error_detail = response.json()["detail"][0]
        assert error_detail["loc"] == ["body", "canonical_id"]

    def test_create_mapping_missing_raw_field_name(self, client: TestClient, admin_headers: dict, test_provider: Provider, canonical_fields: list):
        """Test mapping creation with missing raw_field_name returns 422."""
        invalid_data = {
            "provider_id": test_provider.id,
            "canonical_id": canonical_fields[0].id
        }
        
        response = client.post("/api/transform/mappings", json=invalid_data, headers=admin_headers)
        
        assert response.status_code == 422
        error_detail = response.json()["detail"][0]
        assert error_detail["loc"] == ["body", "raw_field_name"]

    def test_create_mapping_admin_required(self, client: TestClient, auth_headers: dict, test_provider: Provider, canonical_fields: list):
        """Test mapping creation requires admin privileges."""
        mapping_data = {
            "provider_id": test_provider.id,
            "canonical_id": canonical_fields[0].id,
            "raw_field_name": "revenue_raw"
        }
        
        response = client.post("/api/transform/mappings", json=mapping_data, headers=auth_headers)
        
        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]

    def test_create_mapping_unauthorized(self, client: TestClient, test_provider: Provider, canonical_fields: list):
        """Test mapping creation without authentication returns 401."""
        mapping_data = {
            "provider_id": test_provider.id,
            "canonical_id": canonical_fields[0].id,
            "raw_field_name": "revenue_raw"
        }
        
        response = client.post("/api/transform/mappings", json=mapping_data)
        
        assert response.status_code == 401

    def test_get_mappings_success(self, client: TestClient, auth_headers: dict, test_provider: Provider, canonical_fields: list, db_session):
        """Test successful retrieval of mappings."""
        # Create test mapping
        mapping = MappedField(
            provider_id=test_provider.id,
            canonical_id=canonical_fields[0].id,
            raw_field_name="test_field"
        )
        db_session.add(mapping)
        db_session.commit()
        
        response = client.get("/api/transform/mappings", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_mappings_with_provider_filter(self, client: TestClient, auth_headers: dict, test_provider: Provider, canonical_fields: list, db_session):
        """Test mappings retrieval with provider filter."""
        # Create test mapping
        mapping = MappedField(
            provider_id=test_provider.id,
            canonical_id=canonical_fields[0].id,
            raw_field_name="test_field"
        )
        db_session.add(mapping)
        db_session.commit()
        
        response = client.get(f"/api/transform/mappings?provider_id={test_provider.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for mapping_data in data:
            assert mapping_data["provider_id"] == test_provider.id

    def test_update_mapping_success(self, client: TestClient, admin_headers: dict, test_provider: Provider, canonical_fields: list, db_session):
        """Test successful update of a mapping."""
        # Create test mapping
        mapping = MappedField(
            provider_id=test_provider.id,
            canonical_id=canonical_fields[0].id,
            raw_field_name="old_field_name"
        )
        db_session.add(mapping)
        db_session.commit()
        db_session.refresh(mapping)
        
        update_data = {
            "provider_id": test_provider.id,
            "canonical_id": canonical_fields[0].id,
            "raw_field_name": "updated_field_name"
        }
        
        response = client.put(f"/api/transform/mappings/{mapping.id}", json=update_data, headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["raw_field_name"] == "updated_field_name"

    def test_update_mapping_not_found(self, client: TestClient, admin_headers: dict, test_provider: Provider, canonical_fields: list):
        """Test update mapping with invalid ID returns 404."""
        fake_uuid = "12345678-1234-1234-1234-123456789abc"
        update_data = {
            "provider_id": test_provider.id,
            "canonical_id": canonical_fields[0].id,
            "raw_field_name": "updated_field"
        }
        
        response = client.put(f"/api/transform/mappings/{fake_uuid}", json=update_data, headers=admin_headers)
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Mapping not found"

    def test_delete_mapping_success(self, client: TestClient, admin_headers: dict, test_provider: Provider, canonical_fields: list, db_session):
        """Test successful deletion of a mapping."""
        # Create test mapping
        mapping = MappedField(
            provider_id=test_provider.id,
            canonical_id=canonical_fields[0].id,
            raw_field_name="field_to_delete"
        )
        db_session.add(mapping)
        db_session.commit()
        db_session.refresh(mapping)
        
        response = client.delete(f"/api/transform/mappings/{mapping.id}", headers=admin_headers)
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]

    def test_delete_mapping_not_found(self, client: TestClient, admin_headers: dict):
        """Test delete mapping with invalid ID returns 404."""
        fake_uuid = "12345678-1234-1234-1234-123456789abc"
        response = client.delete(f"/api/transform/mappings/{fake_uuid}", headers=admin_headers)
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Mapping not found"


class TestCanonicalFieldsEndpoint:
    """Test canonical fields retrieval."""

    def test_get_canonical_fields_success(self, client: TestClient, auth_headers: dict, canonical_fields: list):
        """Test successful retrieval of canonical fields."""
        response = client.get("/api/transform/canonical-fields", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= len(canonical_fields)
        
        # Verify field structure
        first_field = data[0]
        assert "id" in first_field
        assert "code" in first_field
        assert "name" in first_field
        assert "display_name" in first_field
        assert "type" in first_field
        assert "category" in first_field

    def test_get_canonical_fields_unauthorized(self, client: TestClient):
        """Test canonical fields retrieval requires authentication."""
        response = client.get("/api/transform/canonical-fields")
        
        assert response.status_code == 401


class TestRawFieldsEndpoint:
    """Test raw fields retrieval."""

    def test_get_provider_raw_fields_success(self, client: TestClient, auth_headers: dict, test_provider: Provider, test_company: Company, db_session):
        """Test successful retrieval of raw fields for a provider."""
        # Create test raw data entry
        raw_entry = RawDataEntry(
            provider_id=test_provider.id,
            company_id=test_company.id,
            fiscal_period=date.today(),
            period_type=PeriodType.ANNUAL,
            raw_field_name="test_raw_field",
            value_type=ValueType.NUMBER,
            value=100.0
        )
        db_session.add(raw_entry)
        db_session.commit()
        
        response = client.get(f"/api/transform/providers/{test_provider.id}/raw-fields", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "provider_id" in data
        assert "raw_fields" in data
        assert data["provider_id"] == test_provider.id
        assert isinstance(data["raw_fields"], list)
        assert "test_raw_field" in data["raw_fields"]

    def test_get_provider_raw_fields_empty(self, client: TestClient, auth_headers: dict, test_provider: Provider):
        """Test raw fields retrieval for provider with no data."""
        response = client.get(f"/api/transform/providers/{test_provider.id}/raw-fields", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["raw_fields"] == []


class TestTransformTestEndpoint:
    """Test transform expression testing."""

    def test_test_transform_success(self, client: TestClient, auth_headers: dict):
        """Test successful transform expression evaluation."""
        test_data = {
            "expression": {
                "op": "add",
                "args": [
                    {"field": "field1"},
                    {"value": 10}
                ]
            },
            "sample_data": {
                "field1": 5
            }
        }
        
        response = client.post("/api/transform/test-transform", json=test_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["result"] == 15

    def test_test_transform_invalid_expression(self, client: TestClient, auth_headers: dict):
        """Test transform with invalid expression returns error."""
        test_data = {
            "expression": {
                "op": "divide",
                "args": [
                    {"field": "field1"},
                    {"value": 0}
                ]
            },
            "sample_data": {
                "field1": 10
            }
        }
        
        response = client.post("/api/transform/test-transform", json=test_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "error" in data

    def test_test_transform_missing_field(self, client: TestClient, auth_headers: dict):
        """Test transform with missing field in sample data."""
        test_data = {
            "expression": {
                "field": "nonexistent_field"
            },
            "sample_data": {
                "other_field": 5
            }
        }
        
        response = client.post("/api/transform/test-transform", json=test_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "not found" in data["error"]


class TestMappingBackupEndpoint:
    """Test mapping backup functionality."""

    def test_download_mappings_backup_success(self, client: TestClient, admin_headers: dict, test_provider: Provider, canonical_fields: list, db_session):
        """Test successful download of mappings backup."""
        # Create test mapping
        mapping = MappedField(
            provider_id=test_provider.id,
            canonical_id=canonical_fields[0].id,
            raw_field_name="test_backup_field"
        )
        db_session.add(mapping)
        db_session.commit()
        
        response = client.get(f"/api/transform/backup/{test_provider.id}", headers=admin_headers)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        assert "attachment" in response.headers["content-disposition"]
        
        # Verify JSON structure
        import json
        backup_data = json.loads(response.content.decode())
        assert "provider" in backup_data
        assert "mappings" in backup_data
        assert backup_data["provider"]["name"] == test_provider.name

    def test_download_mappings_backup_provider_not_found(self, client: TestClient, admin_headers: dict):
        """Test backup download for non-existent provider returns 404."""
        response = client.get("/api/transform/backup/99999", headers=admin_headers)
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Provider not found"

    def test_download_mappings_backup_admin_required(self, client: TestClient, auth_headers: dict, test_provider: Provider):
        """Test backup download requires admin privileges."""
        response = client.get(f"/api/transform/backup/{test_provider.id}", headers=auth_headers)
        
        assert response.status_code == 403


class TestSpecificMappingEndpoint:
    """Test specific field mapping retrieval."""

    def test_get_field_mapping_success(self, client: TestClient, auth_headers: dict, test_provider: Provider, canonical_fields: list, db_session):
        """Test successful retrieval of specific field mapping."""
        # Create test mapping
        mapping = MappedField(
            provider_id=test_provider.id,
            canonical_id=canonical_fields[0].id,
            raw_field_name="specific_field",
            transform_expression={"op": "multiply", "args": [{"field": "raw"}, {"value": 2}]}
        )
        db_session.add(mapping)
        db_session.commit()
        
        response = client.get(
            f"/api/transform/mappings/{test_provider.id}/{canonical_fields[0].id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["raw_field_name"] == "specific_field"
        assert data["transform_expression"] is not None

    def test_get_field_mapping_not_found(self, client: TestClient, auth_headers: dict, test_provider: Provider, canonical_fields: list):
        """Test get mapping for non-existent combination returns empty mapping."""
        response = client.get(
            f"/api/transform/mappings/{test_provider.id}/{canonical_fields[0].id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["raw_field_name"] == ""
        assert data["transform_expression"] is None