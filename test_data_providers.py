"""
Test script for the modular data provider system.

This script demonstrates how to use the data provider architecture
to ingest historical price data from different sources.

Usage:
    python test_data_providers.py

Requirements:
    - Download Kaggle dataset manually to data/kaggle/stock-market-data.zip
    - Or configure Kaggle API credentials
"""

import os
import sys
from pathlib import Path
from datetime import date, timedelta
import logging

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent / "backend"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.base import Base
from data_providers import DataProviderFactory, DataProviderType, DataQuality

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_test_database():
    """Setup test database connection"""
    # Use SQLite for testing - you can change this to PostgreSQL for production
    DATABASE_URL = "sqlite:///./test_equity_valuator.db"
    
    engine = create_engine(DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    return SessionLocal()

def test_provider_factory():
    """Test the provider factory functionality"""
    logger.info("=== Testing Data Provider Factory ===")
    
    # Get available providers
    providers = DataProviderFactory.get_available_providers()
    logger.info(f"Available providers: {list(providers.keys())}")
    
    for provider_type, info in providers.items():
        logger.info(f"  {provider_type}: {info['name']} ({info['data_quality']})")

def test_kaggle_provider():
    """Test the Kaggle provider"""
    logger.info("\n=== Testing Kaggle Provider ===")
    
    db = setup_test_database()
    
    try:
        # Create Kaggle provider
        provider = DataProviderFactory.create_provider(
            DataProviderType.KAGGLE,
            db,
            settings={"data_dir": "data/kaggle"}
        )
        
        logger.info(f"Created provider: {provider.get_provider_info()}")
        
        # Test connection (checks if data is available)
        connection_ok = provider.test_connection()
        logger.info(f"Connection test: {'PASS' if connection_ok else 'FAIL'}")
        
        if not connection_ok:
            logger.warning("Kaggle data not available. Please download the dataset:")
            logger.warning("1. Go to https://www.kaggle.com/datasets/paultimothymooney/stock-market-data")
            logger.warning("2. Download to data/kaggle/stock-market-data.zip")
            logger.warning("3. Or configure Kaggle API credentials")
            return
        
        # Get available tickers (sample)
        available_tickers = provider.get_available_tickers()
        sample_tickers = list(available_tickers)[:10] if available_tickers else []
        logger.info(f"Sample available tickers: {sample_tickers}")
        
        # Test with a few popular tickers
        test_tickers = ["AAPL", "GOOGL", "MSFT", "LMT"]  # Include LMT as requested
        available_test_tickers = [t for t in test_tickers if t in available_tickers]
        
        if not available_test_tickers:
            logger.warning(f"None of the test tickers {test_tickers} are available in the dataset")
            return
        
        logger.info(f"Testing with tickers: {available_test_tickers}")
        
        # Ingest historical data
        result = provider.ingest_historical_data(available_test_tickers)
        
        logger.info("=== Ingestion Results ===")
        logger.info(f"Successful tickers: {result.successful_tickers}")
        logger.info(f"Failed tickers: {result.failed_tickers}")
        logger.info(f"Records inserted: {result.records_inserted}")
        logger.info(f"Date range: {result.date_range}")
        
        if result.errors:
            logger.error("Errors occurred:")
            for error in result.errors:
                logger.error(f"  {error}")
        
        # Get data summary for each ticker
        logger.info("\n=== Data Summaries ===")
        for ticker in result.successful_tickers:
            summary = provider.get_data_summary(ticker)
            logger.info(f"{ticker}: {summary}")
    
    except Exception as e:
        logger.error(f"Error testing Kaggle provider: {e}", exc_info=True)
    
    finally:
        db.close()

def test_multiple_providers():
    """Test creating multiple provider instances"""
    logger.info("\n=== Testing Multiple Providers ===")
    
    db = setup_test_database()
    
    try:
        # Create test instances of all available providers
        test_providers = DataProviderFactory.create_test_providers(db)
        
        logger.info(f"Created {len(test_providers)} test providers:")
        
        for provider_type, provider in test_providers.items():
            info = provider.get_provider_info()
            logger.info(f"  {provider_type}: {info['name']} (Quality: {info['data_quality']})")
            
            # Test connection for each
            connection_ok = provider.test_connection()
            logger.info(f"    Connection: {'OK' if connection_ok else 'Failed'}")
    
    except Exception as e:
        logger.error(f"Error testing multiple providers: {e}", exc_info=True)
    
    finally:
        db.close()

def demo_extensibility():
    """Demonstrate how easy it is to add new providers"""
    logger.info("\n=== Extensibility Demo ===")
    
    # This shows how you would add a new provider in the future
    logger.info("To add a new provider (e.g., Alpha Vantage):")
    logger.info("1. Create AlphaVantageProvider class inheriting from BaseDataProvider")
    logger.info("2. Implement the required methods (test_connection, ingest_historical_data, etc.)")
    logger.info("3. Add DataProviderType.ALPHA_VANTAGE to the enum")
    logger.info("4. Register in DataProviderFactory._provider_classes")
    logger.info("5. Add default configuration in DataProviderFactory._default_configs")
    logger.info("\nThat's it! The factory will handle instantiation and the API endpoints")
    logger.info("can use any provider through the same interface.")

if __name__ == "__main__":
    logger.info("Data Provider System Test")
    logger.info("=" * 50)
    
    # Create data directory
    Path("data/kaggle").mkdir(parents=True, exist_ok=True)
    
    # Run tests
    test_provider_factory()
    test_kaggle_provider()
    test_multiple_providers() 
    demo_extensibility()
    
    logger.info("\n" + "=" * 50)
    logger.info("Test completed!")