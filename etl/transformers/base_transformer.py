"""
Base transformer for the Mercurios.ai ETL pipeline.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional
import os
import requests
from functools import lru_cache

from etl.utils.logger import logger

class BaseTransformer(ABC):
    """
    Base class for all transformers.
    Provides common transformation methods and defines the interface for entity-specific transformers.
    """
    
    def __init__(self):
        """Initialize the transformer."""
        self.entity_name = self.__class__.__name__.replace("Transformer", "").lower()
        logger.debug(f"Initializing {self.entity_name} transformer")
        self.exchange_rates = {}
        self.default_currency = os.environ.get("DEFAULT_CURRENCY", "EUR")
        self._load_exchange_rates()
    
    @abstractmethod
    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform a single data record.
        
        Args:
            data: Data record to transform
            
        Returns:
            Transformed data record
        """
        pass
    
    def transform_batch(self, data_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform a batch of data records.
        
        Args:
            data_batch: Batch of data records to transform
            
        Returns:
            Batch of transformed data records
        """
        transformed_batch = []
        
        for data in data_batch:
            try:
                transformed_data = self.transform(data)
                if transformed_data:
                    transformed_batch.append(transformed_data)
            except Exception as e:
                logger.error(f"Error transforming {self.entity_name} data: {e}")
                logger.debug(f"Problematic data: {data}")
        
        logger.info(f"Transformed {len(transformed_batch)}/{len(data_batch)} {self.entity_name} records")
        return transformed_batch
    
    def standardize_timestamp(self, timestamp: Any, field_name: str = "timestamp") -> Optional[datetime]:
        """
        Standardize a timestamp to a datetime object.
        
        Args:
            timestamp: Timestamp to standardize (string, datetime, or None)
            field_name: Name of the field (for logging)
            
        Returns:
            Standardized datetime object or None if invalid
        """
        if not timestamp:
            return None
        
        if isinstance(timestamp, datetime):
            return timestamp
        
        if isinstance(timestamp, str):
            try:
                # Try ISO format first
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                try:
                    # Try other common formats
                    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d.%m.%Y %H:%M:%S", "%d.%m.%Y"):
                        try:
                            return datetime.strptime(timestamp, fmt)
                        except ValueError:
                            continue
                    
                    logger.warning(f"Could not parse {field_name} timestamp: {timestamp}")
                    return None
                except Exception as e:
                    logger.error(f"Error parsing {field_name} timestamp: {e}")
                    return None
        
        logger.warning(f"Unsupported {field_name} timestamp type: {type(timestamp)}")
        return None
    
    def normalize_product_id(self, product_id: Any) -> str:
        """
        Normalize a product ID to a standard format.
        
        Args:
            product_id: Product ID to normalize
            
        Returns:
            Normalized product ID
        """
        if not product_id:
            return ""
        
        # Convert to string
        product_id_str = str(product_id)
        
        # Remove leading zeros
        product_id_str = product_id_str.lstrip('0')
        
        # Handle decimal points (convert to integer if possible)
        if '.' in product_id_str:
            try:
                float_val = float(product_id_str)
                if float_val.is_integer():
                    product_id_str = str(int(float_val))
            except ValueError:
                pass
        
        return product_id_str
    
    def _load_exchange_rates(self):
        """
        Load exchange rates from API or fallback to static rates.
        """
        try:
            # Try to get exchange rates from environment variable
            api_key = os.environ.get("EXCHANGE_RATE_API_KEY")
            if api_key:
                self._fetch_exchange_rates(api_key)
            else:
                logger.warning("No exchange rate API key found, using static rates")
                self._load_static_exchange_rates()
        except Exception as e:
            logger.error(f"Error loading exchange rates: {e}")
            self._load_static_exchange_rates()
    
    def _fetch_exchange_rates(self, api_key: str):
        """
        Fetch exchange rates from an API.
        
        Args:
            api_key: API key for the exchange rate service
        """
        try:
            # Use Exchange Rate API (https://exchangeratesapi.io/)
            base_url = "https://api.exchangeratesapi.io/latest"
            params = {
                "access_key": api_key,
                "base": self.default_currency
            }
            
            response = requests.get(base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get("success", False):
                    self.exchange_rates = data.get("rates", {})
                    logger.info(f"Loaded exchange rates for {len(self.exchange_rates)} currencies")
                else:
                    logger.error(f"Error fetching exchange rates: {data.get('error')}")
                    self._load_static_exchange_rates()
            else:
                logger.error(f"Error fetching exchange rates: HTTP {response.status_code}")
                self._load_static_exchange_rates()
        except Exception as e:
            logger.error(f"Error fetching exchange rates: {e}")
            self._load_static_exchange_rates()
    
    def _load_static_exchange_rates(self):
        """
        Load static exchange rates as a fallback.
        """
        # Static exchange rates (as of March 2023)
        self.exchange_rates = {
            "EUR": 1.0,
            "USD": 1.0731,
            "GBP": 0.8785,
            "CHF": 0.9868,
            "JPY": 143.94,
            "CAD": 1.4559,
            "AUD": 1.6158,
            "CNY": 7.4387,
            "SEK": 11.0613,
            "NOK": 11.2675,
            "DKK": 7.4419,
            "PLN": 4.6893,
            "CZK": 23.4839,
            "HUF": 378.77,
            "RON": 4.9195
        }
        logger.info(f"Loaded static exchange rates for {len(self.exchange_rates)} currencies")
    
    @lru_cache(maxsize=128)
    def convert_currency(self, amount: float, from_currency: str, to_currency: str = None) -> float:
        """
        Convert an amount from one currency to another.
        Uses real exchange rates if available, otherwise falls back to static rates.
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code (ISO 4217)
            to_currency: Target currency code (ISO 4217), defaults to DEFAULT_CURRENCY env var or EUR
            
        Returns:
            Converted amount
        """
        if amount is None:
            return 0.0
        
        # Default to the system default currency if not specified
        if to_currency is None:
            to_currency = self.default_currency
        
        # Normalize currency codes
        from_currency = from_currency.upper() if from_currency else self.default_currency
        to_currency = to_currency.upper() if to_currency else self.default_currency
        
        # If currencies are the same, no conversion needed
        if from_currency == to_currency:
            return amount
        
        try:
            # Check if we have the exchange rates
            if not self.exchange_rates:
                logger.warning("No exchange rates available, using 1:1 conversion")
                return amount
            
            # Get exchange rates for both currencies relative to base currency
            from_rate = self.exchange_rates.get(from_currency)
            to_rate = self.exchange_rates.get(to_currency)
            
            if from_rate is None or to_rate is None:
                logger.warning(f"Exchange rate not found for {from_currency} or {to_currency}, using 1:1 conversion")
                return amount
            
            # Convert to base currency first, then to target currency
            # If base currency is EUR, then:
            # amount_in_eur = amount / from_rate
            # result = amount_in_eur * to_rate
            result = amount * (to_rate / from_rate)
            
            return round(result, 2)
        except Exception as e:
            logger.error(f"Error converting currency: {e}")
            return amount
    
    def detect_currency(self, data: Dict[str, Any]) -> str:
        """
        Detect the currency used in a data record.
        
        Args:
            data: Data record
            
        Returns:
            Currency code (ISO 4217)
        """
        # Check common currency fields
        for field in ['currency', 'currency_code', 'currencyCode']:
            if field in data and data[field]:
                return data[field].upper()
        
        # Check for currency symbols in amount fields
        for field in ['amount', 'price', 'total', 'value']:
            if field in data and isinstance(data[field], str):
                amount_str = data[field]
                if '€' in amount_str:
                    return 'EUR'
                elif '$' in amount_str:
                    return 'USD'
                elif '£' in amount_str:
                    return 'GBP'
                elif '¥' in amount_str:
                    return 'JPY'
        
        # Default to system currency
        return self.default_currency
