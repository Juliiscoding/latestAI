"""
ProHandel API connector for the Mercurios.ai ETL pipeline.
"""
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Generator

import backoff
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from etl.config.config import API_CONFIG, API_ENDPOINTS, ETL_CONFIG
from etl.utils.auth import token_manager
from etl.utils.logger import logger
from etl.utils.database import get_last_timestamp
from etl.validators.schema_validator import schema_validator

class ProHandelConnector:
    """
    Connector for the ProHandel API.
    Handles data extraction with incremental loading, authentication, and validation.
    """
    
    def __init__(self):
        """Initialize the ProHandel API connector."""
        self.api_url = API_CONFIG["api_url"]
        self.max_retries = ETL_CONFIG["max_retries"]
        self.retry_delay = ETL_CONFIG["retry_delay"]
        self.batch_size = ETL_CONFIG["batch_size"]
        self.incremental_load = ETL_CONFIG["incremental_load"]
    
    @backoff.on_exception(
        backoff.expo,
        (requests.exceptions.RequestException, ConnectionError),
        max_tries=3,
        factor=2
    )
    def _make_request(self, endpoint: str, method: str = "GET", params: Dict = None, data: Dict = None) -> Any:
        """
        Make an API request with authentication and error handling.
        
        Args:
            endpoint: API endpoint to call
            method: HTTP method (GET, POST, etc.)
            params: Query parameters
            data: Request body data
            
        Returns:
            API response data
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        # Ensure we have a valid token
        token = token_manager.get_token()
        
        # Construct headers with authentication
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Make sure endpoint starts with a slash
        if not endpoint.startswith('/'):
            endpoint = f"/{endpoint}"
            
        # Get the server URL from token_manager if available
        api_url = token_manager.server_url if hasattr(token_manager, 'server_url') and token_manager.server_url else self.api_url
        
        # Ensure the API URL doesn't end with a slash
        if api_url.endswith('/'):
            api_url = api_url[:-1]
            
        # Add the API path if not present
        if not api_url.endswith('/api/v2') and not '/api/v2/' in api_url:
            api_url = f"{api_url}/api/v2"
            
        # Construct the full URL
        url = f"{api_url}{endpoint}"
        
        logger.debug(f"Making {method} request to {url}")
        
        try:
            response = requests.request(method, url, headers=headers, params=params, json=data)
            response.raise_for_status()
            return response.json() if response.content else None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
    
    def get_entity_list(self, entity_name: str, page: int = 1, pagesize: Optional[int] = None, 
                        params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Get a list of entities from the API.
        
        Args:
            entity_name: Name of the entity (e.g., 'article', 'customer')
            page: Page number
            pagesize: Number of items per page
            params: Additional query parameters
            
        Returns:
            List of entity data
        """
        if entity_name not in API_ENDPOINTS:
            raise ValueError(f"Unknown entity: {entity_name}")
        
        endpoint_config = API_ENDPOINTS[entity_name]
        endpoint = endpoint_config.get("endpoint", f"/{entity_name}")
        pagesize = pagesize or endpoint_config.get("batch_size", self.batch_size)
        
        # Prepare query parameters
        query_params = params or {}
        query_params.update({"page": page, "pagesize": pagesize})
        
        try:
            logger.info(f"Fetching {entity_name} data (page {page}, pagesize {pagesize})")
            # Make sure the endpoint starts with a slash
            if not endpoint.startswith('/'):
                endpoint = f"/{endpoint}"
            data = self._make_request(endpoint, params=query_params)
            
            # Handle different response formats
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and any(k in data for k in ["items", "data", "results"]):
                for key in ["items", "data", "results"]:
                    if key in data:
                        return data[key]
            
            logger.warning(f"Unexpected response format for {entity_name}")
            return data if isinstance(data, list) else []
            
        except Exception as e:
            logger.error(f"Error fetching {entity_name} data: {e}")
            return []
    
    def get_entity_by_id(self, entity_name: str, entity_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific entity by ID.
        
        Args:
            entity_name: Name of the entity (e.g., 'article', 'customer')
            entity_id: ID of the entity
            
        Returns:
            Entity data or None if not found
        """
        if entity_name not in API_ENDPOINTS:
            raise ValueError(f"Unknown entity: {entity_name}")
        
        try:
            logger.info(f"Fetching {entity_name} with ID {entity_id}")
            return self._make_request(f"{entity_name}/{entity_id}")
        except Exception as e:
            logger.error(f"Error fetching {entity_name} with ID {entity_id}: {e}")
            return None
    
    def extract_all_entities(self, entity_name: str, validate: bool = True, 
                             incremental: Optional[bool] = None) -> Generator[List[Dict[str, Any]], None, None]:
        """
        Extract all entities of a given type, with pagination.
        
        Args:
            entity_name: Name of the entity (e.g., 'article', 'customer')
            validate: Whether to validate the data against its schema
            incremental: Whether to use incremental loading (overrides global setting)
            
        Yields:
            Batches of entity data
        """
        if entity_name not in API_ENDPOINTS:
            raise ValueError(f"Unknown entity: {entity_name}")
        
        endpoint_config = API_ENDPOINTS[entity_name]
        pagesize = endpoint_config.get("batch_size", self.batch_size)
        
        # Determine whether to use incremental loading
        use_incremental = incremental if incremental is not None else self.incremental_load
        
        # Get timestamp for incremental loading
        timestamp_field = endpoint_config.get("timestamp_field")
        last_timestamp = None
        
        if use_incremental and timestamp_field:
            last_timestamp = get_last_timestamp(entity_name, timestamp_field)
            if last_timestamp:
                logger.info(f"Using incremental loading for {entity_name} from {last_timestamp}")
        
        # Prepare query parameters for incremental loading
        params = {}
        if use_incremental and last_timestamp and timestamp_field:
            # Format may need to be adjusted based on API requirements
            params[f"{timestamp_field}_gt"] = last_timestamp.isoformat()
        
        page = 1
        total_items = 0
        
        while True:
            try:
                # Fetch data for current page
                data_batch = self.get_entity_list(entity_name, page=page, pagesize=pagesize, params=params)
                
                # If no data or empty list, we've reached the end
                if not data_batch:
                    logger.info(f"No more {entity_name} data to fetch")
                    break
                
                # Validate data if requested
                if validate:
                    data_batch = schema_validator.validate_batch(entity_name, data_batch)
                
                # Update counters
                batch_size = len(data_batch)
                total_items += batch_size
                
                logger.info(f"Fetched {batch_size} {entity_name} items (page {page}, total {total_items})")
                
                # Yield the batch
                yield data_batch
                
                # If we got fewer items than requested, we've reached the end
                if batch_size < pagesize:
                    logger.info(f"Reached end of {entity_name} data (got {batch_size}, expected {pagesize})")
                    break
                
                # Move to next page
                page += 1
                
                # Add a small delay to avoid overwhelming the API
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error extracting {entity_name} data: {e}")
                break
    
    def generate_schemas_from_samples(self, save: bool = True) -> Dict[str, Dict[str, Any]]:
        """
        Generate JSON schemas for all entity types from sample data.
        
        Args:
            save: Whether to save the generated schemas to files
            
        Returns:
            Dictionary of generated schemas
        """
        schemas = {}
        
        for entity_name in API_ENDPOINTS:
            try:
                # Fetch a sample of data
                sample_data = self.get_entity_list(entity_name, page=1, pagesize=5)
                
                if not sample_data:
                    logger.warning(f"No sample data available for {entity_name}")
                    continue
                
                # Generate schema
                schema = schema_validator.generate_schema(entity_name, sample_data, save=save)
                schemas[entity_name] = schema
                
            except Exception as e:
                logger.error(f"Error generating schema for {entity_name}: {e}")
        
        return schemas

# Create a singleton instance
prohandel_connector = ProHandelConnector()
