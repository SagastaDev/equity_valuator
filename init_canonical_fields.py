#!/usr/bin/env python3
"""
Script to initialize canonical fields from JSON file into the database.
Run this script to populate the canonical_fields table with all financial statement items.
"""

import json
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.db.models.field import CanonicalField, FieldCategory
from backend.db.base import Base

def load_canonical_fields_from_json(json_file_path: str) -> list:
    """Load canonical fields from JSON file."""
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    
    all_fields = []
    for section in data['canonical_fields']:
        if 'fields' in section:
            all_fields.extend(section['fields'])
    
    return all_fields

def create_canonical_field_from_dict(field_data: dict) -> CanonicalField:
    """Create a CanonicalField object from dictionary data."""
    
    # Map category string to enum
    category_map = {
        'fundamental': FieldCategory.FUNDAMENTAL,
        'market': FieldCategory.MARKET,
        'ratio': FieldCategory.RATIO
    }
    
    return CanonicalField(
        code=field_data['code'],
        name=field_data['name'],
        display_name=field_data['display_name'],
        type=field_data['type'],
        category=category_map[field_data['category']],
        is_computed=field_data['is_computed']
    )

def main():
    """Main function to initialize canonical fields."""
    
    # Database setup
    database_url = "sqlite:///./equity_valuation.db"  # Default for development
    if len(sys.argv) > 1:
        database_url = sys.argv[1]
    
    print(f"Connecting to database: {database_url}")
    engine = create_engine(database_url)
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Load fields from JSON
        json_file_path = Path(__file__).parent / "canonical_fields.json"
        print(f"Loading canonical fields from: {json_file_path}")
        
        fields_data = load_canonical_fields_from_json(json_file_path)
        print(f"Found {len(fields_data)} canonical fields to process")
        
        # Clear existing fields (optional - comment out if you want to preserve existing data)
        existing_count = db.query(CanonicalField).count()
        if existing_count > 0:
            print(f"Found {existing_count} existing canonical fields")
            response = input("Do you want to clear existing fields and reload? (y/N): ")
            if response.lower() == 'y':
                db.query(CanonicalField).delete()
                db.commit()
                print("Cleared existing canonical fields")
        
        # Insert new fields
        inserted_count = 0
        skipped_count = 0
        
        for field_data in fields_data:
            try:
                # Check if field already exists
                existing_field = db.query(CanonicalField).filter(
                    CanonicalField.code == field_data['code']
                ).first()
                
                if existing_field:
                    print(f"Skipping existing field: {field_data['name']} (code: {field_data['code']})")
                    skipped_count += 1
                    continue
                
                # Create new field
                canonical_field = create_canonical_field_from_dict(field_data)
                db.add(canonical_field)
                inserted_count += 1
                
                print(f"Added: {canonical_field.name} ({canonical_field.category.value})")
                
            except Exception as e:
                print(f"Error processing field {field_data.get('name', 'unknown')}: {e}")
                continue
        
        # Commit all changes
        db.commit()
        
        print(f"\n[SUCCESS] Successfully processed canonical fields:")
        print(f"   - Inserted: {inserted_count}")
        print(f"   - Skipped: {skipped_count}")
        print(f"   - Total in database: {db.query(CanonicalField).count()}")
        
        # Show summary by category
        print(f"\n[SUMMARY] Fields by category:")
        for category in FieldCategory:
            count = db.query(CanonicalField).filter(CanonicalField.category == category).count()
            computed_count = db.query(CanonicalField).filter(
                CanonicalField.category == category,
                CanonicalField.is_computed == True
            ).count()
            raw_count = count - computed_count
            print(f"   - {category.value}: {count} total ({raw_count} raw, {computed_count} computed)")
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        db.rollback()
        return 1
    
    finally:
        db.close()
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)