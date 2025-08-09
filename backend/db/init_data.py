"""
Database initialization module for populating initial data.
This module contains functions to populate initial data for providers and industries.
"""

import os
import json
from pathlib import Path
from sqlalchemy.orm import Session
from backend.db.models.provider import Provider
from backend.db.models.company import Industry
from backend.db.models.field import CanonicalField, FieldCategory
from backend.db.init_dummy_data import initialize_dummy_data
from backend.db.init_sample_data import initialize_sample_price_data


def init_providers(db: Session) -> None:
    """Initialize default providers if they don't exist."""
    existing_provider = db.query(Provider).filter(Provider.name == "Yahoo Finance").first()
    if not existing_provider:
        provider = Provider(name="Yahoo Finance")
        db.add(provider)
        print("Added provider: Yahoo Finance")
    else:
        print("Provider 'Yahoo Finance' already exists")


def init_industries(db: Session) -> None:
    """Initialize default industries if they don't exist."""
    industries_data = [
        ('TECH', 'Technology', 'Technology companies'),
        ('FINANCE', 'Financial Services', 'Banks, insurance, and financial services'),
        ('HEALTHCARE', 'Healthcare', 'Healthcare and pharmaceutical companies'),
        ('ENERGY', 'Energy', 'Oil, gas, and renewable energy companies'),
        ('CONSUMER', 'Consumer Goods', 'Consumer products and retail'),
        ('INDUSTRIAL', 'Industrial', 'Manufacturing and industrial companies'),
        ('UTILITIES', 'Utilities', 'Electric, gas, and water utilities'),
        ('REAL_ESTATE', 'Real Estate', 'Real estate investment and development'),
        ('MATERIALS', 'Materials', 'Mining, chemicals, and raw materials'),
        ('TELECOM', 'Telecommunications', 'Telecommunications and media')
    ]
    
    added_count = 0
    for code, name, description in industries_data:
        existing_industry = db.query(Industry).filter(Industry.code == code).first()
        if not existing_industry:
            industry = Industry(code=code, name=name, description=description)
            db.add(industry)
            added_count += 1
            print(f"Added industry: {name} ({code})")
    
    if added_count == 0:
        print("All industries already exist")
    else:
        print(f"Added {added_count} new industries")


def init_canonical_fields(db: Session) -> None:
    """Initialize canonical fields from JSON file if they don't exist."""
    existing_count = db.query(CanonicalField).count()
    if existing_count > 0:
        print(f"Canonical fields already exist ({existing_count} fields)")
        return
    
    try:
        # Load canonical fields from JSON file
        json_file_path = Path(__file__).parent.parent.parent / "canonical_fields.json"
        
        if not json_file_path.exists():
            print(f"Warning: canonical_fields.json not found at {json_file_path}")
            return
            
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        
        # Extract all fields from sections
        all_fields = []
        for section in data['canonical_fields']:
            if 'fields' in section:
                all_fields.extend(section['fields'])
        
        # Map category strings to enums
        category_map = {
            'fundamental': FieldCategory.FUNDAMENTAL,
            'market': FieldCategory.MARKET,
            'ratio': FieldCategory.RATIO
        }
        
        # Insert fields
        inserted_count = 0
        for field_data in all_fields:
            try:
                canonical_field = CanonicalField(
                    code=field_data['code'],
                    name=field_data['name'],
                    display_name=field_data['display_name'],
                    type=field_data['type'],
                    category=category_map[field_data['category']],
                    is_computed=field_data['is_computed']
                )
                db.add(canonical_field)
                inserted_count += 1
                
            except Exception as e:
                print(f"Error processing field {field_data.get('name', 'unknown')}: {e}")
                continue
        
        print(f"Added {inserted_count} canonical fields")
        
    except Exception as e:
        print(f"Error initializing canonical fields: {e}")
        raise


def initialize_database(db: Session) -> None:
    """Initialize all initial data."""
    print("Initializing database with default data...")
    
    try:
        init_providers(db)
        init_industries(db)
        init_canonical_fields(db)
        
        # Initialize dummy data for development (disabled in production)
        enable_dummy = os.getenv("ENABLE_DUMMY_DATA", "true").lower() == "true"
        initialize_dummy_data(db, enable_dummy_data=enable_dummy)
        
        # Initialize sample price data for development (separate from dummy data)
        enable_sample_data = os.getenv("ENABLE_SAMPLE_DATA", "true").lower() == "true"
        initialize_sample_price_data(db, enable_sample_data=enable_sample_data)
        
        db.commit()
        print("Database initialization completed successfully")
    except Exception as e:
        print(f"Error during database initialization: {e}")
        db.rollback()
        raise