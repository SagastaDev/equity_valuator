"""
Sample Price Data Initialization Module

This module automatically loads sample price data from CSV files during development.
It's separate from the main dummy data initialization to keep concerns separated.
The sample data includes real historical price data for major companies from Kaggle.
"""

import os
import csv
import logging
from pathlib import Path
from datetime import datetime, date
from sqlalchemy.orm import Session
from backend.db.models.company import Company, Industry
from backend.db.models.price import PriceData
from backend.db.models.provider import Provider

logger = logging.getLogger(__name__)

# Sample companies and their details
SAMPLE_COMPANIES = {
    "AAPL": {"name": "Apple Inc.", "industry": "TECH", "country": "US", "currency": "USD"},
    "MSFT": {"name": "Microsoft Corporation", "industry": "TECH", "country": "US", "currency": "USD"},
    "GOOGL": {"name": "Alphabet Inc.", "industry": "TECH", "country": "US", "currency": "USD"},
    "NVDA": {"name": "NVIDIA Corporation", "industry": "TECH", "country": "US", "currency": "USD"},
    "LMT": {"name": "Lockheed Martin Corporation", "industry": "INDUSTRIAL", "country": "US", "currency": "USD"},
}


def _get_sample_data_provider(db: Session) -> Provider:
    """Get or create the sample data provider."""
    provider = db.query(Provider).filter(Provider.name == "Sample Data (Kaggle)").first()
    if not provider:
        provider = Provider(name="Sample Data (Kaggle)")
        db.add(provider)
        db.flush()
        logger.info("Created Sample Data provider")
    return provider


def _create_sample_company(db: Session, ticker: str, details: dict) -> Company:
    """Create or get a sample company."""
    existing_company = db.query(Company).filter(Company.ticker == ticker).first()
    if existing_company:
        return existing_company
    
    # Get industry
    industry = db.query(Industry).filter(Industry.code == details["industry"]).first()
    if not industry:
        # Fallback to TECH if industry not found
        industry = db.query(Industry).filter(Industry.code == "TECH").first()
    
    company = Company(
        ticker=ticker,
        name=details["name"],
        country=details["country"],
        currency=details["currency"],
        industry_id=industry.id if industry else None
    )
    
    db.add(company)
    db.flush()
    logger.info(f"Created sample company: {ticker} ({details['name']})")
    return company


def _load_price_data_from_csv(db: Session, company: Company, provider: Provider, csv_path: Path) -> int:
    """Load price data from a CSV file."""
    if not csv_path.exists():
        logger.warning(f"CSV file not found: {csv_path}")
        return 0
    
    # Check if we already have data for this company from this provider
    existing_count = db.query(PriceData).filter(
        PriceData.company_id == company.id,
        PriceData.provider_id == provider.id
    ).count()
    
    if existing_count > 0:
        logger.info(f"Price data already exists for {company.ticker} ({existing_count} records)")
        return existing_count
    
    records_loaded = 0
    
    try:
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            price_data_batch = []
            
            for row in reader:
                try:
                    # Parse date
                    price_date = datetime.strptime(row['Date'], '%Y-%m-%d').date()
                    
                    # Create price data record (only using fields that exist in the model)
                    price_data = PriceData(
                        company_id=company.id,
                        provider_id=provider.id,
                        date=price_date,
                        open=float(row['Open']) if row['Open'] else None,
                        close=float(row['Close']) if row['Close'] else None,
                        adj_close=float(row['Adj Close']) if row['Adj Close'] else None,
                        volume=int(row['Volume']) if row['Volume'] else None
                    )
                    
                    price_data_batch.append(price_data)
                    records_loaded += 1
                    
                    # Batch insert every 100 records for performance
                    if len(price_data_batch) >= 100:
                        db.add_all(price_data_batch)
                        db.flush()
                        price_data_batch = []
                
                except (ValueError, KeyError) as e:
                    logger.warning(f"Skipping invalid row in {csv_path}: {e}")
                    continue
            
            # Insert remaining records
            if price_data_batch:
                db.add_all(price_data_batch)
                db.flush()
        
        logger.info(f"Loaded {records_loaded} price records for {company.ticker}")
        
    except Exception as e:
        logger.error(f"Error loading price data from {csv_path}: {e}")
        return 0
    
    return records_loaded


def initialize_sample_price_data(db: Session, enable_sample_data: bool = True) -> None:
    """
    Initialize sample price data from CSV files.
    
    Args:
        db: Database session
        enable_sample_data: Whether to load sample price data (should be False in production)
    """
    if not enable_sample_data:
        logger.info("Sample price data initialization disabled (production mode)")
        return
    
    # Check if sample data directory exists
    sample_data_dir = Path(__file__).parent.parent.parent / "data" / "kaggle" / "sample"
    if not sample_data_dir.exists():
        logger.warning(f"Sample data directory not found: {sample_data_dir}")
        return
    
    logger.info("Initializing sample price data for development...")
    
    try:
        # Get or create sample data provider
        provider = _get_sample_data_provider(db)
        
        total_companies = 0
        total_records = 0
        successful_companies = []
        failed_companies = []
        
        # Load data for each sample company
        for ticker, details in SAMPLE_COMPANIES.items():
            try:
                # Create or get company
                company = _create_sample_company(db, ticker, details)
                
                # Load price data from CSV
                csv_file = sample_data_dir / f"{ticker}.csv"
                records_loaded = _load_price_data_from_csv(db, company, provider, csv_file)
                
                if records_loaded > 0:
                    successful_companies.append(ticker)
                    total_records += records_loaded
                    total_companies += 1
                else:
                    failed_companies.append(ticker)
                
            except Exception as e:
                logger.error(f"Failed to load sample data for {ticker}: {e}")
                failed_companies.append(ticker)
        
        # Commit all changes
        db.commit()
        
        # Summary
        logger.info(f"✅ Sample price data initialization complete!")
        logger.info(f"   • Companies loaded: {total_companies}")
        logger.info(f"   • Total price records: {total_records:,}")
        
        if successful_companies:
            logger.info(f"   • Successful: {', '.join(successful_companies)}")
        
        if failed_companies:
            logger.info(f"   • Failed: {', '.join(failed_companies)}")
        
        # Get date range for loaded data
        if total_records > 0:
            from sqlalchemy import func
            date_range = db.query(
                func.min(PriceData.date).label('earliest'),
                func.max(PriceData.date).label('latest')
            ).join(Provider).filter(Provider.name == "Sample Data (Kaggle)").first()
            
            if date_range and date_range.earliest and date_range.latest:
                logger.info(f"   • Date range: {date_range.earliest} to {date_range.latest}")
        
        logger.info("📊 Sample companies are now ready for price chart visualization!")
        logger.info("⚠️  Note: This is sample data for development/testing only")
        
    except Exception as e:
        logger.error(f"Error initializing sample price data: {e}")
        db.rollback()
        raise