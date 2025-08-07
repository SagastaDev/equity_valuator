#!/usr/bin/env python3
"""
Script to create field mappings for MarketInsight Analytics provider to canonical fields.
This simulates the mapping process for a provider with nested data structure.

Usage: python DummyProviders/init_mappings_marketinsight.py [DATABASE_URL]
"""

import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path to import models
sys.path.append(str(Path(__file__).parent.parent))

from backend.db.models.provider import Provider
from backend.db.models.field import CanonicalField
from backend.db.models.mapping import MappedField
from backend.db.base import Base

def create_marketinsight_mappings(database_url: str):
    """Create field mappings for MarketInsight Analytics provider"""
    
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as db:
        # Get MarketInsight Analytics provider
        provider = db.query(Provider).filter(
            Provider.name == "MarketInsight Analytics (Test)"
        ).first()
        
        if not provider:
            print("ERROR: MarketInsight Analytics provider not found. Run init_dummy_provider03.py first.")
            return
            
        print(f"Creating mappings for provider: {provider.name} (ID: {provider.id})")
        
        # Define mappings from MarketInsight raw fields to canonical fields
        # ~55% coverage with focus on key financial metrics
        field_mappings = {
            # Income Statement mappings (from "financials" section)
            "revenue_total": "total_revenue",
            "cost_sales": "cost_of_revenue",
            "profit_gross": "gross_profit",
            "expense_operating": "total_operating_expenses",
            "income_operating": "operating_income",
            "expense_interest": "interest_expense",
            "income_pretax": "income_before_tax",
            "provision_tax": "income_tax_expense",
            "income_net": "net_income",
            "shares_weighted_avg": "weighted_average_shares_outstanding",
            
            # Balance Sheet mappings (from "position" section)
            "cash_total": "cash_and_cash_equivalents",
            "receivables_net": "accounts_receivable", 
            "inventory_total": "inventory",
            "assets_current": "total_current_assets",
            "property_net": "property_plant_equipment_net",
            "assets_intangible": "intangible_assets",
            "assets_total": "total_assets",
            "payables_accounts": "accounts_payable",
            "debt_current": "current_portion_of_long_term_debt",
            "liabilities_current": "total_current_liabilities",
            "debt_longterm": "long_term_debt",
            "liabilities_total": "total_liabilities",
            "stock_common": "common_stock",
            "earnings_retained": "retained_earnings",
            "equity_total": "total_stockholders_equity",
            
            # Cash Flow mappings (from "cashflow" section)
            "cf_operating": "total_cash_from_operating_activities",
            "cf_investing": "total_cashflows_from_investing_activities",
            "cf_financing": "total_cash_from_financing_activities",
            "expenditures_capital": "capital_expenditures",
            "amortization_depreciation": "depreciation",
            
            # Market data
            "stock_price": "close_price",
            "shares_outstanding": "shares_outstanding"
        }
        
        mapped_count = 0
        skipped_count = 0
        
        for raw_field_name, canonical_name in field_mappings.items():
            # Find the canonical field
            canonical_field = db.query(CanonicalField).filter(
                CanonicalField.name == canonical_name
            ).first()
            
            if not canonical_field:
                print(f"WARNING: Canonical field '{canonical_name}' not found, skipping {raw_field_name}")
                skipped_count += 1
                continue
                
            # Check if mapping already exists
            existing_mapping = db.query(MappedField).filter(
                MappedField.provider_id == provider.id,
                MappedField.canonical_id == canonical_field.id,
                MappedField.raw_field_name == raw_field_name
            ).first()
            
            if existing_mapping:
                print(f"  Mapping already exists: {raw_field_name} -> {canonical_name}")
                continue
                
            # Create new mapping
            mapping = MappedField(
                provider_id=provider.id,
                canonical_id=canonical_field.id,
                raw_field_name=raw_field_name,
                company_id=None,  # Global mapping for all companies
                start_date=None,  # No date restrictions
                end_date=None,
                transform_expression=None  # Direct field mapping, no transformation
            )
            
            db.add(mapping)
            mapped_count += 1
            print(f"  Created mapping: {raw_field_name} -> {canonical_name}")
        
        # Commit all mappings
        db.commit()
        
        print(f"\nMapping Summary for {provider.name}:")
        print(f"  - Successfully mapped: {mapped_count} fields")
        print(f"  - Skipped (canonical not found): {skipped_count} fields") 
        print(f"  - Coverage: ~{mapped_count}% of canonical fields")
        
        return provider.id

def main():
    """Main function"""
    database_url = sys.argv[1] if len(sys.argv) > 1 else "sqlite:///./equity_valuation.db"
    
    print("Creating field mappings for MarketInsight Analytics provider...")
    print(f"Database URL: {database_url}")
    print("-" * 60)
    
    try:
        provider_id = create_marketinsight_mappings(database_url)
        print("-" * 60)
        print("SUCCESS: MarketInsight Analytics field mappings created successfully!")
        print("\nWARNING: These are test mappings - remove before production deployment")
        
    except Exception as e:
        print(f"ERROR: Failed to create mappings: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()