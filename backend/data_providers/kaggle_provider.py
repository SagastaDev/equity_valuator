"""
Kaggle Data Provider

Reference implementation for the Kaggle Stock Market Dataset.
This provider serves as a template/example for implementing other data providers.

Note: This is primarily for testing and development. For production use,
consider providers with real-time data and API access.
"""

import pandas as pd
import numpy as np
from datetime import date, datetime
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
import os
import zipfile
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_

from .base_provider import (
    BaseDataProvider, 
    DataProviderConfig, 
    IngestionResult,
    DataProviderType,
    DataQuality
)
from backend.db.models.company import Company
from backend.db.models.provider import Provider
from backend.db.models.price import PriceData, PricePeriodType

logger = logging.getLogger(__name__)

class KaggleStockDataProvider(BaseDataProvider):
    """
    Kaggle Stock Market Dataset Provider
    
    Provides historical stock data from the Kaggle dataset:
    https://www.kaggle.com/datasets/paultimothymooney/stock-market-data
    
    This implementation serves as a reference for other providers and
    demonstrates best practices for data provider architecture.
    """
    
    def __init__(self, config: DataProviderConfig, db_session: Session):
        super().__init__(config)
        self.db = db_session
        self.data_dir = Path(config.settings.get('data_dir', 'data/kaggle'))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Get or create the provider record in database
        self.db_provider = self._get_or_create_db_provider()
    
    def _validate_config(self) -> None:
        """Validate Kaggle-specific configuration"""
        required_settings = ['data_dir']
        for setting in required_settings:
            if setting not in self.config.settings:
                raise ValueError(f"Missing required setting: {setting}")
        
        # Validate credentials if API access is configured
        if self.config.credentials.get('use_api', False):
            if not self.config.credentials.get('api_username') or not self.config.credentials.get('api_key'):
                raise ValueError("Kaggle API credentials required when use_api=True")
    
    def _get_or_create_db_provider(self) -> Provider:
        """Get or create provider record in database"""
        provider = self.db.query(Provider).filter(Provider.name == self.config.name).first()
        if not provider:
            provider = Provider(name=self.config.name)
            self.db.add(provider)
            self.db.commit()
            self.db.refresh(provider)
        return provider
    
    def test_connection(self) -> bool:
        """Test if Kaggle data is accessible"""
        try:
            # Check if dataset is already downloaded
            dataset_path = self.data_dir / "stock-market-data.zip"
            extracted_path = self.data_dir / "extracted"
            sample_path = self.data_dir / "sample"
            
            if dataset_path.exists() or extracted_path.exists():
                self.logger.info("Kaggle dataset found locally")
                return True
            
            # Check for sample data directory
            if sample_path.exists() and any(sample_path.glob("*.csv")):
                self.logger.info("Sample data directory found")
                return True
            
            # If using API, test API connection
            if self.config.credentials.get('use_api', False):
                return self._test_kaggle_api()
            
            self.logger.warning("No Kaggle dataset found and API not configured")
            return False
            
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def _test_kaggle_api(self) -> bool:
        """Test Kaggle API connection"""
        try:
            import kaggle
            kaggle.api.authenticate()
            # Try to list datasets to test API
            kaggle.api.dataset_list(search="stock", max_size=1)
            return True
        except Exception as e:
            self.logger.error(f"Kaggle API test failed: {e}")
            return False
    
    def get_available_tickers(self) -> Set[str]:
        """Get available ticker symbols from Kaggle dataset"""
        try:
            extracted_path = self._ensure_data_extracted()
            
            # Scan for CSV files - different dataset structures possible
            ticker_files = []
            for pattern in ["*.csv", "stocks/*.csv", "**/*.csv"]:
                ticker_files.extend(list(Path(extracted_path).glob(pattern)))
            
            # Extract ticker symbols from filenames
            tickers = set()
            for file_path in ticker_files:
                # Remove .csv extension and get ticker
                ticker = file_path.stem.upper()
                # Basic validation - ticker should be letters/numbers, 1-5 chars typically
                if ticker.isalnum() and 1 <= len(ticker) <= 6:
                    tickers.add(ticker)
            
            self.logger.info(f"Found {len(tickers)} available tickers")
            return tickers
            
        except Exception as e:
            self.logger.error(f"Error getting available tickers: {e}")
            return set()
    
    def ingest_historical_data(self, 
                             tickers: List[str], 
                             start_date: Optional[date] = None,
                             end_date: Optional[date] = None) -> IngestionResult:
        """Ingest historical data from Kaggle dataset"""
        
        result = IngestionResult(provider_name=self.config.name)
        
        try:
            # Ensure data is available
            extracted_path = self._ensure_data_extracted()
            
            for ticker in tickers:
                try:
                    records_count = self._ingest_ticker_data(
                        ticker, extracted_path, start_date, end_date
                    )
                    result.successful_tickers.append(ticker)
                    result.records_inserted += records_count
                    
                    self._log_operation("ingest_historical", {
                        "ticker": ticker,
                        "records": records_count
                    })
                    
                except Exception as e:
                    error_msg = f"Failed to process {ticker}: {str(e)}"
                    result.failed_tickers.append({"ticker": ticker, "error": error_msg})
                    result.errors.append(error_msg)
                    self.logger.error(error_msg)
            
            # Get overall date range for successful tickers
            if result.successful_tickers:
                result.date_range = self._get_date_range(result.successful_tickers)
            
        except Exception as e:
            error_msg = f"Bulk ingestion failed: {str(e)}"
            result.errors.append(error_msg)
            self.logger.error(error_msg)
        
        return result
    
    def ingest_recent_data(self, tickers: List[str], days_back: int = 30) -> IngestionResult:
        """
        Kaggle dataset is typically historical only, so this method
        will return empty result or could be used to re-ingest recent data.
        """
        result = IngestionResult(provider_name=self.config.name)
        
        # Kaggle data is typically static/historical
        # Could implement partial re-ingestion of recent dates if needed
        warning_msg = f"Kaggle provider: Recent data ingestion not supported (historical data only)"
        result.errors.append(warning_msg)
        self.logger.warning(warning_msg)
        
        return result
    
    def _ensure_data_extracted(self) -> str:
        """Ensure Kaggle data is downloaded and extracted"""
        extracted_path = self.data_dir / "extracted"
        
        if extracted_path.exists():
            return str(extracted_path)
        
        # Check for sample data directory
        sample_path = self.data_dir / "sample"
        if sample_path.exists() and any(sample_path.glob("*.csv")):
            return str(sample_path)
        
        # Try to extract from existing zip
        dataset_path = self.data_dir / "stock-market-data.zip"
        if dataset_path.exists():
            return self._extract_dataset(str(dataset_path))
        
        # Try to download via API if configured
        if self.config.credentials.get('use_api', False):
            downloaded_path = self._download_via_api()
            if downloaded_path:
                return self._extract_dataset(downloaded_path)
        
        raise FileNotFoundError(
            f"Kaggle dataset not found. Please download manually to {dataset_path} "
            "or configure API credentials."
        )
    
    def _download_via_api(self) -> Optional[str]:
        """Download dataset via Kaggle API"""
        try:
            import kaggle
            
            dataset_path = self.data_dir / "stock-market-data.zip"
            
            self.logger.info("Downloading Kaggle dataset via API...")
            kaggle.api.dataset_download_files(
                'paultimothymooney/stock-market-data',
                path=str(self.data_dir),
                unzip=False
            )
            
            return str(dataset_path) if dataset_path.exists() else None
            
        except Exception as e:
            self.logger.error(f"Failed to download via API: {e}")
            return None
    
    def _extract_dataset(self, zip_path: str) -> str:
        """Extract dataset from zip file"""
        extracted_path = self.data_dir / "extracted"
        
        self.logger.info(f"Extracting {zip_path}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extracted_path)
        
        return str(extracted_path)
    
    def _ingest_ticker_data(self, ticker: str, data_path: str, 
                           start_date: Optional[date], end_date: Optional[date]) -> int:
        """Ingest data for a single ticker"""
        
        # Get or create company
        company = self._get_or_create_company(ticker)
        
        # Find ticker CSV file
        csv_file = self._find_ticker_csv(ticker, data_path)
        if not csv_file:
            raise FileNotFoundError(f"No CSV file found for ticker {ticker}")
        
        # Load and process data
        df = pd.read_csv(csv_file)
        df = self._standardize_dataframe(df)
        
        # Apply date filters if specified
        if start_date or end_date:
            df = self._filter_by_date(df, start_date, end_date)
        
        # Remove existing records to avoid duplicates
        df = self._filter_existing_records(df, company.id)
        
        if df.empty:
            return 0
        
        # Bulk insert price data
        return self._bulk_insert_price_data(df, company.id)
    
    def _find_ticker_csv(self, ticker: str, data_path: str) -> Optional[Path]:
        """Find CSV file for given ticker"""
        possible_paths = [
            Path(data_path) / f"{ticker}.csv",
            Path(data_path) / f"{ticker.upper()}.csv",
            Path(data_path) / f"{ticker.lower()}.csv",
            Path(data_path) / "stocks" / f"{ticker}.csv",
            Path(data_path) / "stocks" / f"{ticker.upper()}.csv",
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        return None
    
    def _standardize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names and data types"""
        # Standardize column names
        df.columns = df.columns.str.strip().str.title().str.replace(' ', '_')
        
        column_mapping = {
            'Date': 'Date',
            'Open': 'Open',
            'High': 'High', 
            'Low': 'Low',
            'Close': 'Close',
            'Adj_Close': 'Adj_Close',
            'Volume': 'Volume'
        }
        df = df.rename(columns=column_mapping)
        
        # Convert date
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Ensure numeric columns
        numeric_cols = ['Open', 'High', 'Low', 'Close', 'Adj_Close', 'Volume']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def _filter_by_date(self, df: pd.DataFrame, start_date: Optional[date], 
                       end_date: Optional[date]) -> pd.DataFrame:
        """Filter dataframe by date range"""
        if start_date:
            df = df[df['Date'].dt.date >= start_date]
        if end_date:
            df = df[df['Date'].dt.date <= end_date]
        return df
    
    def _filter_existing_records(self, df: pd.DataFrame, company_id) -> pd.DataFrame:
        """Filter out records that already exist in database"""
        existing_dates = set(
            record.date for record in 
            self.db.query(PriceData.date)
            .filter(and_(
                PriceData.company_id == company_id,
                PriceData.provider_id == self.db_provider.id
            ))
            .all()
        )
        
        return df[~df['Date'].dt.date.isin(existing_dates)]
    
    def _bulk_insert_price_data(self, df: pd.DataFrame, company_id) -> int:
        """Bulk insert price data records"""
        price_records = []
        
        for _, row in df.iterrows():
            price_record = PriceData(
                company_id=company_id,
                provider_id=self.db_provider.id,
                date=row['Date'].date(),
                period_type=PricePeriodType.DAILY,
                open=float(row.get('Open')) if not pd.isna(row.get('Open')) else None,
                close=float(row.get('Close')) if not pd.isna(row.get('Close')) else None,
                adj_close=float(row.get('Adj_Close', row.get('Close'))) if not pd.isna(row.get('Adj_Close', row.get('Close'))) else None,
                volume=int(row.get('Volume')) if not pd.isna(row.get('Volume')) else None
            )
            price_records.append(price_record)
        
        # Batch insert
        batch_size = 1000
        inserted_count = 0
        
        for i in range(0, len(price_records), batch_size):
            batch = price_records[i:i + batch_size]
            self.db.bulk_save_objects(batch)
            self.db.commit()
            inserted_count += len(batch)
        
        return inserted_count
    
    def _get_or_create_company(self, ticker: str) -> Company:
        """Get or create company record"""
        company = self.db.query(Company).filter(Company.ticker == ticker).first()
        if not company:
            company = Company(
                ticker=ticker,
                name=ticker,  # Kaggle doesn't provide company names
                country='Unknown',
                currency='USD'
            )
            self.db.add(company)
            self.db.commit()
            self.db.refresh(company)
        
        return company
    
    def _get_date_range(self, tickers: List[str]) -> Dict[str, str]:
        """Get date range of ingested data"""
        try:
            companies = self.db.query(Company).filter(Company.ticker.in_(tickers)).all()
            company_ids = [c.id for c in companies]
            
            from sqlalchemy import func
            date_range = self.db.query(
                func.min(PriceData.date).label('min_date'),
                func.max(PriceData.date).label('max_date')
            ).filter(
                and_(
                    PriceData.company_id.in_(company_ids),
                    PriceData.provider_id == self.db_provider.id
                )
            ).first()
            
            return {
                "start_date": date_range.min_date.isoformat() if date_range.min_date else None,
                "end_date": date_range.max_date.isoformat() if date_range.max_date else None
            }
        except Exception as e:
            self.logger.error(f"Error getting date range: {e}")
            return {}
    
    def get_data_summary(self, ticker: str) -> Dict[str, Any]:
        """Get data summary for a specific ticker"""
        try:
            company = self.db.query(Company).filter(Company.ticker == ticker).first()
            if not company:
                return {"error": "Company not found"}
            
            from sqlalchemy import func
            summary = self.db.query(
                func.min(PriceData.date).label('start_date'),
                func.max(PriceData.date).label('end_date'),
                func.count(PriceData.id).label('record_count')
            ).filter(
                and_(
                    PriceData.company_id == company.id,
                    PriceData.provider_id == self.db_provider.id
                )
            ).first()
            
            return {
                "provider": self.config.name,
                "provider_type": self.config.provider_type.value,
                "data_quality": self.config.data_quality.value,
                "ticker": ticker,
                "company_name": company.name,
                "start_date": summary.start_date.isoformat() if summary.start_date else None,
                "end_date": summary.end_date.isoformat() if summary.end_date else None,
                "record_count": summary.record_count or 0
            }
            
        except Exception as e:
            return {"error": str(e)}