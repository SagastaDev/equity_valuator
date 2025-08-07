#!/usr/bin/env python3
"""
Script to create field mappings for AlphaFinance Pro provider to canonical fields.
This simulates the mapping process that would be done through the UI.

Usage: python DummyProviders/init_mappings_alphafin.py [DATABASE_URL]
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

def create_alphafin_mappings(database_url: str):
    """Create field mappings for AlphaFinance Pro provider"""
    
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as db:
        # Get AlphaFinance Pro provider
        provider = db.query(Provider).filter(
            Provider.name == "AlphaFinance Pro (Test)"
        ).first()
        
        if not provider:
            print("ERROR: AlphaFinance Pro provider not found. Run init_dummy_provider02.py first.")
            return
            
        print(f"Creating mappings for provider: {provider.name} (ID: {provider.id})")
        
        # Define mappings from AlphaFinance Pro raw fields to canonical fields
        # This represents ~60% coverage by mapping key financial statement items
        field_mappings = {
            # Income Statement mappings
            "revenues": "total_revenue",
            "total_revenues": "total_revenue", 
            "cogs": "cost_of_revenue",
            "gross_margin": "gross_profit",
            "sga_expenses": "selling_general_administrative",
            "operating_earnings": "operating_income",
            "ebitda": "ebitda",
            "interest_exp": "interest_expense",
            "pretax_income": "income_before_tax",
            "tax_expense": "income_tax_expense",
            "net_earnings": "net_income",
            "net_earnings_available": "net_income_common_stockholders",
            "diluted_eps": "diluted_earnings_per_share",
            "basic_eps": "basic_earnings_per_share",
            
            # Balance Sheet mappings  
            "cash_and_equivalents": "cash_and_cash_equivalents",
            "accounts_rec": "accounts_receivable",
            "inventories": "inventory",
            "current_assets_total": "total_current_assets",
            "ppe_net": "property_plant_equipment_net",
            "goodwill_net": "goodwill",
            "intangibles_net": "intangible_assets",
            "assets_total": "total_assets",
            "accounts_pay": "accounts_payable",
            "current_debt": "current_portion_of_long_term_debt",
            "current_liabilities_total": "total_current_liabilities",
            "long_term_debt_total": "long_term_debt",
            "liabilities_total": "total_liabilities",
            "common_shares": "common_stock",
            "retained_earnings_total": "retained_earnings",
            "shareholders_equity": "total_stockholders_equity",
            "tangible_book_value": "tangible_book_value",
            
            # Cash Flow mappings
            "operating_cash_flow": "total_cash_from_operating_activities",
            "investing_cash_flow": "total_cashflows_from_investing_activities", 
            "financing_cash_flow": "total_cash_from_financing_activities",
            "capex": "capital_expenditures",
            "depreciation_amortization": "depreciation",
            "free_cash_flow": "free_cash_flow",
            
            # Market data
            "market_price": "close_price",
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
    
    print("Creating field mappings for AlphaFinance Pro provider...")
    print(f"Database URL: {database_url}")
    print("-" * 60)
    
    try:
        provider_id = create_alphafin_mappings(database_url)
        print("-" * 60)
        print("SUCCESS: AlphaFinance Pro field mappings created successfully!")
        print("\nWARNING: These are test mappings - remove before production deployment")
        
    except Exception as e:
        print(f"ERROR: Failed to create mappings: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()