"""
Load Companies Script

This script loads 5 real companies with maximum historical data available.
Companies include Lockheed Martin (LMT) as requested, plus 4 other major companies.

This uses the existing FinancialDataService (Yahoo Finance integration) 
rather than the new provider system for now, to ensure we get real data.
"""

import sys
import os
from pathlib import Path
from datetime import date, timedelta
import logging

# Add backend to Python path
sys.path.append(str(Path(__file__).parent / "backend"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.base import Base
from db.models.company import Company
from db.models.price import PriceData
from services.financial_data_service import FinancialDataService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Companies to load - including LMT as requested
COMPANIES = [
    "LMT",   # Lockheed Martin (as requested)
    "AAPL",  # Apple
    "MSFT",  # Microsoft  
    "GOOGL", # Alphabet/Google
    "NVDA"   # NVIDIA
]

def get_database_session():
    """Get database session"""
    # Use the same database as the main application
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./equity_valuator.db")
    
    engine = create_engine(DATABASE_URL, echo=False)
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def load_company_data(ticker: str, db_session, financial_service: FinancialDataService):
    """Load historical data for a single company"""
    
    logger.info(f"Loading data for {ticker}...")
    
    try:
        # Calculate date range - get maximum historical data (5 years)
        end_date = date.today()
        start_date = end_date - timedelta(days=5*365)  # ~5 years
        
        # Fetch and store company data
        result = financial_service.fetch_and_store_company_data(ticker, start_date, end_date)
        
        # Get the company record
        company = db_session.query(Company).filter(Company.ticker == ticker).first()
        
        if company:
            # Count price records
            price_count = db_session.query(PriceData).filter(PriceData.company_id == company.id).count()
            
            logger.info(f"✅ {ticker} ({company.name}):")
            logger.info(f"   - Price records: {price_count}")
            logger.info(f"   - Country: {company.country}")
            logger.info(f"   - Currency: {company.currency}")
            
            # Show some financial metrics if available
            if result and isinstance(result, dict):
                metrics = []
                for key in ['market_cap', 'enterprise_value', 'ebitda', 'total_revenue']:
                    if key in result and result[key]:
                        value = result[key]
                        if isinstance(value, (int, float)) and abs(value) > 1000000:
                            value = f"${value/1000000:.1f}M"
                        elif isinstance(value, (int, float)):
                            value = f"${value:,.0f}"
                        metrics.append(f"{key}: {value}")
                
                if metrics:
                    logger.info(f"   - Metrics: {', '.join(metrics[:3])}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to load {ticker}: {e}")
        return False

def main():
    """Main function to load all companies"""
    
    logger.info("🚀 Starting company data loading process")
    logger.info(f"Loading {len(COMPANIES)} companies with maximum historical data...")
    logger.info(f"Companies: {', '.join(COMPANIES)}")
    
    # Get database session
    db = get_database_session()
    
    try:
        # Initialize financial data service
        financial_service = FinancialDataService(db)
        
        successful_loads = []
        failed_loads = []
        
        # Load each company
        for ticker in COMPANIES:
            if load_company_data(ticker, db, financial_service):
                successful_loads.append(ticker)
            else:
                failed_loads.append(ticker)
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("📊 LOADING COMPLETE")
        logger.info(f"✅ Successfully loaded: {len(successful_loads)} companies")
        if successful_loads:
            logger.info(f"   {', '.join(successful_loads)}")
        
        if failed_loads:
            logger.info(f"❌ Failed to load: {len(failed_loads)} companies")
            logger.info(f"   {', '.join(failed_loads)}")
        
        # Database statistics
        total_companies = db.query(Company).count()
        total_price_records = db.query(PriceData).count()
        
        logger.info(f"\n📈 Database Statistics:")
        logger.info(f"   Total companies: {total_companies}")
        logger.info(f"   Total price records: {total_price_records}")
        
        # Show date range for loaded data
        if total_price_records > 0:
            from sqlalchemy import func
            date_range = db.query(
                func.min(PriceData.date).label('earliest'),
                func.max(PriceData.date).label('latest')
            ).first()
            
            logger.info(f"   Date range: {date_range.earliest} to {date_range.latest}")
        
        # Show some sample companies
        logger.info(f"\n🏢 Loaded Companies:")
        companies = db.query(Company).limit(10).all()
        for company in companies:
            price_count = db.query(PriceData).filter(PriceData.company_id == company.id).count()
            logger.info(f"   {company.ticker}: {company.name} ({price_count} price records)")
        
        logger.info("\n🎯 Ready for frontend visualization!")
        logger.info("You can now:")
        logger.info("1. Start the backend: python backend/main.py or uvicorn backend.main:app --reload")
        logger.info("2. Use the API endpoints at /api/companies/")
        logger.info("3. Build the frontend to visualize the data")
        
    except Exception as e:
        logger.error(f"💥 Critical error: {e}", exc_info=True)
    
    finally:
        db.close()

if __name__ == "__main__":
    main()