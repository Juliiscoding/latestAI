"""
ProHandel API connector module for data extraction.
"""

import logging
import requests
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta

from etl.utils.auth import TokenManager
from etl.config.config import API_CONFIG

logger = logging.getLogger(__name__)

class ProHandelConnector:
    """
    Connector for the ProHandel API to extract data.
    
    This class handles the connection to the ProHandel API, including:
    - Authentication using the TokenManager
    - Data extraction with pagination
    - Error handling and retries
    - Incremental loading based on timestamps
    """
    
    def __init__(self, api_url: str, token_manager: TokenManager, 
                 max_retries: int = 3, retry_delay: int = 2):
        """
        Initialize the ProHandel API connector.
        
        Args:
            api_url: Base URL for the ProHandel API
            token_manager: TokenManager instance for authentication
            max_retries: Maximum number of retries for failed API calls
            retry_delay: Delay between retries in seconds
        """
        self.api_url = api_url.rstrip('/')
        self.token_manager = token_manager
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session = requests.Session()
    
    def get_headers(self) -> Dict[str, str]:
        """
        Get the headers for API requests, including the authentication token.
        
        Returns:
            Dictionary of headers
        """
        token = self.token_manager.authenticate()
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def get_data(self, endpoint: str, params: Optional[Dict[str, Any]] = None, 
                 paginate: bool = True, page_size: int = 100) -> List[Dict[str, Any]]:
        """
        Get data from the ProHandel API.
        
        Args:
            endpoint: API endpoint to call
            params: Query parameters
            paginate: Whether to handle pagination
            page_size: Number of records per page
            
        Returns:
            List of data records
        """
        url = f"{self.api_url}{endpoint}"
        all_data = []
        
        # Initialize parameters
        query_params = params.copy() if params else {}
        if paginate:
            query_params['limit'] = page_size
            query_params['page'] = 1
        
        while True:
            # Make API request with retries
            response_data = self._make_request_with_retry(url, query_params)
            
            # Extract data from response
            if isinstance(response_data, dict) and 'data' in response_data:
                # Handle paginated response format
                data = response_data.get('data', [])
                all_data.extend(data)
                
                # Check if there are more pages
                if paginate and 'meta' in response_data:
                    meta = response_data.get('meta', {})
                    current_page = meta.get('current_page', 0)
                    last_page = meta.get('last_page', 0)
                    
                    if current_page >= last_page:
                        break
                    
                    query_params['page'] = current_page + 1
                else:
                    break
            elif isinstance(response_data, list):
                # Handle non-paginated list response
                all_data.extend(response_data)
                break
            else:
                # Unknown response format
                logger.warning(f"Unexpected response format from {endpoint}: {type(response_data)}")
                break
        
        return all_data
    
    def get_incremental_data(self, endpoint: str, timestamp_field: str, 
                            last_timestamp: Optional[str] = None, 
                            params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get data incrementally based on a timestamp field.
        
        Args:
            endpoint: API endpoint to call
            timestamp_field: Field name to use for incremental loading
            last_timestamp: ISO format timestamp to use as the starting point
            params: Additional query parameters
            
        Returns:
            List of data records
        """
        query_params = params.copy() if params else {}
        
        if last_timestamp:
            # Add filter for timestamp field
            query_params[f'filter[{timestamp_field}][gte]'] = last_timestamp
        
        # Sort by timestamp field to ensure consistent ordering
        query_params[f'sort'] = timestamp_field
        
        return self.get_data(endpoint, query_params)
    
    def _make_request_with_retry(self, url: str, params: Dict[str, Any]) -> Union[Dict[str, Any], List[Any]]:
        """
        Make an API request with retry logic.
        
        Args:
            url: URL to call
            params: Query parameters
            
        Returns:
            Response data
            
        Raises:
            Exception: If all retries fail
        """
        for attempt in range(self.max_retries):
            try:
                headers = self.get_headers()
                response = self.session.get(url, headers=headers, params=params, timeout=30)
                
                # Check for rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', self.retry_delay))
                    logger.warning(f"Rate limited. Retrying after {retry_after} seconds.")
                    time.sleep(retry_after)
                    continue
                
                # Check for auth errors
                if response.status_code == 401:
                    logger.info("Authentication token expired. Refreshing token.")
                    self.token_manager.refresh_token()
                    continue
                
                # Raise for other errors
                response.raise_for_status()
                
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt+1}/{self.max_retries}): {str(e)}")
                
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    sleep_time = self.retry_delay * (2 ** attempt)
                    time.sleep(sleep_time)
                else:
                    logger.error(f"All retries failed for {url}")
                    raise
        
        # This should not be reached due to the raise in the loop
        raise Exception(f"All retries failed for {url}")
    
    def get_latest_timestamp(self, data: List[Dict[str, Any]], timestamp_field: str) -> Optional[str]:
        """
        Get the latest timestamp from a list of data records.
        
        Args:
            data: List of data records
            timestamp_field: Field name containing timestamps
            
        Returns:
            ISO format timestamp string or None if no timestamps found
        """
        if not data:
            return None
        
        timestamps = []
        for record in data:
            ts = record.get(timestamp_field)
            if ts:
                try:
                    # Parse timestamp to ensure it's valid
                    dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    timestamps.append(dt)
                except (ValueError, TypeError):
                    continue
        
        if not timestamps:
            return None
        
        # Return the latest timestamp
        latest = max(timestamps)
        return latest.isoformat()
