import requests
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
import json

class ProHandelAPI:
    def __init__(self, api_key: str, api_secret: str):
        self.auth_url = "https://auth.prohandel.cloud/api/v4"
        self.api_url = "https://linde.prohandel.de/api/v2"  # Updated to use the verified working URL
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = None
        self.session = requests.Session()
        
    def authenticate(self) -> str:
        """
        Authenticate with the ProHandel API and get access token
        Returns the token value
        """
        try:
            auth_data = {
                "apiKey": self.api_key,
                "secret": self.api_secret
            }
            
            print("Authenticating...")
            response = self.session.post(f"{self.auth_url}/token", json=auth_data)
            response.raise_for_status()
            
            auth_response = response.json()
            self.access_token = auth_response["token"]["token"]["value"]
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            print(f"Authentication failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                if e.response.content:
                    print(f"Response content: {e.response.content.decode()}")
            raise

    def _make_request(self, endpoint: str, method: str = "GET", params: Dict = None, data: Dict = None) -> Any:
        """Make an API request with authentication"""
        if not self.access_token:
            self.authenticate()
            
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-API-Version": "v2.29.1"
        }
        
        # List of URL patterns to try, based on our testing
        url_patterns = [
            f"{self.api_url}/{endpoint.lstrip('/')}",                  # Standard pattern
            f"https://linde.prohandel.de/api/v2/{endpoint.lstrip('/')}",  # Direct URL with linde subdomain
            f"{self.api_url}/v2/{endpoint.lstrip('/')}",              # With v2 prefix
            f"{self.api_url}/api/v2/{endpoint.lstrip('/')}",          # With api/v2 prefix
            f"{self.api_url}/v2.29.1/{endpoint.lstrip('/')}"          # With version number
        ]
        
        last_error = None
        response = None
        
        for url in url_patterns:
            try:
                print(f"Making request to {url} with params {params}")
                response = self.session.request(method, url, headers=headers, params=params, json=data)
                response.raise_for_status()
                # If we get here, the request was successful
                break
            except requests.exceptions.RequestException as e:
                print(f"Request to {url} failed: {str(e)}")
                last_error = e
                response = getattr(e, 'response', None)
                # Try the next URL pattern
                continue
        
        # If we've tried all URLs and all failed, raise the last error
        if last_error and (response is None or response.status_code != 200):
            print(f"All URL patterns failed. Last error: {str(last_error)}")
            raise last_error
        
        # If we get here, we have a successful response
        try:
            # Print response headers and status for debugging
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {response.headers}")
            
            # Handle empty responses
            if not response.content or len(response.content) == 0:
                print("Empty response received")
                return {"data": [], "meta": {"pagination": {"total_pages": 0}}}
                
            # Parse JSON response
            json_response = response.json()
            print(f"Response type: {type(json_response)}")
            
            # Normalize response format
            if isinstance(json_response, list):
                # If response is a list, wrap it in a dict with data key
                print("Converting list response to dictionary format")
                return {"data": json_response, "meta": {"pagination": {"total_pages": 1}}}
            elif isinstance(json_response, dict):
                # If response is already a dict but doesn't have data key, add it
                if "data" not in json_response:
                    if any(isinstance(json_response.get(k), list) for k in json_response):
                        # Find the first list value and use it as data
                        for k, v in json_response.items():
                            if isinstance(v, list):
                                print(f"Using '{k}' as data key")
                                return {"data": v, "meta": {"pagination": {"total_pages": 1}}}
                    # If no lists found, wrap the whole response as a single item
                    print("Wrapping response in data array")
                    return {"data": [json_response], "meta": {"pagination": {"total_pages": 1}}}
            
            # Return original response if it's already in the expected format
            return json_response
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            print(f"Raw response: {response.content}")
            # Return empty data structure on JSON decode error
            return {"data": [], "meta": {"pagination": {"total_pages": 0}}}

    # Core endpoints
    def get_customers(self, page: int = 1, pagesize: int = 100, updated_since: Optional[str] = None) -> Dict:
        """Get customers with pagination and optional timestamp filter"""
        params = {"page": page, "pagesize": pagesize}
        if updated_since:
            params["updated_since"] = updated_since
        return self._make_request("customer", params=params)

    def get_articles(self, page: int = 1, pagesize: int = 100, updated_since: Optional[str] = None) -> Dict:
        """Get articles with pagination and optional timestamp filter"""
        params = {"page": page, "pagesize": pagesize}
        if updated_since:
            params["updated_since"] = updated_since
        return self._make_request("article", params=params)

    def get_orders(self, page: int = 1, pagesize: int = 100, updated_since: Optional[str] = None) -> Dict:
        """Get orders with pagination and optional timestamp filter"""
        params = {"page": page, "pagesize": pagesize}
        if updated_since:
            params["updated_since"] = updated_since
        return self._make_request("order", params=params)

    def get_sales(self, page: int = 1, pagesize: int = 100, updated_since: Optional[str] = None) -> Dict:
        """Get sales with pagination and optional timestamp filter"""
        params = {"page": page, "pagesize": pagesize}
        if updated_since:
            params["updated_since"] = updated_since
        return self._make_request("sale", params=params)

    def get_inventory(self, page: int = 1, pagesize: int = 100, updated_since: Optional[str] = None) -> Dict:
        """Get inventory with pagination and optional timestamp filter"""
        params = {"page": page, "pagesize": pagesize}
        if updated_since:
            params["updated_since"] = updated_since
        return self._make_request("inventory", params=params)
        
    # Additional endpoints discovered through testing
    def get_suppliers(self, page: int = 1, pagesize: int = 100, updated_since: Optional[str] = None) -> Dict:
        """Get suppliers with pagination and optional timestamp filter"""
        params = {"page": page, "pagesize": pagesize}
        if updated_since:
            params["updated_since"] = updated_since
        return self._make_request("supplier", params=params)
        
    def get_branches(self, page: int = 1, pagesize: int = 100, updated_since: Optional[str] = None) -> Dict:
        """Get branches with pagination and optional timestamp filter"""
        params = {"page": page, "pagesize": pagesize}
        if updated_since:
            params["updated_since"] = updated_since
        return self._make_request("branch", params=params)
        
    def get_categories(self, page: int = 1, pagesize: int = 100, updated_since: Optional[str] = None) -> Dict:
        """Get categories with pagination and optional timestamp filter"""
        params = {"page": page, "pagesize": pagesize}
        if updated_since:
            params["updated_since"] = updated_since
        return self._make_request("category", params=params)
        
    def get_countries(self, page: int = 1, pagesize: int = 100, updated_since: Optional[str] = None) -> Dict:
        """Get countries with pagination and optional timestamp filter"""
        params = {"page": page, "pagesize": pagesize}
        if updated_since:
            params["updated_since"] = updated_since
        return self._make_request("country", params=params)
        
    def get_credits(self, page: int = 1, pagesize: int = 100, updated_since: Optional[str] = None) -> Dict:
        """Get credits with pagination and optional timestamp filter"""
        params = {"page": page, "pagesize": pagesize}
        if updated_since:
            params["updated_since"] = updated_since
        return self._make_request("credit", params=params)
        
    def get_currencies(self, page: int = 1, pagesize: int = 100, updated_since: Optional[str] = None) -> Dict:
        """Get currencies with pagination and optional timestamp filter"""
        params = {"page": page, "pagesize": pagesize}
        if updated_since:
            params["updated_since"] = updated_since
        return self._make_request("currency", params=params)
        
    def get_invoices(self, page: int = 1, pagesize: int = 100, updated_since: Optional[str] = None) -> Dict:
        """Get invoices with pagination and optional timestamp filter"""
        params = {"page": page, "pagesize": pagesize}
        if updated_since:
            params["updated_since"] = updated_since
        return self._make_request("invoice", params=params)
        
    def get_labels(self, page: int = 1, pagesize: int = 100, updated_since: Optional[str] = None) -> Dict:
        """Get labels with pagination and optional timestamp filter"""
        params = {"page": page, "pagesize": pagesize}
        if updated_since:
            params["updated_since"] = updated_since
        return self._make_request("label", params=params)
        
    def get_payments(self, page: int = 1, pagesize: int = 100, updated_since: Optional[str] = None) -> Dict:
        """Get payments with pagination and optional timestamp filter"""
        params = {"page": page, "pagesize": pagesize}
        if updated_since:
            params["updated_since"] = updated_since
        return self._make_request("payment", params=params)
        
    def get_staff(self, page: int = 1, pagesize: int = 100, updated_since: Optional[str] = None) -> Dict:
        """Get staff with pagination and optional timestamp filter"""
        params = {"page": page, "pagesize": pagesize}
        if updated_since:
            params["updated_since"] = updated_since
        return self._make_request("staff", params=params)
        
    def get_vouchers(self, page: int = 1, pagesize: int = 100, updated_since: Optional[str] = None) -> Dict:
        """Get vouchers with pagination and optional timestamp filter"""
        params = {"page": page, "pagesize": pagesize}
        if updated_since:
            params["updated_since"] = updated_since
        return self._make_request("voucher", params=params)
