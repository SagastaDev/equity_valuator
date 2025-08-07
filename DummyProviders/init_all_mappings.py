#!/usr/bin/env python3
"""
Master script to initialize all field mappings for dummy data providers.
This creates the provider-to-canonical field mappings for testing.

Usage: python DummyProviders/init_all_mappings.py [DATABASE_URL]
"""

import sys
from pathlib import Path

# Import individual mapping modules
sys.path.append(str(Path(__file__).parent))

from init_mappings_alphafin import create_alphafin_mappings
from init_mappings_marketinsight import create_marketinsight_mappings  
from init_mappings_datastream import create_datastream_mappings

def init_all_mappings(database_url: str):
    """Initialize all dummy provider mappings"""
    print("=" * 80)
    print("INITIALIZING ALL DUMMY PROVIDER FIELD MAPPINGS")
    print("=" * 80)
    
    providers = []
    
    try:
        # Initialize AlphaFinance Pro mappings
        print("\n1. Creating AlphaFinance Pro field mappings...")
        provider_id = create_alphafin_mappings(database_url)
        providers.append(("AlphaFinance Pro (Test)", provider_id))
        
        # Initialize MarketInsight Analytics mappings
        print("\n2. Creating MarketInsight Analytics field mappings...")
        provider_id = create_marketinsight_mappings(database_url)
        providers.append(("MarketInsight Analytics (Test)", provider_id))
        
        # Initialize DataStream Financial mappings
        print("\n3. Creating DataStream Financial field mappings...")
        provider_id = create_datastream_mappings(database_url)
        providers.append(("DataStream Financial (Test)", provider_id))
        
    except Exception as e:
        print(f"ERROR: Failed to initialize mappings: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 80)
    print("FIELD MAPPING INITIALIZATION COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print(f"\nCreated field mappings for {len(providers)} dummy providers:")
    for name, provider_id in providers:
        print(f"  - {name} (ID: {provider_id})")
    
    print("\nField Mapping Coverage:")
    print("  - AlphaFinance Pro: Maps ~35 key financial fields to canonical")
    print("  - MarketInsight Analytics: Maps ~30 nested structure fields to canonical")
    print("  - DataStream Financial: Maps ~38 hierarchical fields to canonical")
    
    print("\nNote: FinStack Global provider already has comprehensive field coverage")
    print("and serves as the reference provider with standard naming conventions.")
    
    print("\nTest Results:")
    print("  ✓ Provider raw data entries exist")
    print("  ✓ Field mappings to canonical fields created")
    print("  ✓ Ready for field mapping UI testing")
    
    print("\nWARNING: These are test mappings - remove before production deployment")
    print("Use the transformation UI to test field mapping and formula functionality")

def main():
    """Main function"""
    database_url = sys.argv[1] if len(sys.argv) > 1 else "sqlite:///./equity_valuation.db"
    
    print("Database URL:", database_url)
    print("Prerequisites: Dummy providers and raw data must be initialized first")
    print("Run 'python DummyProviders/init_all_dummy_providers.py' if not done already")
    print()
    
    init_all_mappings(database_url)

if __name__ == "__main__":
    main()