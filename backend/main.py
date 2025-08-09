from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import valuation, transform, providers, companies
from backend.auth import routes as auth_routes
from backend.db.base import engine
from backend.db import models
from backend.db.session import get_db
from backend.db.init_data import initialize_database
import os
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Equity Valuation System",
    description="A modular equity valuation system with data transformation capabilities",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Initialize database with default data and load Kaggle sample data on startup."""
    db = next(get_db())
    try:
        # Initialize database with canonical fields, providers, etc.
        initialize_database(db)
        
        # Load Kaggle sample data automatically
        await load_kaggle_sample_data(db)
        
    finally:
        db.close()

async def load_kaggle_sample_data(db):
    """Load Kaggle sample data if it exists and hasn't been loaded yet."""
    try:
        from backend.data_providers import DataProviderFactory, DataProviderType
        from backend.db.models.company import Company
        from backend.db.models.price import PriceData
        
        # Check if we already have price data
        existing_price_data = db.query(PriceData).first()
        if existing_price_data:
            logger.info("Price data already exists, skipping Kaggle data load")
            return
        
        # Check if Kaggle data directory exists
        kaggle_data_dir = "/app/data/kaggle" if os.path.exists("/app/data/kaggle") else "data/kaggle"
        if not os.path.exists(kaggle_data_dir):
            logger.info("No Kaggle sample data directory found, skipping data load")
            return
            
        logger.info("Loading Kaggle sample data automatically...")
        
        # Companies to load
        target_companies = ["AAPL", "MSFT", "GOOGL", "NVDA", "LMT"]
        
        # Create Kaggle provider instance
        provider = DataProviderFactory.create_provider(
            DataProviderType.KAGGLE,
            db,
            settings={"data_dir": kaggle_data_dir}
        )
        
        # Test connection
        if not provider.test_connection():
            logger.warning("Kaggle provider connection test failed")
            return
        
        # Get available tickers
        available_tickers = provider.get_available_tickers()
        loadable_companies = [ticker for ticker in target_companies if ticker in available_tickers]
        
        if not loadable_companies:
            logger.warning("No Kaggle sample companies available for loading")
            return
        
        logger.info(f"Loading Kaggle data for: {loadable_companies}")
        
        # Ingest historical data
        result = provider.ingest_historical_data(loadable_companies)
        
        logger.info(f"Kaggle data load complete - {len(result.successful_tickers)} companies, {result.records_inserted:,} records")
        
    except Exception as e:
        logger.error(f"Error loading Kaggle sample data: {e}")
        # Don't fail startup if Kaggle data loading fails

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://0.0.0.0:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router, prefix="/auth", tags=["authentication"])
app.include_router(valuation.router, prefix="/api/valuation", tags=["valuation"])
app.include_router(transform.router, prefix="/api/transform", tags=["transform"])
app.include_router(providers.router, prefix="/api/providers", tags=["providers"])
app.include_router(companies.router, tags=["companies"])  # companies router includes its own prefix

@app.get("/")
async def root():
    return {"message": "Equity Valuation System API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}