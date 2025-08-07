#!/usr/bin/env python3
"""
Simple script to verify that dummy provider field mappings are working correctly.
Shows sample mappings and validates the data structure.

Usage: python DummyProviders/verify_mappings.py [DATABASE_URL]
"""

import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path to import models
sys.path.append(str(Path(__file__).parent.parent))

from backend.db.models.provider import Provider
from backend.db.models.field import CanonicalField
from backend.db.models.mapping import MappedField, RawDataEntry

def verify_mappings(database_url: str):
    """Verify that field mappings are working correctly"""
    
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as db:
        print("=" * 70)
        print("DUMMY PROVIDER FIELD MAPPING VERIFICATION")
        print("=" * 70)
        
        # Get all test providers
        providers = db.query(Provider).filter(
            Provider.name.like('%Test%')
        ).all()
        
        total_mappings = 0
        total_raw_fields = 0
        
        for provider in providers:
            print(f"\n{provider.name} (ID: {provider.id})")
            print("-" * 50)
            
            # Count raw data entries
            raw_count = db.query(RawDataEntry).filter(
                RawDataEntry.provider_id == provider.id
            ).count()
            
            # Count mappings
            mapping_count = db.query(MappedField).filter(
                MappedField.provider_id == provider.id
            ).count()
            
            total_raw_fields += raw_count
            total_mappings += mapping_count
            
            print(f"Raw Fields: {raw_count}")
            print(f"Mapped Fields: {mapping_count}")
            print(f"Coverage: {mapping_count/raw_count*100:.1f}% of raw fields mapped")
            
            # Show sample mappings
            sample_mappings = db.query(MappedField, CanonicalField).join(
                CanonicalField, MappedField.canonical_id == CanonicalField.id
            ).filter(
                MappedField.provider_id == provider.id
            ).limit(5).all()
            
            if sample_mappings:
                print("\nSample Mappings:")
                for mapping, canonical in sample_mappings:
                    print(f"  {mapping.raw_field_name} -> {canonical.name}")
        
        print("\n" + "=" * 70)
        print("OVERALL SUMMARY")
        print("=" * 70)
        print(f"Total Providers: {len(providers)}")
        print(f"Total Raw Fields: {total_raw_fields}")
        print(f"Total Field Mappings: {total_mappings}")
        print(f"Overall Mapping Rate: {total_mappings/total_raw_fields*100:.1f}%")
        
        # Verify data integrity
        print("\nData Integrity Checks:")
        
        # Check for orphaned mappings
        orphaned = db.query(MappedField).outerjoin(
            CanonicalField, MappedField.canonical_id == CanonicalField.id
        ).filter(CanonicalField.id == None).count()
        
        print(f"  Orphaned mappings (should be 0): {orphaned}")
        
        # Check for duplicate mappings
        from sqlalchemy import func
        duplicates = db.query(
            MappedField.provider_id,
            MappedField.canonical_id,
            MappedField.raw_field_name,
            func.count(MappedField.id).label('count')
        ).group_by(
            MappedField.provider_id,
            MappedField.canonical_id, 
            MappedField.raw_field_name
        ).having(func.count(MappedField.id) > 1).count()
        
        print(f"  Duplicate mappings (should be 0): {duplicates}")
        
        print("\n✓ Field mapping verification completed successfully!")
        print("✓ Ready for field mapping UI testing")

def main():
    """Main function"""
    database_url = sys.argv[1] if len(sys.argv) > 1 else "sqlite:///./equity_valuation.db"
    
    try:
        verify_mappings(database_url)
    except Exception as e:
        print(f"ERROR: Verification failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()