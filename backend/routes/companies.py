"""
Companies API Routes

This module provides REST API endpoints for managing companies and their price data.
Includes endpoints for:
- Company CRUD operations  
- Price data ingestion from multiple providers
- Historical price data retrieval for charts
- Company data summaries and statistics
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
import logging

from backend.db.session import get_db
from backend.db.models.company import Company
from backend.db.models.price import PriceData, PricePeriodType
from backend.data_providers import DataProviderFactory, DataProviderType
from backend.auth.routes import get_current_user
from backend.db.models.user import User
from pydantic import BaseModel, field_validator
from uuid import UUID

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/companies", tags=["companies"])

# Pydantic models for API requests/responses

class CompanyCreate(BaseModel):
    ticker: str
    name: str
    country: str = "Unknown"
    currency: str = "USD"
    industry_id: Optional[int] = None

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None
    currency: Optional[str] = None
    industry_id: Optional[int] = None

class CompanyResponse(BaseModel):
    id: str
    ticker: str
    name: str
    country: str
    currency: str
    industry_id: Optional[int]
    
    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v
    
    class Config:
        from_attributes = True

class PriceDataResponse(BaseModel):
    date: date
    open: Optional[float]
    close: Optional[float] 
    adj_close: Optional[float]
    volume: Optional[int]
    provider_name: str
    
    class Config:
        from_attributes = True

class CompanySummaryResponse(BaseModel):
    company: CompanyResponse
    price_data_summary: Dict[str, Any]
    latest_price: Optional[float]
    price_change_1d: Optional[float]
    price_change_1w: Optional[float]
    total_records: int

class DataIngestionRequest(BaseModel):
    tickers: List[str]
    provider_type: str = "kaggle"  # Default to kaggle for now
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
class DataIngestionResponse(BaseModel):
    successful_tickers: List[str]
    failed_tickers: List[Dict[str, str]]
    records_inserted: int
    date_range: Optional[Dict[str, str]]
    errors: List[str]

# Company Management Endpoints

@router.get("/", response_model=List[CompanyResponse])
async def list_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all companies with optional search and pagination"""
    
    query = db.query(Company)
    
    # Apply search filter
    if search:
        search_term = f"%{search.upper()}%"
        query = query.filter(
            (Company.ticker.ilike(search_term)) | 
            (Company.name.ilike(search_term))
        )
    
    # Apply pagination
    companies = query.order_by(Company.ticker).offset(skip).limit(limit).all()
    
    return companies

@router.post("/", response_model=CompanyResponse)
async def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new company"""
    
    # Check if company already exists
    existing = db.query(Company).filter(Company.ticker == company_data.ticker.upper()).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Company with ticker {company_data.ticker} already exists")
    
    # Create new company
    company = Company(
        ticker=company_data.ticker.upper(),
        name=company_data.name,
        country=company_data.country,
        currency=company_data.currency,
        industry_id=company_data.industry_id
    )
    
    db.add(company)
    db.commit()
    db.refresh(company)
    
    logger.info(f"Created company: {company.ticker}")
    return company

@router.get("/{company_id}", response_model=CompanySummaryResponse)
async def get_company(
    company_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed company information with price data summary"""
    
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Get price data summary
    price_summary = db.query(
        func.min(PriceData.date).label('earliest_date'),
        func.max(PriceData.date).label('latest_date'),
        func.count(PriceData.id).label('total_records')
    ).filter(PriceData.company_id == company.id).first()
    
    # Get latest prices for trend calculation
    latest_prices = db.query(PriceData).filter(
        PriceData.company_id == company.id
    ).order_by(desc(PriceData.date)).limit(10).all()
    
    latest_price = None
    price_change_1d = None
    price_change_1w = None
    
    if latest_prices:
        latest_price = latest_prices[0].close
        
        # Calculate 1-day change
        if len(latest_prices) > 1 and latest_prices[1].close:
            price_change_1d = ((latest_price - latest_prices[1].close) / latest_prices[1].close) * 100
        
        # Calculate 1-week change (approximate - find price ~7 days ago)
        week_ago_price = None
        for price in latest_prices:
            if (latest_prices[0].date - price.date).days >= 7:
                week_ago_price = price.close
                break
        
        if week_ago_price:
            price_change_1w = ((latest_price - week_ago_price) / week_ago_price) * 100
    
    return CompanySummaryResponse(
        company=CompanyResponse.model_validate(company),
        price_data_summary={
            "earliest_date": price_summary.earliest_date.isoformat() if price_summary.earliest_date else None,
            "latest_date": price_summary.latest_date.isoformat() if price_summary.latest_date else None,
        },
        latest_price=latest_price,
        price_change_1d=price_change_1d,
        price_change_1w=price_change_1w,
        total_records=price_summary.total_records or 0
    )

@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: str,
    company_data: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update company information"""
    
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Update fields
    update_data = company_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)
    
    db.commit()
    db.refresh(company)
    
    logger.info(f"Updated company: {company.ticker}")
    return company

# Price Data Endpoints

@router.get("/{company_id}/prices", response_model=List[PriceDataResponse])
async def get_company_prices(
    company_id: str,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(1000, ge=1, le=10000),
    provider: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get historical price data for a company"""
    
    # Verify company exists
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Build query
    query = db.query(PriceData).filter(PriceData.company_id == company_id)
    
    # Apply date filters
    if start_date:
        query = query.filter(PriceData.date >= start_date)
    if end_date:
        query = query.filter(PriceData.date <= end_date)
    
    # Apply provider filter
    if provider:
        from backend.db.models.provider import Provider
        provider_obj = db.query(Provider).filter(Provider.name.ilike(f"%{provider}%")).first()
        if provider_obj:
            query = query.filter(PriceData.provider_id == provider_obj.id)
    
    # Get results ordered by date (most recent first for charts)
    prices = query.order_by(desc(PriceData.date)).limit(limit).all()
    
    # Add provider name to response
    result = []
    for price in prices:
        price_dict = {
            'date': price.date,
            'open': price.open,
            'close': price.close,
            'adj_close': price.adj_close,
            'volume': price.volume,
            'provider_name': price.provider.name if price.provider else "Unknown"
        }
        result.append(PriceDataResponse.model_validate(price_dict))
    
    return result

@router.get("/ticker/{ticker}", response_model=CompanySummaryResponse)
async def get_company_by_ticker(
    ticker: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get company information by ticker symbol"""
    
    company = db.query(Company).filter(Company.ticker == ticker.upper()).first()
    if not company:
        raise HTTPException(status_code=404, detail=f"Company with ticker {ticker} not found")
    
    # Reuse the detailed company endpoint logic
    return await get_company(str(company.id), db, current_user)

@router.get("/ticker/{ticker}/prices", response_model=List[PriceDataResponse])
async def get_company_prices_by_ticker(
    ticker: str,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(1000, ge=1, le=10000),
    provider: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get historical price data for a company by ticker"""
    
    company = db.query(Company).filter(Company.ticker == ticker.upper()).first()
    if not company:
        raise HTTPException(status_code=404, detail=f"Company with ticker {ticker} not found")
    
    # Reuse the price endpoint logic
    return await get_company_prices(str(company.id), start_date, end_date, limit, provider, db, current_user)

# Data Ingestion Endpoints (Admin only)

@router.post("/ingest", response_model=DataIngestionResponse)
async def ingest_price_data(
    request: DataIngestionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ingest historical price data for multiple companies (Admin only)"""
    
    # Check admin permissions
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Map provider type string to enum
        provider_type_map = {
            "kaggle": DataProviderType.KAGGLE,
            "yahoo": DataProviderType.YAHOO_FINANCE,
        }
        
        provider_type = provider_type_map.get(request.provider_type.lower())
        if not provider_type:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported provider type: {request.provider_type}"
            )
        
        # Create provider instance
        provider = DataProviderFactory.create_provider(provider_type, db)
        
        # Test connection
        if not provider.test_connection():
            raise HTTPException(
                status_code=503, 
                detail=f"Cannot connect to {request.provider_type} data source"
            )
        
        # Start ingestion (run in background for large datasets)
        def run_ingestion():
            try:
                result = provider.ingest_historical_data(
                    request.tickers,
                    request.start_date,
                    request.end_date
                )
                logger.info(f"Ingestion completed: {result.records_inserted} records")
            except Exception as e:
                logger.error(f"Background ingestion failed: {e}")
        
        background_tasks.add_task(run_ingestion)
        
        # Return immediate response
        return DataIngestionResponse(
            successful_tickers=[],
            failed_tickers=[],
            records_inserted=0,
            date_range=None,
            errors=["Ingestion started in background. Check logs for progress."]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting ingestion: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@router.get("/providers", response_model=Dict[str, Any])
async def get_available_providers(
    current_user: User = Depends(get_current_user)
):
    """Get information about available data providers"""
    
    providers = DataProviderFactory.get_available_providers()
    return {"providers": providers}

@router.post("/ingest/sync", response_model=DataIngestionResponse)  
async def ingest_price_data_sync(
    request: DataIngestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Synchronously ingest price data (for small datasets, Admin only)"""
    
    # Check admin permissions
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if len(request.tickers) > 5:
        raise HTTPException(
            status_code=400, 
            detail="Use async endpoint (/ingest) for more than 5 tickers"
        )
    
    try:
        # Map provider type
        provider_type_map = {
            "kaggle": DataProviderType.KAGGLE,
            "yahoo": DataProviderType.YAHOO_FINANCE,
        }
        
        provider_type = provider_type_map.get(request.provider_type.lower())
        if not provider_type:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported provider type: {request.provider_type}"
            )
        
        # Create provider and ingest
        provider = DataProviderFactory.create_provider(provider_type, db)
        
        if not provider.test_connection():
            raise HTTPException(
                status_code=503,
                detail=f"Cannot connect to {request.provider_type} data source"
            )
        
        result = provider.ingest_historical_data(
            request.tickers,
            request.start_date,
            request.end_date
        )
        
        return DataIngestionResponse(
            successful_tickers=result.successful_tickers,
            failed_tickers=result.failed_tickers,
            records_inserted=result.records_inserted,
            date_range=result.date_range,
            errors=result.errors
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sync ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")