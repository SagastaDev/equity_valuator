#!/usr/bin/env python3
"""
Master script to initialize all dummy data providers for testing field mapping functionality.
This script can be safely removed once real providers are configured.

Usage: python DummyProviders/init_all_dummy_providers.py [DATABASE_URL]
"""

import sys
from pathlib import Path

# Import individual initialization modules
sys.path.append(str(Path(__file__).parent))

from init_dummy_provider import init_dummy_provider as init_finstack
from init_dummy_provider02 import init_dummy_provider as init_alphafin
from init_dummy_provider03 import init_dummy_provider as init_marketinsight
from init_dummy_provider04 import init_dummy_provider as init_datastream

def init_all_dummy_providers(database_url: str):
    """Initialize all dummy providers"""
    print("=" * 70)
    print("INITIALIZING ALL DUMMY DATA PROVIDERS")
    print("=" * 70)
    
    providers = []
    
    try:
        # Initialize FinStack Global provider
        print("\n1. Initializing FinStack Global (Test)...")
        provider_id = init_finstack(database_url)
        providers.append(("FinStack Global (Test)", provider_id))
        
        # Initialize AlphaFinance Pro provider
        print("\n2. Initializing AlphaFinance Pro (Test)...")
        provider_id = init_alphafin(database_url)
        providers.append(("AlphaFinance Pro (Test)", provider_id))
        
        # Initialize MarketInsight Analytics provider
        print("\n3. Initializing MarketInsight Analytics (Test)...")
        provider_id = init_marketinsight(database_url)
        providers.append(("MarketInsight Analytics (Test)", provider_id))
        
        # Initialize DataStream Financial provider
        print("\n4. Initializing DataStream Financial (Test)...")
        provider_id = init_datastream(database_url)
        providers.append(("DataStream Financial (Test)", provider_id))
        
    except Exception as e:
        print(f"ERROR: Failed to initialize providers: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("INITIALIZATION COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print(f"\nInitialized {len(providers)} dummy providers:")
    for name, provider_id in providers:
        print(f"  - {name} (ID: {provider_id})")
    
    print("\nTest companies created:")
    print("  - ACM: Acme Technologies Ltd. (FinStack Global)")
    print("  - TECH: TechCorp Industries Inc. (AlphaFinance Pro)")
    print("  - SOFT: SoftwareDev Solutions Ltd. (MarketInsight Analytics)")
    print("  - INNV: Innovation Dynamics Corp. (DataStream Financial)")
    
    print("\nField Mapping Coverage Summary:")
    print("  - FinStack Global: ~100% canonical field coverage (reference provider)")
    print("  - AlphaFinance Pro: ~60% canonical field coverage (different naming)")
    print("  - MarketInsight Analytics: ~55% canonical field coverage (nested structure)")
    print("  - DataStream Financial: ~65% canonical field coverage (alternative names)")
    
    print("\nWARNING: These are test providers - remove before production deployment")
    print("Use the field mapping UI to test provider-to-canonical field mappings")

def main():
    """Main function"""
    database_url = sys.argv[1] if len(sys.argv) > 1 else "sqlite:///./equity_valuation.db"
    
    print("Database URL:", database_url)
    init_all_dummy_providers(database_url)

if __name__ == "__main__":
    main()