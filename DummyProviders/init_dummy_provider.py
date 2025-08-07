#!/usr/bin/env python3
"""
Script to initialize dummy data providers for testing field mapping functionality.
This script can be safely removed once real providers are configured.

Usage: python DummyProviders/init_dummy_provider.py [DATABASE_URL]
"""

import json
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Add backend to path to import models
sys.path.append(str(Path(__file__).parent.parent))

from backend.db.models.provider import Provider
from backend.db.models.company import Company, Industry
from backend.db.models.mapping import RawDataEntry, ValueType, PeriodType
from backend.db.base import Base
from datetime import datetime, date

def load_mockup_data():
    """Load the MockupData01.json file"""
    mockup_file = Path(__file__).parent / "MockupData01.json"
    with open(mockup_file, 'r') as f:
        return json.load(f)

def init_dummy_provider(database_url: str):
    """Initialize dummy provider and sample data"""
    
    # Create database engine and session
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as db:
        # Load mockup data
        mockup = load_mockup_data()
        
        # Create dummy provider if it doesn't exist
        dummy_provider = db.query(Provider).filter(
            Provider.name == "FinStack Global (Test)"
        ).first()
        
        if not dummy_provider:
            dummy_provider = Provider(
                name="FinStack Global (Test)"
            )
            db.add(dummy_provider)
            db.commit()
            db.refresh(dummy_provider)
            print(f"Created dummy provider: {dummy_provider.name} (ID: {dummy_provider.id})")
        else:
            print(f"Dummy provider already exists: {dummy_provider.name} (ID: {dummy_provider.id})")
        
        # Create test industry if it doesn't exist
        tech_industry = db.query(Industry).filter(
            Industry.name == "Technology"
        ).first()
        
        if not tech_industry:
            tech_industry = Industry(
                name="Technology",
                description="Technology companies for testing"
            )
            db.add(tech_industry)
            db.commit()
            db.refresh(tech_industry)
            print(f"Created test industry: {tech_industry.name}")
        
        # Create test company based on mockup metadata
        test_company = db.query(Company).filter(
            Company.ticker == mockup["metadata"]["ticker_symbol"]
        ).first()
        
        if not test_company:
            test_company = Company(
                ticker=mockup["metadata"]["ticker_symbol"],
                name=mockup["metadata"]["entity_name"],
                industry_id=tech_industry.id,
                country=mockup["metadata"]["country"],
                currency=mockup["metadata"]["currency_used"]
            )
            db.add(test_company)
            db.commit()
            db.refresh(test_company)
            print(f"Created test company: {test_company.name} ({test_company.ticker})")
        else:
            print(f"Test company already exists: {test_company.name} ({test_company.ticker})")
        
        # Process each report and create raw data entries
        for report in mockup["reports"]:
            fiscal_date = date(report["fiscal_year"], report["fiscal_month"], 1)
            
            # Add all financial statement fields as raw data
            for statement_type, fields in [
                ("income_statement", report.get("income_statement", {})),
                ("balance_sheet", report.get("balance_sheet", {})),
                ("cash_flow_statement", report.get("cash_flow_statement", {}))
            ]:
                for field_name, value in fields.items():
                    # Check if raw data entry already exists
                    existing_entry = db.query(RawDataEntry).filter(
                        RawDataEntry.provider_id == dummy_provider.id,
                        RawDataEntry.company_id == test_company.id,
                        RawDataEntry.fiscal_period == fiscal_date,
                        RawDataEntry.raw_field_name == field_name
                    ).first()
                    
                    if not existing_entry:
                        raw_entry = RawDataEntry(
                            provider_id=dummy_provider.id,
                            company_id=test_company.id,
                            fiscal_period=fiscal_date,
                            period_type=PeriodType.ANNUAL,
                            raw_field_name=field_name,
                            value_type=ValueType.NUMBER,
                            value=value
                        )
                        db.add(raw_entry)
            
            # Add market data fields
            market_fields = {
                "avg_month_price": report.get("avg_month_price"),
                "shares_outstanding": mockup["metadata"]["shares_outstanding"]
            }
            
            for field_name, value in market_fields.items():
                if value is not None:
                    existing_entry = db.query(RawDataEntry).filter(
                        RawDataEntry.provider_id == dummy_provider.id,
                        RawDataEntry.company_id == test_company.id,
                        RawDataEntry.fiscal_period == fiscal_date,
                        RawDataEntry.raw_field_name == field_name
                    ).first()
                    
                    if not existing_entry:
                        raw_entry = RawDataEntry(
                            provider_id=dummy_provider.id,
                            company_id=test_company.id,
                            fiscal_period=fiscal_date,
                            period_type=PeriodType.ANNUAL,
                            raw_field_name=field_name,
                            value_type=ValueType.NUMBER,
                            value=value
                        )
                        db.add(raw_entry)
        
        # Commit all raw data entries
        db.commit()
        print("Successfully loaded dummy data into database")
        
        # Print summary of available raw fields
        raw_fields = db.query(RawDataEntry.raw_field_name).filter(
            RawDataEntry.provider_id == dummy_provider.id
        ).distinct().all()
        
        print(f"\nAvailable raw field names from {dummy_provider.name}:")
        for (field_name,) in sorted(raw_fields):
            print(f"  - {field_name}")
        
        return dummy_provider.id

def main():
    """Main function to run the dummy provider initialization"""
    database_url = sys.argv[1] if len(sys.argv) > 1 else "sqlite:///./equity_valuation.db"
    
    print(f"Initializing dummy provider data...")
    print(f"Database URL: {database_url}")
    print(f"Source data: {Path(__file__).parent / 'MockupData01.json'}")
    print("-" * 50)
    
    try:
        provider_id = init_dummy_provider(database_url)
        print("-" * 50)
        print("SUCCESS: Dummy provider initialization completed successfully!")
        print(f"Provider ID: {provider_id}")
        print("\nWARNING: This is test data - remove before production deployment")
        
    except Exception as e:
        print(f"ERROR: Error initializing dummy provider: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()