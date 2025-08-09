"""
Base Data Provider Interface

This module defines the abstract base class and common interfaces
that all data providers must implement. This ensures consistency
across different data sources and makes the system easily extensible.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Dict, List, Any, Optional, Set
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class DataProviderType(str, Enum):
    """Supported data provider types"""
    KAGGLE = "kaggle"
    YAHOO_FINANCE = "yahoo_finance" 
    ALPHA_VANTAGE = "alpha_vantage"
    POLYGON = "polygon"
    QUANDL = "quandl"
    # Add more as needed

class DataQuality(str, Enum):
    """Data quality levels"""
    HIGH = "high"           # Real-time, premium sources
    MEDIUM = "medium"       # Daily updates, reliable
    LOW = "low"            # Historical only, test data
    TEST = "test"          # Test/development data

@dataclass
class DataProviderConfig:
    """Configuration for a data provider"""
    name: str
    provider_type: DataProviderType
    data_quality: DataQuality
    credentials: Dict[str, str] = field(default_factory=dict)
    settings: Dict[str, Any] = field(default_factory=dict)
    rate_limits: Dict[str, int] = field(default_factory=dict)  # requests per minute, etc.
    enabled: bool = True

@dataclass 
class IngestionResult:
    """Result of a data ingestion operation"""
    provider_name: str
    successful_tickers: List[str] = field(default_factory=list)
    failed_tickers: List[Dict[str, str]] = field(default_factory=list)  # {ticker, error}
    records_inserted: int = 0
    date_range: Optional[Dict[str, str]] = None  # start_date, end_date
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

class BaseDataProvider(ABC):
    """
    Abstract base class for all data providers.
    
    Each provider implementation should:
    1. Handle its own authentication/credentials
    2. Implement rate limiting if needed
    3. Provide consistent error handling
    4. Support both bulk and incremental data ingestion
    5. Be testable in isolation
    """
    
    def __init__(self, config: DataProviderConfig):
        self.config = config
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """Validate provider-specific configuration"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test if the provider connection/credentials work.
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_available_tickers(self) -> Set[str]:
        """
        Get list of available ticker symbols from this provider.
        
        Returns:
            Set of available ticker symbols
        """
        pass
    
    @abstractmethod
    def ingest_historical_data(self, 
                             tickers: List[str], 
                             start_date: Optional[date] = None,
                             end_date: Optional[date] = None) -> IngestionResult:
        """
        Ingest historical price data for given tickers.
        
        Args:
            tickers: List of ticker symbols to ingest
            start_date: Start date for data (None = earliest available)
            end_date: End date for data (None = latest available)
            
        Returns:
            IngestionResult with operation details
        """
        pass
    
    @abstractmethod
    def ingest_recent_data(self, 
                          tickers: List[str], 
                          days_back: int = 30) -> IngestionResult:
        """
        Ingest recent price data for given tickers.
        
        Args:
            tickers: List of ticker symbols to update
            days_back: Number of days back to fetch
            
        Returns:
            IngestionResult with operation details
        """
        pass
    
    def get_data_summary(self, ticker: str) -> Dict[str, Any]:
        """
        Get summary of available data for a ticker from this provider.
        Base implementation - can be overridden by providers.
        
        Args:
            ticker: Ticker symbol
            
        Returns:
            Dictionary with data summary
        """
        return {
            "provider": self.config.name,
            "provider_type": self.config.provider_type.value,
            "data_quality": self.config.data_quality.value,
            "ticker": ticker,
            "summary": "Not implemented"
        }
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about this provider"""
        return {
            "name": self.config.name,
            "type": self.config.provider_type.value,
            "data_quality": self.config.data_quality.value,
            "enabled": self.config.enabled,
            "rate_limits": self.config.rate_limits,
            "has_credentials": bool(self.config.credentials)
        }
    
    def _log_operation(self, operation: str, details: Dict[str, Any]):
        """Log provider operations for monitoring"""
        self.logger.info(f"{self.config.name} - {operation}: {details}")
    
    def _handle_rate_limit(self, operation: str) -> None:
        """Handle rate limiting for provider operations"""
        # Base implementation - providers can override for specific rate limiting
        pass