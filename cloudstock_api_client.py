#!/usr/bin/env python3
"""
CloudStock API Client for ProHandel
A simplified client focused on the core endpoints needed for inventory management:
- Articles (products)
- Inventory (stock levels)
- Sales (historical data)

This client implements the working configuration discovered through testing.
"""

import os
import json
import requests
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables if available
load_dotenv()

class CloudStockAPI:
    """
    CloudStock API Client for ProHandel
    Focused on core inventory management functionality
    """
    
    def __init__(self, api_key=None, api_secret=None):
        """Initialize the API client with credentials"""
        # Use provided credentials or load from environment
        self.api_key = api_key or os.getenv("PROHANDEL_API_KEY", "7e7c639358434c4fa215d4e3978739d0")
        self.api_secret = api_secret or os.getenv("PROHANDEL_API_SECRET", "1cjnuux79d")
        
        # Use the working configuration from our tests
        self.auth_url = os.getenv("PROHANDEL_AUTH_URL", "https://auth.prohandel.cloud/api/v4")
        self.api_url = os.getenv("PROHANDEL_API_URL", "https://linde.prohandel.de/api/v2")
        
        self.access_token = None
        self.token_expiry = None
        self.session = requests.Session()
    
    def authenticate(self) -> str:
        """
        Authenticate with the ProHandel API and get access token
        Returns the token value
        """
        auth_data = {
            "apiKey": self.api_key,
            "secret": self.api_secret
        }
        
        response = self.session.post(f"{self.auth_url}/token", json=auth_data)
        response.raise_for_status()
        
        auth_response = response.json()
        
        # Handle different response formats
        if "token" in auth_response and "value" in auth_response["token"]:
            self.access_token = auth_response["token"]["value"]
        elif "token" in auth_response and isinstance(auth_response["token"], dict) and "token" in auth_response["token"]:
            self.access_token = auth_response["token"]["token"]["value"]
        elif "access_token" in auth_response:
            self.access_token = auth_response["access_token"]
        else:
            raise ValueError(f"Unexpected token format: {json.dumps(auth_response, indent=2)}")
        
        # Set token expiry to now + 1 hour (typical token lifetime)
        self.token_expiry = datetime.now().timestamp() + 3600
        
        return self.access_token
    
    def _ensure_token(self):
        """Ensure we have a valid token"""
        if not self.access_token or (self.token_expiry and datetime.now().timestamp() > self.token_expiry):
            self.authenticate()
    
    def _make_request(self, endpoint: str, params: Dict = None, method: str = "GET") -> Any:
        """Make an authenticated request to the API"""
        self._ensure_token()
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-API-Version": "v2.29.1"
        }
        
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(method, url, headers=headers, params=params)
            
            # Handle token expiration
            if response.status_code == 401:
                self.authenticate()
                return self._make_request(endpoint, params, method)
            
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            # Normalize response format
            if isinstance(data, list):
                return {"data": data}
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response content: {e.response.content.decode()}")
            raise
    
    def get_articles(self, page: int = 1, pagesize: int = 100, updated_since: Optional[str] = None) -> Dict:
        """
        Get product data with pagination and optional timestamp filter
        
        Args:
            page: Page number to retrieve
            pagesize: Number of items per page
            updated_since: ISO timestamp to filter by update date
            
        Returns:
            Dictionary with product data
        """
        params = {"page": page, "pagesize": pagesize}
        if updated_since:
            params["updated_since"] = updated_since
        
        return self._make_request("article", params=params)
    
    def get_inventory(self, page: int = 1, pagesize: int = 100, updated_since: Optional[str] = None) -> Dict:
        """
        Get inventory data with pagination and optional timestamp filter
        
        Args:
            page: Page number to retrieve
            pagesize: Number of items per page
            updated_since: ISO timestamp to filter by update date
            
        Returns:
            Dictionary with inventory data
        """
        params = {"page": page, "pagesize": pagesize}
        if updated_since:
            params["updated_since"] = updated_since
        
        return self._make_request("inventory", params=params)
    
    def get_sales(self, page: int = 1, pagesize: int = 100, updated_since: Optional[str] = None) -> Dict:
        """
        Get sales data with pagination and optional timestamp filter
        
        Args:
            page: Page number to retrieve
            pagesize: Number of items per page
            updated_since: ISO timestamp to filter by update date
            
        Returns:
            Dictionary with sales data
        """
        params = {"page": page, "pagesize": pagesize}
        if updated_since:
            params["updated_since"] = updated_since
        
        return self._make_request("sale", params=params)
    
    def get_all_articles(self, pagesize: int = 100, updated_since: Optional[str] = None) -> List[Dict]:
        """
        Get all articles with pagination handling
        
        Args:
            pagesize: Number of items per page
            updated_since: ISO timestamp to filter by update date
            
        Returns:
            List of all articles
        """
        all_data = []
        page = 1
        more_pages = True
        
        while more_pages:
            response = self.get_articles(page=page, pagesize=pagesize, updated_since=updated_since)
            
            # Extract data based on response format
            if "data" in response:
                data = response["data"]
            else:
                data = response
            
            if not data:
                break
                
            all_data.extend(data)
            
            # Check if there are more pages
            if "meta" in response and "pagination" in response["meta"]:
                pagination = response["meta"]["pagination"]
                if "total_pages" in pagination and page >= pagination["total_pages"]:
                    more_pages = False
                else:
                    page += 1
            elif len(data) < pagesize:
                more_pages = False
            else:
                page += 1
        
        return all_data
    
    def get_all_inventory(self, pagesize: int = 100, updated_since: Optional[str] = None) -> List[Dict]:
        """
        Get all inventory items with pagination handling
        
        Args:
            pagesize: Number of items per page
            updated_since: ISO timestamp to filter by update date
            
        Returns:
            List of all inventory items
        """
        all_data = []
        page = 1
        more_pages = True
        
        while more_pages:
            response = self.get_inventory(page=page, pagesize=pagesize, updated_since=updated_since)
            
            # Extract data based on response format
            if "data" in response:
                data = response["data"]
            else:
                data = response
            
            if not data:
                break
                
            all_data.extend(data)
            
            # Check if there are more pages
            if "meta" in response and "pagination" in response["meta"]:
                pagination = response["meta"]["pagination"]
                if "total_pages" in pagination and page >= pagination["total_pages"]:
                    more_pages = False
                else:
                    page += 1
            elif len(data) < pagesize:
                more_pages = False
            else:
                page += 1
        
        return all_data
    
    def get_all_sales(self, pagesize: int = 100, updated_since: Optional[str] = None) -> List[Dict]:
        """
        Get all sales with pagination handling
        
        Args:
            pagesize: Number of items per page
            updated_since: ISO timestamp to filter by update date
            
        Returns:
            List of all sales
        """
        all_data = []
        page = 1
        more_pages = True
        
        while more_pages:
            response = self.get_sales(page=page, pagesize=pagesize, updated_since=updated_since)
            
            # Extract data based on response format
            if "data" in response:
                data = response["data"]
            else:
                data = response
            
            if not data:
                break
                
            all_data.extend(data)
            
            # Check if there are more pages
            if "meta" in response and "pagination" in response["meta"]:
                pagination = response["meta"]["pagination"]
                if "total_pages" in pagination and page >= pagination["total_pages"]:
                    more_pages = False
                else:
                    page += 1
            elif len(data) < pagesize:
                more_pages = False
            else:
                page += 1
        
        return all_data
    
    def get_stock_status(self) -> List[Dict]:
        """
        Get enhanced stock status with product details
        Combines inventory and article data for a complete view
        
        Returns:
            List of stock items with product details
        """
        # Get all inventory items
        inventory = self.get_all_inventory()
        
        # Get all articles
        articles = self.get_all_articles()
        
        # Create article lookup by ID
        article_lookup = {article.get("id", ""): article for article in articles}
        
        # Combine inventory with article details
        stock_status = []
        for item in inventory:
            article_id = item.get("articleId", "")
            article = article_lookup.get(article_id, {})
            
            # Create enhanced stock item
            stock_item = {
                "inventory_id": item.get("id", ""),
                "article_id": article_id,
                "name": article.get("name", ""),
                "sku": article.get("sku", ""),
                "barcode": article.get("barcode", ""),
                "quantity": item.get("quantity", 0),
                "min_stock_level": item.get("minStockLevel", 0),
                "max_stock_level": item.get("maxStockLevel", 0),
                "reorder_point": item.get("reorderPoint", 0),
                "price": article.get("price", 0),
                "cost": article.get("cost", 0),
                "category": article.get("category", ""),
                "stock_status": self._calculate_stock_status(
                    item.get("quantity", 0),
                    item.get("minStockLevel", 0),
                    item.get("reorderPoint", 0)
                )
            }
            
            stock_status.append(stock_item)
        
        return stock_status
    
    def _calculate_stock_status(self, quantity: float, min_level: float, reorder_point: float) -> str:
        """Calculate stock status based on inventory levels"""
        if quantity <= 0:
            return "out_of_stock"
        elif quantity <= min_level:
            return "critical"
        elif quantity <= reorder_point:
            return "low"
        else:
            return "ok"


def main():
    """Example usage of the CloudStock API client"""
    print("=== CloudStock API Client Example ===")
    
    # Create API client
    api = CloudStockAPI()
    
    try:
        # Authenticate
        print("\nAuthenticating...")
        api.authenticate()
        print("Authentication successful!")
        
        # Get articles example
        print("\nFetching articles (products)...")
        articles = api.get_articles(pagesize=5)
        if "data" in articles:
            print(f"Retrieved {len(articles['data'])} articles")
        else:
            print(f"Retrieved {len(articles)} articles")
        
        # Get inventory example
        print("\nFetching inventory...")
        inventory = api.get_inventory(pagesize=5)
        if "data" in inventory:
            print(f"Retrieved {len(inventory['data'])} inventory items")
        else:
            print(f"Retrieved {len(inventory)} inventory items")
        
        # Get sales example
        print("\nFetching sales...")
        sales = api.get_sales(pagesize=5)
        if "data" in sales:
            print(f"Retrieved {len(sales['data'])} sales")
        else:
            print(f"Retrieved {len(sales)} sales")
        
        # Get enhanced stock status
        print("\nGenerating enhanced stock status...")
        stock_status = api.get_stock_status()
        print(f"Generated stock status for {len(stock_status)} items")
        
        # Print sample stock status
        if stock_status:
            print("\nSample stock status:")
            sample = stock_status[0]
            for key, value in sample.items():
                print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"\nError: {str(e)}")


if __name__ == "__main__":
    main()
