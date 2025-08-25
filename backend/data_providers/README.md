# Data Providers Module

## Overview

The data providers module implements a pluggable architecture for ingesting financial data from multiple sources. This module enables the Equity Valuation System to integrate with various data providers while maintaining a consistent interface and data quality standards.

## Role and Responsibilities

### Primary Functions
- **Data Source Abstraction**: Provides a unified interface for accessing financial data regardless of source
- **Connection Management**: Handles authentication, rate limiting, and connection lifecycle for each provider
- **Data Ingestion**: Coordinates bulk and incremental data loading from external sources
- **Quality Control**: Validates and normalizes data according to provider-specific quality levels
- **Error Handling**: Provides robust error handling and retry mechanisms for external API failures

### Key Components
- `BaseDataProvider`: Abstract base class defining the provider interface
- `DataProviderFactory`: Factory pattern implementation for creating provider instances
- `KaggleProvider`: Kaggle dataset integration for historical stock data
- Provider configuration and metadata management

## Architecture

### Provider Interface Design
```python
class BaseDataProvider(ABC):
    def test_connection() -> bool
    def get_available_tickers() -> Set[str]
    def ingest_historical_data(tickers, start_date, end_date) -> IngestionResult
    def ingest_recent_data(tickers, days_back) -> IngestionResult
```

### Factory Pattern Implementation
The `DataProviderFactory` uses the factory pattern to:
- Dynamically instantiate providers based on configuration
- Manage provider lifecycle and dependency injection
- Support runtime provider registration and discovery

### Data Flow
1. **Configuration**: Provider settings loaded from database or environment
2. **Instantiation**: Factory creates provider instances with validated config
3. **Connection Test**: Provider validates credentials and connectivity  
4. **Data Discovery**: Provider queries available tickers/instruments
5. **Data Ingestion**: Provider fetches and transforms data into standardized format
6. **Result Processing**: System processes ingestion results and updates database

## Key Dependencies

### External Libraries
- `requests`: HTTP client for API interactions
- `pandas`: Data manipulation and transformation
- `sqlalchemy`: Database ORM integration
- `pydantic`: Data validation and settings management

### Internal Dependencies
- `backend.db.models`: Database models for data persistence
- `backend.db.session`: Database session management
- `backend.config`: Application configuration settings

## Setup Instructions

### Environment Configuration
```bash
# Set data directories
export KAGGLE_DATA_DIR="/app/data/kaggle"
export YAHOO_FINANCE_API_KEY="your-api-key"

# Configure rate limiting
export PROVIDER_RATE_LIMIT_RPM=60
```

### Database Initialization
```python
from backend.data_providers import DataProviderFactory, DataProviderType

# Create provider configuration
provider_config = DataProviderConfig(
    name="Kaggle Stock Data",
    provider_type=DataProviderType.KAGGLE,
    data_quality=DataQuality.MEDIUM,
    settings={"data_dir": "/app/data/kaggle"}
)

# Initialize provider
provider = DataProviderFactory.create_provider(
    DataProviderType.KAGGLE,
    db_session,
    config=provider_config
)
```

## Usage Guide

### Creating a New Provider
1. **Inherit from BaseDataProvider**:
```python
class CustomProvider(BaseDataProvider):
    def _validate_config(self):
        # Validate provider-specific configuration
        pass
    
    def test_connection(self) -> bool:
        # Test API connectivity
        pass
    
    def get_available_tickers(self) -> Set[str]:
        # Return available instruments
        pass
```

2. **Register with Factory**:
```python
DataProviderFactory.register_provider(
    DataProviderType.CUSTOM,
    CustomProvider
)
```

3. **Configure in Database**:
```python
provider_config = Provider(
    name="Custom Data Source",
    provider_type="custom",
    data_quality="high",
    configuration={
        "api_endpoint": "https://api.example.com",
        "credentials": {"api_key": "secret"}
    }
)
```

### Ingesting Data
```python
# Test provider connectivity
if not provider.test_connection():
    logger.error("Provider connection failed")
    return

# Get available tickers
available_tickers = provider.get_available_tickers()
target_tickers = ["AAPL", "MSFT", "GOOGL"]
loadable_tickers = [t for t in target_tickers if t in available_tickers]

# Ingest historical data
result = provider.ingest_historical_data(
    tickers=loadable_tickers,
    start_date=date(2020, 1, 1),
    end_date=date(2023, 12, 31)
)

# Process results
logger.info(f"Loaded {len(result.successful_tickers)} companies")
logger.info(f"Inserted {result.records_inserted:,} price records")
```

## Testing Instructions

### Unit Tests
```bash
# Run provider-specific tests
pytest tests/test_data_providers.py -v

# Test specific provider
pytest tests/test_kaggle_provider.py -v

# Test with coverage
pytest tests/test_data_providers.py --cov=backend.data_providers
```

### Integration Tests
```bash
# Test with real data sources (requires credentials)
pytest tests/integration/test_provider_integration.py -v

# Test data ingestion pipeline
pytest tests/integration/test_data_ingestion.py -v
```

### Manual Testing
```python
# Test provider registration and discovery
from backend.data_providers import DataProviderFactory, DataProviderType

# List available provider types
available_types = DataProviderFactory.get_available_types()
print(f"Available providers: {available_types}")

# Test provider instantiation
provider = DataProviderFactory.create_provider(
    DataProviderType.KAGGLE,
    db_session
)

# Test connection
connection_ok = provider.test_connection()
print(f"Connection test: {'PASS' if connection_ok else 'FAIL'}")
```

## Error Handling

### Connection Failures
- **Automatic Retry**: Exponential backoff for transient failures
- **Circuit Breaker**: Temporary disable after repeated failures
- **Fallback Providers**: Route to alternative data sources when available

### Data Quality Issues
- **Validation Pipeline**: Multi-stage data validation before persistence
- **Quarantine System**: Isolate suspicious data for manual review
- **Data Lineage**: Track data provenance for audit and debugging

### Rate Limiting
- **Adaptive Throttling**: Adjust request rates based on provider responses
- **Queue Management**: Buffer requests during high-demand periods
- **Priority Scheduling**: Prioritize critical data updates

## Performance Considerations

### Batch Processing
- **Chunk Size Optimization**: Balance memory usage and processing speed
- **Parallel Processing**: Multi-threaded ingestion for independent tickers
- **Database Bulk Operations**: Use bulk inserts for large datasets

### Caching Strategy
- **Provider Metadata**: Cache available tickers and instrument details
- **Rate Limit State**: Cache rate limit counters to prevent overages
- **Configuration Cache**: Avoid repeated database queries for provider settings

### Monitoring
- **Ingestion Metrics**: Track success rates, latency, and throughput
- **Data Freshness**: Monitor last update timestamps for each provider
- **Error Rates**: Alert on elevated failure rates or data quality issues

## Configuration Reference

### Provider Types
- `kaggle`: Kaggle datasets (CSV files)
- `yahoo_finance`: Yahoo Finance API
- `alpha_vantage`: Alpha Vantage API  
- `polygon`: Polygon.io API
- `quandl`: Quandl/NASDAQ Data Link

### Data Quality Levels
- `high`: Real-time, premium data sources
- `medium`: Daily updates, free/reliable sources  
- `low`: Historical data only, irregular updates
- `test`: Development/testing data

### Required Configuration Fields
```json
{
  "name": "Provider Display Name",
  "provider_type": "kaggle|yahoo_finance|alpha_vantage|polygon|quandl", 
  "data_quality": "high|medium|low|test",
  "enabled": true,
  "configuration": {
    "api_key": "provider-specific-api-key",
    "base_url": "https://api.provider.com",
    "rate_limit_rpm": 60,
    "timeout_seconds": 30
  }
}
```