"""
Development-only dummy data initialization module.
This module initializes test providers and field mappings for development purposes.
It should be disabled in production environments.
"""

import json
import os
from pathlib import Path
from sqlalchemy.orm import Session
from backend.db.models.provider import Provider
from backend.db.models.company import Company, Industry
from backend.db.models.mapping import RawDataEntry, MappedField, ValueType, PeriodType
from backend.db.models.field import CanonicalField
from backend.db.models.user import User, UserRole
from backend.auth.utils import get_password_hash
from datetime import date


def _load_json_data(filename: str) -> dict:
    """Load JSON data from DummyProviders directory."""
    json_path = Path(__file__).parent.parent.parent / "DummyProviders" / filename
    if not json_path.exists():
        raise FileNotFoundError(f"Dummy data file not found: {json_path}")
    
    with open(json_path, 'r') as f:
        return json.load(f)


def _create_test_provider(db: Session, name: str) -> int:
    """Create a test provider if it doesn't exist."""
    existing_provider = db.query(Provider).filter(Provider.name == name).first()
    if existing_provider:
        return existing_provider.id
    
    provider = Provider(name=name)
    db.add(provider)
    db.flush()
    print(f"Created test provider: {name}")
    return provider.id


def _create_test_company(db: Session, ticker: str, name: str, industry_code: str) -> int:
    """Create a test company if it doesn't exist."""
    existing_company = db.query(Company).filter(Company.ticker == ticker).first()
    if existing_company:
        return existing_company.id
    
    # Get industry
    industry = db.query(Industry).filter(Industry.code == industry_code).first()
    if not industry:
        raise ValueError(f"Industry {industry_code} not found")
    
    company = Company(
        ticker=ticker,
        name=name,
        country="US",
        currency="USD",
        industry_id=industry.id
    )
    db.add(company)
    db.flush()
    print(f"Created test company: {ticker} ({name})")
    return company.id


def _create_raw_data_entries(db: Session, provider_id: int, company_id: int, data: dict):
    """Create raw data entries from JSON data."""
    fiscal_period = date(2023, 12, 31)  # Q4 2023
    period_type = PeriodType.QUARTERLY
    
    def process_data(data_dict, prefix=""):
        for key, value in data_dict.items():
            if isinstance(value, dict):
                # Handle nested data (like MarketInsight and DataStream)
                new_prefix = f"{prefix}_{key}" if prefix else key
                process_data(value, new_prefix)
            elif isinstance(value, (int, float, str)) and value != "":
                field_name = f"{prefix}_{key}" if prefix else key
                
                # Check if entry already exists
                existing_entry = db.query(RawDataEntry).filter(
                    RawDataEntry.provider_id == provider_id,
                    RawDataEntry.company_id == company_id,
                    RawDataEntry.raw_field_name == field_name,
                    RawDataEntry.fiscal_period == fiscal_period
                ).first()
                
                if not existing_entry:
                    # Determine value type
                    if isinstance(value, (int, float)):
                        value_type = ValueType.NUMBER
                        json_value = float(value)
                    else:
                        value_type = ValueType.STRING
                        json_value = str(value)
                    
                    entry = RawDataEntry(
                        provider_id=provider_id,
                        company_id=company_id,
                        raw_field_name=field_name,
                        value_type=value_type,
                        value=json_value,
                        fiscal_period=fiscal_period,
                        period_type=period_type
                    )
                    db.add(entry)
    
    process_data(data)


def _create_field_mappings(db: Session, provider_id: int, mappings: dict):
    """Create field mappings from provider fields to canonical fields."""
    for provider_field, canonical_field_name in mappings.items():
        # Get canonical field
        canonical_field = db.query(CanonicalField).filter(
            CanonicalField.name == canonical_field_name
        ).first()
        
        if not canonical_field:
            print(f"Warning: Canonical field '{canonical_field_name}' not found, skipping mapping for '{provider_field}'")
            continue
        
        # Check if mapping already exists
        existing_mapping = db.query(MappedField).filter(
            MappedField.provider_id == provider_id,
            MappedField.raw_field_name == provider_field
        ).first()
        
        if not existing_mapping:
            mapping = MappedField(
                provider_id=provider_id,
                raw_field_name=provider_field,
                canonical_id=canonical_field.id
            )
            db.add(mapping)


def init_finstack_provider(db: Session) -> int:
    """Initialize FinStack Global test provider (mappings only, no fake companies)."""
    provider_id = _create_test_provider(db, "FinStack Global (Test)")
    
    # Note: Provider created without fake companies - use real companies from Kaggle data
    # Field mappings will be added when real company data is processed
    
    return provider_id


def init_alphafin_provider(db: Session) -> int:
    """Initialize AlphaFinance Pro test provider (mappings only, no fake companies)."""
    provider_id = _create_test_provider(db, "AlphaFinance Pro (Test)")
    
    # Create field mappings for AlphaFinance Pro (keep mappings for real data processing)
    mappings = {
        "revenues": "total_revenue",
        "cogs": "cost_of_revenue",
        "gross_margin": "gross_profit",
        "net_earnings": "net_income",
        "ebitda": "ebitda",
        "cash_and_equivalents": "cash",
        "current_assets_total": "total_current_assets",
        "shareholders_equity": "total_stockholder_equity",
        "operating_cash_flow": "total_cash_from_operating_activities",
        "capex": "capital_expenditures",
        "free_cash_flow": "free_cash_flow",
        "shares_outstanding": "shares_outstanding",
        "market_cap": "market_cap",
        "enterprise_value": "enterprise_value"
    }
    _create_field_mappings(db, provider_id, mappings)
    
    return provider_id


def init_marketinsight_provider(db: Session) -> int:
    """Initialize MarketInsight Analytics test provider (mappings only, no fake companies)."""
    provider_id = _create_test_provider(db, "MarketInsight Analytics (Test)")
    
    # Create field mappings for MarketInsight Analytics (nested structure)
    mappings = {
        "financials_revenue_total": "total_revenue",
        "financials_cost_sales": "cost_of_revenue",
        "financials_income_operating": "operating_income",
        "financials_income_net": "net_income",
        "position_cash_total": "cash",
        "position_assets_current": "total_current_assets",
        "position_equity_total": "total_stockholder_equity",
        "cashflow_cf_operating": "total_cash_from_operating_activities",
        "cashflow_expenditures_capital": "capital_expenditures",
        "market_shares_outstanding": "shares_outstanding",
        "market_market_cap": "market_cap"
    }
    _create_field_mappings(db, provider_id, mappings)
    
    return provider_id


def init_datastream_provider(db: Session) -> int:
    """Initialize DataStream Financial test provider (mappings only, no fake companies)."""
    provider_id = _create_test_provider(db, "DataStream Financial (Test)")
    
    # Create field mappings for DataStream Financial (hierarchical structure)
    mappings = {
        "statements_income_sales_net": "total_revenue",
        "statements_income_cost_goods_sold": "cost_of_revenue",
        "statements_income_profit_operating": "operating_income",
        "statements_income_earnings_net": "net_income",
        "statements_balance_cash_cash_equiv": "cash",
        "statements_balance_assets_current": "total_current_assets",
        "statements_balance_equity_shareholders": "total_stockholder_equity",
        "statements_flows_cash_operations": "total_cash_from_operating_activities",
        "statements_flows_investments_capital": "capital_expenditures",
        "statements_flows_flow_free_cash": "free_cash_flow",
        "market_data_shares_outstanding": "shares_outstanding",
        "market_data_market_capitalization": "market_cap"
    }
    _create_field_mappings(db, provider_id, mappings)
    
    return provider_id


def init_test_users(db: Session) -> None:
    """Initialize test users for development purposes."""
    test_users = [
        {
            "email": "admin@test.com",
            "password": "admin123",
            "role": UserRole.ADMIN,
            "description": "Test admin user"
        },
        {
            "email": "viewer@test.com", 
            "password": "viewer123",
            "role": UserRole.VIEWER,
            "description": "Test viewer user"
        },
        {
            "email": "john.admin@company.com",
            "password": "secure123",
            "role": UserRole.ADMIN,
            "description": "John Smith - Admin"
        },
        {
            "email": "jane.analyst@company.com",
            "password": "analyst123",
            "role": UserRole.VIEWER,
            "description": "Jane Doe - Financial Analyst"
        },
        {
            "email": "demo@equity.com",
            "password": "demo123",
            "role": UserRole.VIEWER,
            "description": "Demo user for presentations"
        }
    ]
    
    created_count = 0
    skipped_count = 0
    
    for user_data in test_users:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        
        if existing_user:
            print(f"User {user_data['email']} already exists, skipping...")
            skipped_count += 1
            continue
        
        # Create new user
        hashed_password = get_password_hash(user_data["password"])
        db_user = User(
            email=user_data["email"],
            hashed_password=hashed_password,
            role=user_data["role"]
        )
        
        db.add(db_user)
        print(f"Created {user_data['role'].value} user: {user_data['email']} ({user_data['description']})")
        created_count += 1
    
    if created_count > 0:
        print(f"✅ Test users initialization complete!")
        print(f"   • Created: {created_count} users")
        print(f"   • Skipped: {skipped_count} existing users")
        print(f"📝 Test User Credentials:")
        print(f"   Admin users: admin@test.com/admin123, john.admin@company.com/secure123")
        print(f"   Viewer users: viewer@test.com/viewer123, jane.analyst@company.com/analyst123, demo@equity.com/demo123")
        print(f"🔐 Change these passwords in production!")
    elif skipped_count > 0:
        print(f"All {skipped_count} test users already exist")


def initialize_dummy_data(db: Session, enable_dummy_data: bool = True) -> None:
    """
    Initialize all dummy data for development purposes.
    
    Args:
        db: Database session
        enable_dummy_data: Whether to initialize dummy data (should be False in production)
    """
    if not enable_dummy_data:
        print("Dummy data initialization disabled (production mode)")
        return
    
    # Check if DummyProviders directory exists
    dummy_dir = Path(__file__).parent.parent.parent / "DummyProviders"
    if not dummy_dir.exists():
        print("DummyProviders directory not found - skipping dummy data initialization")
        return
    
    print("Initializing dummy data for development...")
    
    try:
        # Initialize test users
        init_test_users(db)
        
        providers = []
        
        # Initialize all test providers
        provider_id = init_finstack_provider(db)
        providers.append(("FinStack Global (Test)", provider_id))
        
        provider_id = init_alphafin_provider(db)
        providers.append(("AlphaFinance Pro (Test)", provider_id))
        
        provider_id = init_marketinsight_provider(db)
        providers.append(("MarketInsight Analytics (Test)", provider_id))
        
        provider_id = init_datastream_provider(db)
        providers.append(("DataStream Financial (Test)", provider_id))
        
        db.commit()
        
        print(f"Successfully initialized {len(providers)} test providers:")
        for name, provider_id in providers:
            print(f"  - {name} (ID: {provider_id})")
        
        print("NOTE: Providers created with field mappings only - no fake companies")
        print("Use real companies from Kaggle data (AAPL, MSFT, GOOGL, NVDA, LMT)")
        print("WARNING: Remove dummy providers before production deployment")
        
    except Exception as e:
        print(f"Error initializing dummy data: {e}")
        db.rollback()
        raise