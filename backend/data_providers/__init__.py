"""
Data Providers Module

This module contains integrations for various external data providers.
Each provider is implemented as a separate, self-contained module following
a common interface pattern.

This architecture allows for:
- Easy addition of new data providers
- Clean separation from core business logic
- Individual testing and configuration per provider
- Consistent data ingestion patterns
"""

from .base_provider import BaseDataProvider, DataProviderConfig, IngestionResult, DataProviderType
from .provider_factory import DataProviderFactory

__all__ = [
    'BaseDataProvider',
    'DataProviderConfig', 
    'IngestionResult',
    'DataProviderType',
    'DataProviderFactory'
]