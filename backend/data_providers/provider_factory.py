"""
Data Provider Factory

Factory class for creating and managing data provider instances.
This centralizes provider configuration and makes it easy to add new providers.
"""

from typing import Dict, Type, Optional
from sqlalchemy.orm import Session
import logging

from .base_provider import BaseDataProvider, DataProviderConfig, DataProviderType, DataQuality
from .kaggle_provider import KaggleStockDataProvider

logger = logging.getLogger(__name__)

class DataProviderFactory:
    """
    Factory for creating data provider instances.
    
    This class handles:
    - Provider registration and configuration
    - Instance creation with proper dependencies
    - Configuration validation
    - Provider discovery
    """
    
    # Registry of available provider classes
    _provider_classes: Dict[DataProviderType, Type[BaseDataProvider]] = {
        DataProviderType.KAGGLE: KaggleStockDataProvider,
        # Add more providers here as they are implemented:
        # DataProviderType.ALPHA_VANTAGE: AlphaVantageProvider,
        # DataProviderType.POLYGON: PolygonProvider,
    }
    
    # Default configurations for different providers
    _default_configs = {
        DataProviderType.KAGGLE: {
            "name": "Kaggle Stock Market Data",
            "data_quality": DataQuality.TEST,
            "settings": {
                "data_dir": "data/kaggle"
            },
            "rate_limits": {
                "requests_per_minute": 10  # Conservative for file-based operations
            }
        },
        # Future providers can have their default configs here
    }
    
    @classmethod
    def create_provider(cls, 
                       provider_type: DataProviderType, 
                       db_session: Session,
                       config: Optional[DataProviderConfig] = None,
                       **config_overrides) -> BaseDataProvider:
        """
        Create a data provider instance.
        
        Args:
            provider_type: Type of provider to create
            db_session: Database session for the provider
            config: Optional custom configuration
            **config_overrides: Additional config parameters to override
            
        Returns:
            Configured data provider instance
            
        Raises:
            ValueError: If provider type is not supported
        """
        
        if provider_type not in cls._provider_classes:
            available = list(cls._provider_classes.keys())
            raise ValueError(f"Unsupported provider type: {provider_type}. Available: {available}")
        
        # Create configuration if not provided
        if config is None:
            config = cls._create_default_config(provider_type, **config_overrides)
        else:
            # Apply any overrides to the provided config
            cls._apply_config_overrides(config, **config_overrides)
        
        # Get the provider class and create instance
        provider_class = cls._provider_classes[provider_type]
        
        try:
            # Different providers might have different constructor signatures
            # Handle this gracefully
            if provider_type == DataProviderType.KAGGLE:
                return provider_class(config, db_session)
            else:
                # Generic fallback - most providers should follow this pattern
                return provider_class(config, db_session)
                
        except Exception as e:
            logger.error(f"Failed to create {provider_type.value} provider: {e}")
            raise
    
    @classmethod
    def _create_default_config(cls, provider_type: DataProviderType, **overrides) -> DataProviderConfig:
        """Create default configuration for a provider type"""
        defaults = cls._default_configs.get(provider_type, {}).copy()
        defaults.update(overrides)
        
        return DataProviderConfig(
            name=defaults.get("name", f"{provider_type.value} Provider"),
            provider_type=provider_type,
            data_quality=defaults.get("data_quality", DataQuality.MEDIUM),
            credentials=defaults.get("credentials", {}),
            settings=defaults.get("settings", {}),
            rate_limits=defaults.get("rate_limits", {}),
            enabled=defaults.get("enabled", True)
        )
    
    @classmethod  
    def _apply_config_overrides(cls, config: DataProviderConfig, **overrides):
        """Apply configuration overrides to existing config"""
        for key, value in overrides.items():
            if hasattr(config, key):
                setattr(config, key, value)
            elif key in ['credentials', 'settings', 'rate_limits']:
                # Handle nested dictionary updates
                current_dict = getattr(config, key, {})
                if isinstance(value, dict):
                    current_dict.update(value)
                else:
                    logger.warning(f"Expected dict for {key}, got {type(value)}")
    
    @classmethod
    def get_available_providers(cls) -> Dict[str, Dict[str, str]]:
        """Get information about available providers"""
        providers = {}
        
        for provider_type, provider_class in cls._provider_classes.items():
            defaults = cls._default_configs.get(provider_type, {})
            providers[provider_type.value] = {
                "name": defaults.get("name", provider_type.value),
                "class": provider_class.__name__,
                "data_quality": defaults.get("data_quality", DataQuality.MEDIUM).value,
                "description": provider_class.__doc__.strip().split('\n')[0] if provider_class.__doc__ else "No description"
            }
        
        return providers
    
    @classmethod
    def register_provider(cls, 
                         provider_type: DataProviderType, 
                         provider_class: Type[BaseDataProvider],
                         default_config: Optional[Dict] = None):
        """
        Register a new provider type.
        
        This allows for dynamic registration of providers at runtime.
        
        Args:
            provider_type: The provider type enum
            provider_class: The provider implementation class
            default_config: Default configuration for this provider
        """
        
        if not issubclass(provider_class, BaseDataProvider):
            raise ValueError("Provider class must inherit from BaseDataProvider")
        
        cls._provider_classes[provider_type] = provider_class
        
        if default_config:
            cls._default_configs[provider_type] = default_config
        
        logger.info(f"Registered new provider: {provider_type.value}")
    
    @classmethod
    def create_test_providers(cls, db_session: Session) -> Dict[str, BaseDataProvider]:
        """
        Create instances of all available providers with test configurations.
        Useful for testing and development.
        
        Args:
            db_session: Database session
            
        Returns:
            Dictionary of provider instances keyed by provider type
        """
        providers = {}
        
        for provider_type in cls._provider_classes.keys():
            try:
                # Create with test/development settings
                config_overrides = {
                    "data_quality": DataQuality.TEST,
                    "enabled": True
                }
                
                provider = cls.create_provider(
                    provider_type, 
                    db_session, 
                    **config_overrides
                )
                providers[provider_type.value] = provider
                
            except Exception as e:
                logger.warning(f"Could not create test provider {provider_type.value}: {e}")
        
        return providers

# Convenience functions for common provider creation patterns

def create_kaggle_provider(db_session: Session, 
                          data_dir: str = "data/kaggle",
                          use_api: bool = False,
                          api_credentials: Optional[Dict[str, str]] = None) -> KaggleStockDataProvider:
    """
    Convenience function to create a Kaggle provider with common settings.
    
    Args:
        db_session: Database session
        data_dir: Directory for Kaggle data files
        use_api: Whether to use Kaggle API for downloads
        api_credentials: Kaggle API credentials if using API
        
    Returns:
        Configured Kaggle provider instance
    """
    
    credentials = {}
    if use_api and api_credentials:
        credentials.update(api_credentials)
        credentials["use_api"] = True
    
    return DataProviderFactory.create_provider(
        DataProviderType.KAGGLE,
        db_session,
        settings={"data_dir": data_dir},
        credentials=credentials
    )