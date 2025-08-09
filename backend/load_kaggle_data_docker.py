"""
Load Kaggle Data Script for Docker Environment

This script uses our Kaggle provider to load historical price data
for companies from the sample/Kaggle dataset.

Run with: docker-compose exec backend python backend/load_kaggle_data_docker.py
"""

import sys
import os
from datetime import date
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import from the current container environment
from backend.db.session import get_db
from backend.data_providers import DataProviderFactory, DataProviderType

# Companies to load
TARGET_COMPANIES = ["AAPL", "MSFT", "GOOGL", "NVDA", "LMT"]

def main():
    """Main function to load Kaggle data"""
    
    logger.info("🚀 Starting Kaggle data loading process")
    logger.info(f"Loading historical price data for: {', '.join(TARGET_COMPANIES)}")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create Kaggle provider instance
        logger.info("🏭 Creating Kaggle data provider...")
        
        provider = DataProviderFactory.create_provider(
            DataProviderType.KAGGLE,
            db,
            settings={
                "data_dir": "/app/data/kaggle"  # Path inside Docker container
            }
        )
        
        # Test connection
        logger.info("🔍 Testing provider connection...")
        if not provider.test_connection():
            logger.error("❌ Provider connection test failed")
            return False
        
        logger.info("✅ Provider connection successful")
        
        # Get available tickers
        logger.info("📋 Checking available tickers...")
        available_tickers = provider.get_available_tickers()
        logger.info(f"Available tickers: {sorted(available_tickers)}")
        
        # Filter to only companies we have data for
        loadable_companies = [ticker for ticker in TARGET_COMPANIES if ticker in available_tickers]
        missing_companies = [ticker for ticker in TARGET_COMPANIES if ticker not in available_tickers]
        
        if missing_companies:
            logger.warning(f"⚠️ Missing data for: {missing_companies}")
        
        if not loadable_companies:
            logger.error("❌ No companies available for loading")
            return False
        
        logger.info(f"📊 Loading data for: {loadable_companies}")
        
        # Ingest historical data
        logger.info("⏳ Starting data ingestion...")
        result = provider.ingest_historical_data(loadable_companies)
        
        # Display results
        logger.info("\n" + "="*60)
        logger.info("📊 INGESTION RESULTS")
        logger.info("="*60)
        logger.info(f"✅ Successfully loaded: {len(result.successful_tickers)} companies")
        
        if result.successful_tickers:
            logger.info(f"   Companies: {', '.join(result.successful_tickers)}")
        
        if result.failed_tickers:
            logger.info(f"❌ Failed to load: {len(result.failed_tickers)} companies")
            for failed in result.failed_tickers:
                logger.info(f"   {failed['ticker']}: {failed['error']}")
        
        logger.info(f"📈 Total records inserted: {result.records_inserted:,}")
        
        if result.date_range:
            logger.info(f"📅 Date range: {result.date_range.get('start_date')} to {result.date_range.get('end_date')}")
        
        if result.errors:
            logger.info("⚠️ Errors encountered:")
            for error in result.errors:
                logger.info(f"   {error}")
        
        # Get summary for each company
        logger.info("\n📋 Company Data Summaries:")
        for ticker in result.successful_tickers:
            try:
                summary = provider.get_data_summary(ticker)
                logger.info(f"   {ticker}: {summary.get('record_count', 0):,} records")
                if summary.get('start_date') and summary.get('end_date'):
                    logger.info(f"      📅 {summary['start_date']} to {summary['end_date']}")
            except Exception as e:
                logger.info(f"   {ticker}: Error getting summary - {e}")
        
        # Final database statistics
        logger.info("\n📈 Database Statistics:")
        from backend.db.models.company import Company
        from backend.db.models.price import PriceData
        
        total_companies = db.query(Company).count()
        total_price_records = db.query(PriceData).count()
        
        logger.info(f"   Total companies: {total_companies}")
        logger.info(f"   Total price records: {total_price_records:,}")
        
        # Show companies with price data
        companies_with_data = db.query(Company).join(PriceData).distinct().all()
        logger.info(f"   Companies with price data: {len(companies_with_data)}")
        for company in companies_with_data:
            price_count = db.query(PriceData).filter(PriceData.company_id == company.id).count()
            logger.info(f"      {company.ticker}: {price_count:,} records")
        
        logger.info("\n🎯 SUCCESS!")
        logger.info("Historical price data loaded successfully.")
        logger.info("You can now:")
        logger.info("1. Visit http://localhost:3000/companies to see the companies")
        logger.info("2. Click on any company to view price charts")
        logger.info("3. Test the API at http://localhost:8000/docs")
        
        return len(result.successful_tickers) > 0
        
    except Exception as e:
        logger.error(f"💥 Critical error: {e}", exc_info=True)
        return False
    
    finally:
        db.close()

if __name__ == "__main__":
    success = main()
    if not success:
        logger.error("❌ Data loading failed")
        sys.exit(1)
    else:
        logger.info("✅ Data loading completed successfully!")