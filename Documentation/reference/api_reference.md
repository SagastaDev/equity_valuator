# API Reference

This document provides detailed information about the Equity Valuation System REST API endpoints.

## Base URL

- Development: `http://localhost:8000`
- Production: Configure via environment variables

## Authentication

All protected endpoints require JWT authentication via the `Authorization` header:

```
Authorization: Bearer <jwt_token>
```

## Endpoints

### Authentication

#### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "username": "string",
  "email": "user@example.com", 
  "password": "string"
}
```

**Response:**
```json
{
  "id": "uuid",
  "username": "string",
  "email": "user@example.com",
  "is_active": true
}
```

**Status Codes:**
- `201`: User created successfully
- `400`: Invalid input data
- `409`: Username or email already exists

#### POST /auth/login  
Authenticate user and receive access token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "username": "string", 
    "email": "user@example.com"
  }
}
```

**Status Codes:**
- `200`: Authentication successful
- `401`: Invalid credentials

### Companies

#### GET /companies
Get paginated list of companies.

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum records to return (default: 100)

**Response:**
```json
[
  {
    "id": "uuid",
    "ticker": "AAPL",
    "name": "Apple Inc.",
    "country": "US",
    "currency": "USD",
    "industry_id": 1,
    "industry": {
      "id": 1,
      "code": "TECH",
      "name": "Technology",
      "description": "Technology companies"
    }
  }
]
```

#### GET /companies/{company_id}
Get specific company by ID.

**Path Parameters:**
- `company_id` (uuid): Company UUID

**Response:**
```json
{
  "id": "uuid",
  "ticker": "AAPL", 
  "name": "Apple Inc.",
  "country": "US",
  "currency": "USD",
  "industry_id": 1,
  "industry": {
    "id": 1,
    "code": "TECH",
    "name": "Technology"
  }
}
```

**Status Codes:**
- `200`: Company found
- `404`: Company not found

#### GET /companies/{company_id}/prices
Get historical price data for a company.

**Path Parameters:**
- `company_id` (uuid): Company UUID

**Query Parameters:**
- `start_date` (date, optional): Start date (YYYY-MM-DD)
- `end_date` (date, optional): End date (YYYY-MM-DD)
- `limit` (int, optional): Maximum records to return

**Response:**
```json
[
  {
    "id": "uuid",
    "company_id": "uuid",
    "date": "2023-12-01",
    "open": 189.50,
    "high": 191.20,
    "low": 188.80,
    "close": 190.95,
    "volume": 45678900,
    "adjusted_close": 190.95,
    "provider_id": "uuid"
  }
]
```

### Valuation

#### POST /api/valuation/
Create a new valuation result.

**Authentication:** Required

**Request Body:**
```json
{
  "company_id": "uuid",
  "as_of": "2023-12-01",
  "results": {
    "dcf_value": 150.00,
    "pe_ratio": 25.5,
    "price_to_book": 5.2,
    "methodology": "DCF Analysis"
  }
}
```

**Response:**
```json
{
  "id": "uuid",
  "company_id": "uuid", 
  "as_of": "2023-12-01",
  "user_id": "uuid",
  "results": {
    "dcf_value": 150.00,
    "pe_ratio": 25.5,
    "price_to_book": 5.2,
    "methodology": "DCF Analysis"
  },
  "created_at": "2023-12-01T10:30:00Z"
}
```

**Status Codes:**
- `201`: Valuation created successfully
- `400`: Invalid input data
- `401`: Authentication required
- `404`: Company not found

#### GET /api/valuation/{company_id}
Get all valuations for a specific company.

**Authentication:** Required

**Path Parameters:**
- `company_id` (uuid): Company UUID

**Response:**
```json
[
  {
    "id": "uuid",
    "company_id": "uuid",
    "as_of": "2023-12-01", 
    "user_id": "uuid",
    "results": {
      "dcf_value": 150.00,
      "pe_ratio": 25.5,
      "methodology": "DCF Analysis"
    },
    "created_at": "2023-12-01T10:30:00Z"
  }
]
```

#### GET /api/valuation/
Get all valuations (paginated).

**Authentication:** Required

**Query Parameters:**
- `skip` (int, optional): Number of records to skip
- `limit` (int, optional): Maximum records to return (max 100)

### Data Providers

#### GET /api/providers
Get list of configured data providers.

**Authentication:** Required

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Kaggle Provider",
    "provider_type": "kaggle",
    "data_quality": "medium",
    "enabled": true,
    "configuration": {
      "data_dir": "/app/data/kaggle"
    },
    "created_at": "2023-12-01T10:00:00Z",
    "updated_at": "2023-12-01T10:00:00Z"
  }
]
```

#### POST /api/providers
Create a new data provider configuration.

**Authentication:** Required

**Request Body:**
```json
{
  "name": "New Provider",
  "provider_type": "yahoo_finance",
  "data_quality": "high",
  "enabled": true,
  "configuration": {
    "api_key": "your-api-key"
  }
}
```

#### GET /api/providers/{provider_id}/test
Test connection to a data provider.

**Authentication:** Required

**Path Parameters:**
- `provider_id` (uuid): Provider UUID

**Response:**
```json
{
  "provider_id": "uuid",
  "provider_name": "Kaggle Provider", 
  "connection_successful": true,
  "test_timestamp": "2023-12-01T10:30:00Z",
  "message": "Connection test successful"
}
```

### Data Transformation

#### GET /api/transform/canonical-fields
Get list of canonical field definitions.

**Authentication:** Required

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "revenue",
    "display_name": "Revenue",
    "data_type": "decimal",
    "category": "income_statement",
    "description": "Total company revenue",
    "validation_rules": {
      "min_value": 0,
      "required": true
    }
  }
]
```

#### POST /api/transform/mappings
Create field mapping between raw data and canonical fields.

**Authentication:** Required

**Request Body:**
```json
{
  "provider_id": "uuid",
  "raw_field": "total_revenue",
  "canonical_field_id": "uuid",
  "transformation_rule": "direct",
  "multiplier": 1000000
}
```

## Error Responses

All endpoints may return these common error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid input data",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

API requests are rate limited to prevent abuse:

- **Authentication endpoints**: 5 requests per minute per IP
- **Data ingestion endpoints**: 10 requests per minute per user  
- **Query endpoints**: 100 requests per minute per user

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Request limit per window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Time when rate limit window resets

## Pagination

List endpoints support cursor-based pagination:

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records per page (default: 100, max: 1000)

**Response Headers:**
- `X-Total-Count`: Total number of records
- `Link`: Next/previous page links (if applicable)