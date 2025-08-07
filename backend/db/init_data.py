"""
Database initialization module for populating initial data.
This module contains functions to populate initial data for providers and industries.
"""

from sqlalchemy.orm import Session
from backend.db.models.provider import Provider
from backend.db.models.company import Industry


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


def initialize_database(db: Session) -> None:
    """Initialize all initial data."""
    print("Initializing database with default data...")
    
    try:
        init_providers(db)
        init_industries(db)
        db.commit()
        print("Database initialization completed successfully")
    except Exception as e:
        print(f"Error during database initialization: {e}")
        db.rollback()
        raise