import requests
from typing import Optional, Dict, Any, List
from datetime import datetime
import json

class ProHandelAPI:
    def __init__(self, api_key: str, api_secret: str):
        self.auth_url = "https://auth.prohandel.cloud/api/v4"
        self.api_url = "https://linde.prohandel.de/api/v2"
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
        
        # List of URL patterns to try
        url_patterns = [
            f"{self.api_url}/{endpoint.lstrip('/')}",                  # Standard pattern
            f"{self.api_url}/v2/{endpoint.lstrip('/')}",              # With v2 prefix
            f"{self.api_url}/api/v2/{endpoint.lstrip('/')}",          # With api/v2 prefix
            f"{self.api_url}/v2.29.1/{endpoint.lstrip('/')}",         # With version number
            f"https://linde.prohandel.de/api/v2/{endpoint.lstrip('/')}"  # Full URL with v2
        ]
        
        last_exception = None
        for url in url_patterns:
            try:
                print(f"\nTrying URL: {url}")
                response = self.session.request(method, url, headers=headers, params=params, json=data)
                response.raise_for_status()
                return response.json() if response.content else None
            except requests.exceptions.RequestException as e:
                print(f"Response: {e.response.status_code if hasattr(e, 'response') else 'Error'}")
                last_exception = e
                continue
                
        raise last_exception

    # Customer endpoints
    def get_customers(self, page: int = 1, pagesize: int = 1000) -> List[Dict]:
        """Get customers with pagination"""
        return self._make_request("customer", params={"page": page, "pagesize": pagesize})

    def get_customer(self, customer_id: str) -> Dict:
        """Get a specific customer by ID"""
        return self._make_request(f"customer/{customer_id}")

    # Article endpoints
    def get_articles(self, page: int = 1, pagesize: int = 1000) -> List[Dict]:
        """Get articles with pagination"""
        return self._make_request("article", params={"page": page, "pagesize": pagesize})

    def get_article(self, article_id: str) -> Dict:
        """Get a specific article by ID"""
        return self._make_request(f"article/{article_id}")

    # Order endpoints
    def get_orders(self, page: int = 1, pagesize: int = 1000) -> List[Dict]:
        """Get orders with pagination"""
        return self._make_request("order", params={"page": page, "pagesize": pagesize})

    def get_order(self, order_id: str) -> Dict:
        """Get a specific order by ID"""
        return self._make_request(f"order/{order_id}")

    # Sale endpoints
    def get_sales(self, page: int = 1, pagesize: int = 1000) -> List[Dict]:
        """Get sales with pagination"""
        return self._make_request("sale", params={"page": page, "pagesize": pagesize})

    def get_sale(self, sale_id: str) -> Dict:
        """Get a specific sale by ID"""
        return self._make_request(f"sale/{sale_id}")

    # Inventory endpoints
    def get_inventory(self, page: int = 1, pagesize: int = 1000) -> List[Dict]:
        """Get inventory with pagination"""
        return self._make_request("inventory", params={"page": page, "pagesize": pagesize})

    def get_inventory_item(self, inventory_id: str) -> Dict:
        """Get a specific inventory item by ID"""
        return self._make_request(f"inventory/{inventory_id}")

    # Customer card endpoints
    def get_customer_cards(self, page: int = 1, pagesize: int = 1000) -> List[Dict]:
        """Get customer cards with pagination"""
        return self._make_request("customercard", params={"page": page, "pagesize": pagesize})

    def get_customer_card(self, card_id: str) -> Dict:
        """Get a specific customer card by ID"""
        return self._make_request(f"customercard/{card_id}")

    # Supplier endpoints
    def get_suppliers(self, page: int = 1, pagesize: int = 1000) -> List[Dict]:
        """Get suppliers with pagination"""
        return self._make_request("supplier", params={"page": page, "pagesize": pagesize})

    def get_supplier(self, supplier_id: str) -> Dict:
        """Get a specific supplier by ID"""
        return self._make_request(f"supplier/{supplier_id}")

    # Branch endpoints
    def get_branches(self, page: int = 1, pagesize: int = 1000) -> List[Dict]:
        """Get branches with pagination"""
        return self._make_request("branch", params={"page": page, "pagesize": pagesize})

    def get_branch(self, branch_id: str) -> Dict:
        """Get a specific branch by ID"""
        return self._make_request(f"branch/{branch_id}")

    # Category endpoints
    def get_categories(self, page: int = 1, pagesize: int = 1000) -> List[Dict]:
        """Get categories with pagination"""
        return self._make_request("category", params={"page": page, "pagesize": pagesize})

    def get_category(self, category_id: str) -> Dict:
        """Get a specific category by ID"""
        return self._make_request(f"category/{category_id}")

    # Voucher endpoints
    def get_vouchers(self, page: int = 1, pagesize: int = 1000) -> List[Dict]:
        """Get vouchers with pagination"""
        return self._make_request("voucher", params={"page": page, "pagesize": pagesize})

    def get_voucher(self, voucher_id: str) -> Dict:
        """Get a specific voucher by ID"""
        return self._make_request(f"voucher/{voucher_id}")

    # Invoice endpoints
    def get_invoices(self, page: int = 1, pagesize: int = 1000) -> List[Dict]:
        """Get invoices with pagination"""
        return self._make_request("invoice", params={"page": page, "pagesize": pagesize})

    def get_invoice(self, invoice_id: str) -> Dict:
        """Get a specific invoice by ID"""
        return self._make_request(f"invoice/{invoice_id}")

    # Payment endpoints
    def get_payments(self, page: int = 1, pagesize: int = 1000) -> List[Dict]:
        """Get payments with pagination"""
        return self._make_request("payment", params={"page": page, "pagesize": pagesize})

    def get_payment(self, payment_id: str) -> Dict:
        """Get a specific payment by ID"""
        return self._make_request(f"payment/{payment_id}")

    # Test all available endpoints and return their status
    def test_endpoints(self):
        """Test all available endpoints and return their status"""
        endpoints = [
            # Core business endpoints
            ("article", "Articles"),
            ("customer", "Customers"),
            ("order", "Orders"),
            ("sale", "Sales"),
            ("inventory", "Inventory"),
            ("customercard", "Customer Cards"),
            ("supplier", "Suppliers"),
            
            # User and access management
            ("employee", "Employees"),
            ("user", "Users"),
            ("role", "Roles"),
            ("permission", "Permissions"),
            
            # Location and organization
            ("warehouse", "Warehouses"),
            ("branch", "Branches"),
            ("store", "Stores"),
            ("location", "Locations"),
            
            # Product management
            ("product", "Products"),
            ("category", "Categories"),
            ("brand", "Brands"),
            ("manufacturer", "Manufacturers"),
            
            # Pricing and discounts
            ("price", "Prices"),
            ("discount", "Discounts"),
            ("promotion", "Promotions"),
            ("voucher", "Vouchers"),
            
            # Stock management
            ("stock", "Stock"),
            ("stocktaking", "Stock Taking"),
            ("stockmovement", "Stock Movements"),
            ("delivery", "Deliveries"),
            
            # Financial
            ("invoice", "Invoices"),
            ("payment", "Payments"),
            ("transaction", "Transactions"),
            ("receipt", "Receipts"),
            
            # Customer related
            ("customergroup", "Customer Groups"),
            ("customersegment", "Customer Segments"),
            ("loyalty", "Loyalty Program"),
            ("bonus", "Bonus Points"),
            
            # Reporting
            ("report", "Reports"),
            ("statistic", "Statistics"),
            ("analytics", "Analytics"),
            
            # Settings and configuration
            ("setting", "Settings"),
            ("configuration", "Configurations"),
            ("parameter", "Parameters"),
            
            # Additional business endpoints
            ("return", "Returns"),
            ("refund", "Refunds"),
            ("reservation", "Reservations"),
            ("appointment", "Appointments"),
            ("service", "Services"),
            ("repair", "Repairs"),
            
            # Communication
            ("message", "Messages"),
            ("notification", "Notifications"),
            ("email", "Emails"),
            ("newsletter", "Newsletters"),
            
            # Documents
            ("document", "Documents"),
            ("attachment", "Attachments"),
            ("file", "Files"),
            
            # Marketing
            ("campaign", "Campaigns"),
            ("marketing", "Marketing"),
            ("advertisement", "Advertisements")
        ]
        
        results = []
        print("\nTesting all possible endpoints...")
        print("-" * 60)
        
        for endpoint, name in endpoints:
            try:
                response = self._make_request(endpoint, params={"page": 1, "pagesize": 1})
                status = "Available"
                if isinstance(response, list):
                    count = len(response)
                    status += f" (Retrieved {count} items)"
                elif isinstance(response, dict):
                    status += " (Single object endpoint)"
                print(f"✓ {name:<25} ({endpoint}): {status}")
                
            except requests.exceptions.RequestException as e:
                status = f"Not available ({e.response.status_code if hasattr(e, 'response') else 'Error'})"
                print(f"✗ {name:<25} ({endpoint}): {status}")
            
            results.append({"Endpoint": endpoint, "Name": name, "Status": status})
        
        # Summarize results
        available = [r for r in results if "Available" in r["Status"]]
        unavailable = [r for r in results if "Not available" in r["Status"]]
        
        print("\nSummary:")
        print("-" * 60)
        print(f"Total endpoints tested: {len(results)}")
        print(f"Available endpoints: {len(available)}")
        print(f"Unavailable endpoints: {len(unavailable)}")
        
        if available:
            print("\nAvailable Endpoints:")
            print("-" * 60)
            for r in available:
                print(f"{r['Name']:<25} ({r['Endpoint']}): {r['Status']}")
        
        return results

# Example usage
if __name__ == "__main__":
    # Initialize the API client with your credentials
    api = ProHandelAPI(
        api_key="7e7c639358434c4fa215d4e3978739d0",
        api_secret="1cjnuux79d"
    )
    
    try:
        print("\nTesting available endpoints...")
        results = api.test_endpoints()
        
        print("\nEndpoint Status Summary:")
        print("-" * 60)
        for result in results:
            print(f"{result['Name']:<20} ({result['Endpoint']}): {result['Status']}")
        
    except Exception as e:
        print("Error:", str(e))
