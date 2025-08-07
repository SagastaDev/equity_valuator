#!/usr/bin/env python3
"""
Script to create field mappings for DataStream Financial provider to canonical fields.
This simulates mapping for a provider with hierarchical data structure.

Usage: python DummyProviders/init_mappings_datastream.py [DATABASE_URL]
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

def create_datastream_mappings(database_url: str):
    """Create field mappings for DataStream Financial provider"""
    
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as db:
        # Get DataStream Financial provider
        provider = db.query(Provider).filter(
            Provider.name == "DataStream Financial (Test)"
        ).first()
        
        if not provider:
            print("ERROR: DataStream Financial provider not found. Run init_dummy_provider04.py first.")
            return
            
        print(f"Creating mappings for provider: {provider.name} (ID: {provider.id})")
        
        # Define mappings from DataStream raw fields to canonical fields
        # ~65% coverage with detailed field names
        field_mappings = {
            # Income Statement mappings (from "income" section)
            "sales_net": "total_revenue",
            "sales_total": "total_revenue",
            "cost_goods_sold": "cost_of_revenue",
            "margin_gross": "gross_profit",
            "expenses_admin": "selling_general_administrative",
            "expenses_sales": "selling_general_administrative",
            "profit_operating": "operating_income", 
            "charges_interest": "interest_expense",
            "earnings_pretax": "income_before_tax",
            "taxes_income": "income_tax_expense",
            "earnings_net": "net_income",
            "earnings_per_share": "basic_earnings_per_share",
            
            # Balance Sheet mappings (from "balance" section)
            "cash_cash_equiv": "cash_and_cash_equivalents",
            "receivables_trade": "accounts_receivable",
            "stock_inventory": "inventory", 
            "assets_current_total": "total_current_assets",
            "equipment_net": "property_plant_equipment_net",
            "goodwill_intangibles": "goodwill",
            "assets_grand_total": "total_assets",
            "payables_trade": "accounts_payable",
            "debt_short_term": "current_portion_of_long_term_debt",
            "liabilities_current_total": "total_current_liabilities",
            "debt_long_term": "long_term_debt",
            "liabilities_grand_total": "total_liabilities",
            "capital_stock": "common_stock",
            "surplus_capital": "additional_paid_in_capital",
            "earnings_accumulated": "retained_earnings",
            "equity_stockholders": "total_stockholders_equity",
            
            # Cash Flow mappings (from "flows" section)
            "cash_operations": "total_cash_from_operating_activities",
            "cash_investments": "total_cashflows_from_investing_activities",
            "cash_financing": "total_cash_from_financing_activities",
            "investments_capital": "capital_expenditures",
            "writeoffs_depreciation": "depreciation",
            "flow_free_cash": "free_cash_flow",
            
            # Market data
            "price_per_share": "close_price",
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
    
    print("Creating field mappings for DataStream Financial provider...")
    print(f"Database URL: {database_url}")
    print("-" * 60)
    
    try:
        provider_id = create_datastream_mappings(database_url)
        print("-" * 60)
        print("SUCCESS: DataStream Financial field mappings created successfully!")
        print("\nWARNING: These are test mappings - remove before production deployment")
        
    except Exception as e:
        print(f"ERROR: Failed to create mappings: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()