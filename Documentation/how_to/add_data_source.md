# How to Add a New Data Source

## Problem Statement

You need to integrate a new financial data provider (such as Alpha Vantage, IEX Cloud, or a proprietary API) into the Equity Valuation System to expand data coverage or improve data quality.

## Prerequisites

- Existing Equity Valuation System installation
- API credentials for the new data provider
- Basic understanding of the data provider's API structure
- Python development environment set up

## Step 1: Create the Data Provider Class

Create a new provider class that inherits from `BaseDataProvider`.

### Create the Provider File

```bash
# Navigate to the data providers directory
cd backend/data_providers/

# Create the new provider file
touch alpha_vantage_provider.py
```

### Implement the Provider Class

```python
# backend/data_providers/alpha_vantage_provider.py

import requests
from datetime import date, datetime, timedelta
from typing import Dict, List, Set, Optional, Any
import time
import logging
from sqlalchemy.orm import Session

from .base_provider import BaseDataProvider, DataProviderConfig, IngestionResult
from backend.db.models.company import Company
from backend.db.models.price import PriceData, PricePeriodType
from backend.db.models.provider import Provider

logger = logging.getLogger(__name__)

class AlphaVantageProvider(BaseDataProvider):
    """
    Alpha Vantage API data provider for stock price data.
    
    Required configuration:
    - api_key: Alpha Vantage API key
    - base_url: API base URL (default: https://www.alphavantage.co/query)
    - rate_limit_calls_per_minute: API rate limit (default: 5)
    """
    
    def __init__(self, config: DataProviderConfig, db: Session):
        super().__init__(config)
        self.db = db
        self.api_key = config.credentials.get('api_key')
        self.base_url = config.settings.get('base_url', 'https://www.alphavantage.co/query')
        self.rate_limit_rpm = config.rate_limits.get('calls_per_minute', 5)
        self.last_request_time = 0
        
    def _validate_config(self) -> None:
        """Validate Alpha Vantage specific configuration"""
        if not self.api_key:
            raise ValueError("Alpha Vantage API key is required")
        
        if not self.api_key.strip():
            raise ValueError("Alpha Vantage API key cannot be empty")
    
    def _rate_limit_delay(self) -> None:
        """Implement rate limiting between API calls"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        min_interval = 60.0 / self.rate_limit_rpm  # seconds between requests
        
        if time_since_last_request < min_interval:
            sleep_time = min_interval - time_since_last_request
            logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def test_connection(self) -> bool:
        """Test connection to Alpha Vantage API"""
        try:
            self._rate_limit_delay()
            
            # Test with a simple API call
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': 'AAPL',
                'outputsize': 'compact',
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API error responses
            if 'Error Message' in data:
                logger.error(f"Alpha Vantage API error: {data['Error Message']}")
                return False
            
            if 'Note' in data:
                logger.warning(f"Alpha Vantage API note: {data['Note']}")
                # Note usually indicates rate limiting, but connection works
                return True
            
            # Check for expected data structure
            if 'Time Series (Daily)' in data:
                logger.info("Alpha Vantage connection test successful")
                return True
            
            logger.error(f"Unexpected Alpha Vantage API response structure: {list(data.keys())}")
            return False
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Alpha Vantage connection test failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Alpha Vantage connection test error: {e}")
            return False
    
    def get_available_tickers(self) -> Set[str]:
        """
        Get available tickers from Alpha Vantage.
        Note: Alpha Vantage doesn't provide a ticker list endpoint,
        so we return a predefined set of common tickers.
        """
        # For production, you might want to:
        # 1. Maintain a curated list of supported tickers
        # 2. Integrate with a ticker reference data service
        # 3. Allow users to manually add tickers
        
        common_tickers = {
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NFLX', 'NVDA',
            'JPM', 'JNJ', 'V', 'PG', 'UNH', 'HD', 'MA', 'DIS', 'PYPL', 'BAC',
            'ADBE', 'CRM', 'INTC', 'VZ', 'CMCSA', 'NKE', 'T', 'PFE', 'ABT',
            'WMT', 'KO', 'MRK', 'CSCO', 'XOM', 'CVX', 'PEP', 'TMO', 'COST'
        }
        
        logger.info(f"Alpha Vantage provider has {len(common_tickers)} available tickers")
        return common_tickers
    
    def ingest_historical_data(self, 
                             tickers: List[str], 
                             start_date: Optional[date] = None,
                             end_date: Optional[date] = None) -> IngestionResult:
        """Ingest historical price data from Alpha Vantage"""
        result = IngestionResult(provider_name=self.config.name)
        
        # Get provider record from database
        provider_record = self.db.query(Provider).filter(
            Provider.name == self.config.name
        ).first()
        
        if not provider_record:
            logger.error("Provider not found in database")
            result.errors.append("Provider not found in database")
            return result
        
        for ticker in tickers:
            try:
                logger.info(f"Ingesting Alpha Vantage data for {ticker}")
                
                # Get company record
                company = self.db.query(Company).filter(Company.ticker == ticker).first()
                if not company:
                    logger.warning(f"Company {ticker} not found in database, skipping")
                    result.failed_tickers.append({
                        "ticker": ticker,
                        "error": "Company not found in database"
                    })
                    continue
                
                # Fetch price data from API
                price_data = self._fetch_price_data(ticker)
                if not price_data:
                    result.failed_tickers.append({
                        "ticker": ticker,
                        "error": "Failed to fetch price data"
                    })
                    continue
                
                # Filter by date range if specified
                if start_date or end_date:
                    price_data = self._filter_by_date_range(price_data, start_date, end_date)
                
                # Store in database
                records_added = self._store_price_data(
                    company.id, 
                    provider_record.id, 
                    price_data
                )
                
                result.successful_tickers.append(ticker)
                result.records_inserted += records_added
                
                logger.info(f"Successfully ingested {records_added} records for {ticker}")
                
            except Exception as e:
                logger.error(f"Error ingesting data for {ticker}: {e}")
                result.failed_tickers.append({
                    "ticker": ticker,
                    "error": str(e)
                })
                result.errors.append(f"Error processing {ticker}: {str(e)}")
        
        # Set date range in result
        if result.successful_tickers:
            result.date_range = {
                "start_date": str(start_date) if start_date else "earliest_available",
                "end_date": str(end_date) if end_date else "latest_available"
            }
        
        return result
    
    def ingest_recent_data(self, tickers: List[str], days_back: int = 30) -> IngestionResult:
        """Ingest recent price data"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days_back)
        
        return self.ingest_historical_data(tickers, start_date, end_date)
    
    def _fetch_price_data(self, ticker: str) -> Optional[Dict[str, Dict[str, str]]]:
        """Fetch price data from Alpha Vantage API"""
        try:
            self._rate_limit_delay()
            
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': ticker,
                'outputsize': 'full',  # Get full history
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors
            if 'Error Message' in data:
                logger.error(f"Alpha Vantage API error for {ticker}: {data['Error Message']}")
                return None
            
            if 'Note' in data:
                logger.warning(f"Alpha Vantage rate limit hit for {ticker}: {data['Note']}")
                return None
            
            # Extract time series data
            if 'Time Series (Daily)' not in data:
                logger.error(f"No time series data for {ticker}")
                return None
            
            return data['Time Series (Daily)']
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {ticker}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
            return None
    
    def _filter_by_date_range(self, 
                            price_data: Dict[str, Dict[str, str]], 
                            start_date: Optional[date], 
                            end_date: Optional[date]) -> Dict[str, Dict[str, str]]:
        """Filter price data by date range"""
        if not start_date and not end_date:
            return price_data
        
        filtered_data = {}
        for date_str, values in price_data.items():
            try:
                data_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                
                if start_date and data_date < start_date:
                    continue
                if end_date and data_date > end_date:
                    continue
                
                filtered_data[date_str] = values
            except ValueError:
                logger.warning(f"Invalid date format: {date_str}")
                continue
        
        return filtered_data
    
    def _store_price_data(self, 
                         company_id: str, 
                         provider_id: int, 
                         price_data: Dict[str, Dict[str, str]]) -> int:
        """Store price data in database"""
        records_added = 0
        
        for date_str, values in price_data.items():
            try:
                # Parse date
                price_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                
                # Check if record already exists
                existing = self.db.query(PriceData).filter(
                    PriceData.company_id == company_id,
                    PriceData.provider_id == provider_id,
                    PriceData.date == price_date,
                    PriceData.period_type == PricePeriodType.DAILY
                ).first()
                
                if existing:
                    # Update existing record
                    existing.open = float(values['1. open'])
                    existing.close = float(values['4. close'])
                    existing.adj_close = float(values['5. adjusted close'])
                    existing.volume = int(values['6. volume'])
                else:
                    # Create new record
                    price_record = PriceData(
                        company_id=company_id,
                        provider_id=provider_id,
                        date=price_date,
                        period_type=PricePeriodType.DAILY,
                        open=float(values['1. open']),
                        close=float(values['4. close']),
                        adj_close=float(values['5. adjusted close']),
                        volume=int(values['6. volume'])
                    )
                    self.db.add(price_record)
                    records_added += 1
                
            except (ValueError, KeyError) as e:
                logger.warning(f"Invalid data for {date_str}: {e}")
                continue
        
        self.db.commit()
        return records_added
```

## Step 2: Register the Provider with the Factory

Update the provider factory to include your new provider.

### Update the Provider Factory

```python
# backend/data_providers/provider_factory.py

from .alpha_vantage_provider import AlphaVantageProvider
from .base_provider import DataProviderType

# Add your provider type to the enum
class DataProviderType(str, Enum):
    KAGGLE = "kaggle"
    YAHOO_FINANCE = "yahoo_finance"
    ALPHA_VANTAGE = "alpha_vantage"  # Add this line
    POLYGON = "polygon"
    QUANDL = "quandl"

class DataProviderFactory:
    _providers = {
        DataProviderType.KAGGLE: KaggleProvider,
        DataProviderType.ALPHA_VANTAGE: AlphaVantageProvider,  # Add this line
        # ... other providers
    }
```

## Step 3: Add Database Configuration

Create a database entry for your new provider.

### Add Provider Configuration

```python
# Create a script: scripts/add_alpha_vantage_provider.py

from backend.db.session import SessionLocal
from backend.db.models.provider import Provider
from backend.data_providers.base_provider import DataQuality

def add_alpha_vantage_provider():
    db = SessionLocal()
    try:
        # Check if provider already exists
        existing = db.query(Provider).filter(
            Provider.name == "Alpha Vantage"
        ).first()
        
        if existing:
            print("Alpha Vantage provider already exists")
            return
        
        # Create new provider configuration
        provider = Provider(
            name="Alpha Vantage",
            provider_type="alpha_vantage",
            data_quality="high",
            enabled=True,
            configuration={
                "api_key": "YOUR_API_KEY_HERE",
                "base_url": "https://www.alphavantage.co/query",
                "rate_limit_calls_per_minute": 5,
                "description": "Alpha Vantage provides real-time and historical stock data"
            }
        )
        
        db.add(provider)
        db.commit()
        print("Alpha Vantage provider added successfully")
        
    finally:
        db.close()

if __name__ == "__main__":
    add_alpha_vantage_provider()
```

### Run the Configuration Script

```bash
# From the project root directory
docker-compose exec backend python scripts/add_alpha_vantage_provider.py
```

## Step 4: Update Environment Variables

Add your API credentials to the environment configuration.

### Update Docker Environment

```bash
# Add to .env file
echo "ALPHA_VANTAGE_API_KEY=your_actual_api_key_here" >> .env
```

### Update Provider Configuration

```python
# Update the provider configuration in database or via API
configuration = {
    "api_key": "${ALPHA_VANTAGE_API_KEY}",  # Will be replaced with actual key
    "base_url": "https://www.alphavantage.co/query",
    "rate_limit_calls_per_minute": 5
}
```

## Step 5: Test the New Provider

Create tests to verify your provider works correctly.

### Create Unit Tests

```python
# tests/test_alpha_vantage_provider.py

import pytest
from unittest.mock import Mock, patch
from backend.data_providers.alpha_vantage_provider import AlphaVantageProvider
from backend.data_providers.base_provider import DataProviderConfig, DataProviderType, DataQuality

@pytest.fixture
def provider_config():
    return DataProviderConfig(
        name="Test Alpha Vantage",
        provider_type=DataProviderType.ALPHA_VANTAGE,
        data_quality=DataQuality.HIGH,
        credentials={"api_key": "test_api_key"},
        settings={"base_url": "https://www.alphavantage.co/query"},
        rate_limits={"calls_per_minute": 5}
    )

@pytest.fixture
def mock_db():
    return Mock()

def test_provider_initialization(provider_config, mock_db):
    provider = AlphaVantageProvider(provider_config, mock_db)
    assert provider.api_key == "test_api_key"
    assert provider.base_url == "https://www.alphavantage.co/query"

@patch('requests.get')
def test_connection_success(mock_get, provider_config, mock_db):
    # Mock successful API response
    mock_response = Mock()
    mock_response.json.return_value = {
        "Time Series (Daily)": {
            "2023-12-01": {
                "1. open": "150.00",
                "4. close": "155.00",
                "5. adjusted close": "155.00",
                "6. volume": "1000000"
            }
        }
    }
    mock_get.return_value = mock_response
    
    provider = AlphaVantageProvider(provider_config, mock_db)
    assert provider.test_connection() == True

def test_get_available_tickers(provider_config, mock_db):
    provider = AlphaVantageProvider(provider_config, mock_db)
    tickers = provider.get_available_tickers()
    assert len(tickers) > 0
    assert 'AAPL' in tickers
```

### Run the Tests

```bash
# Run specific provider tests
pytest tests/test_alpha_vantage_provider.py -v

# Run all provider tests
pytest tests/test_data_providers.py -v
```

## Step 6: Configure via the UI

Use the web interface to configure and test your new provider.

### Add Provider via Web Interface

1. **Navigate to the Providers page** in your browser
2. **Click "Add New Provider"**
3. **Fill in the configuration**:
   - Name: "Alpha Vantage Production"
   - Type: "alpha_vantage"
   - Data Quality: "high"
   - Configuration:
     ```json
     {
       "api_key": "your_actual_api_key",
       "base_url": "https://www.alphavantage.co/query",
       "rate_limit_calls_per_minute": 5
     }
     ```

### Test the Provider Connection

1. **Click "Test Connection"** for your new provider
2. **Verify the test passes**
3. **Check the logs** for any error messages

## Step 7: Ingest Data

Use your new provider to ingest financial data.

### Manual Data Ingestion

```python
# Create a script: scripts/ingest_alpha_vantage_data.py

from backend.db.session import SessionLocal
from backend.data_providers import DataProviderFactory, DataProviderType
from datetime import date, timedelta

def ingest_sample_data():
    db = SessionLocal()
    try:
        # Create provider instance
        provider = DataProviderFactory.create_provider(
            DataProviderType.ALPHA_VANTAGE,
            db
        )
        
        # Test connection
        if not provider.test_connection():
            print("Provider connection failed")
            return
        
        # Ingest data for sample companies
        tickers = ["AAPL", "MSFT", "GOOGL"]
        end_date = date.today()
        start_date = end_date - timedelta(days=365)  # Last year
        
        result = provider.ingest_historical_data(tickers, start_date, end_date)
        
        print(f"Ingestion complete:")
        print(f"  Successful: {len(result.successful_tickers)} companies")
        print(f"  Failed: {len(result.failed_tickers)} companies")
        print(f"  Records inserted: {result.records_inserted:,}")
        
        if result.failed_tickers:
            print("Failed tickers:")
            for failure in result.failed_tickers:
                print(f"  {failure['ticker']}: {failure['error']}")
        
    finally:
        db.close()

if __name__ == "__main__":
    ingest_sample_data()
```

### Run Data Ingestion

```bash
docker-compose exec backend python scripts/ingest_alpha_vantage_data.py
```

## Troubleshooting

### Common Issues and Solutions

**API Key Issues**
```bash
# Verify API key is set correctly
docker-compose exec backend printenv | grep ALPHA_VANTAGE

# Test API key manually
curl "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=AAPL&apikey=YOUR_API_KEY"
```

**Rate Limiting Problems**
- Check the `calls_per_minute` setting in your configuration
- Monitor the provider logs for rate limiting messages
- Consider upgrading to a paid API plan for higher limits

**Data Format Issues**
- Verify the API response structure matches your parser
- Add logging to see the actual API responses
- Handle edge cases (missing fields, different date formats)

**Database Connection Issues**
```bash
# Check database connectivity
docker-compose exec backend python -c "
from backend.db.session import SessionLocal
db = SessionLocal()
print('Database connection successful')
db.close()
"
```

## Verification

To verify your new provider is working correctly:

1. **Check provider status** in the web interface
2. **Verify data ingestion** by viewing company price charts
3. **Compare data quality** with existing providers
4. **Monitor error logs** for any recurring issues
5. **Test rate limiting** by making multiple rapid requests

## Next Steps

After successfully adding your new data provider:

- **Configure field mappings** for any provider-specific data fields
- **Set up automated data refresh** schedules
- **Monitor data quality** and consistency over time
- **Document any provider-specific quirks** for future reference
- **Consider adding additional endpoints** (fundamental data, news, etc.)

Your new data source is now fully integrated into the Equity Valuation System and ready for production use!