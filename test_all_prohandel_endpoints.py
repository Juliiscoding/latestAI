"""
Test all ProHandel API endpoints
This script tests all 54 potential ProHandel API endpoints to see which ones return usable data
"""
import os
import json
import requests
import traceback
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Load environment variables
load_dotenv()

# API credentials
API_KEY = os.environ.get('PROHANDEL_API_KEY', '7e7c639358434c4fa215d4e3978739d0')
API_SECRET = os.environ.get('PROHANDEL_API_SECRET', '1cjnuux79d')
AUTH_URL = os.environ.get('PROHANDEL_AUTH_URL', 'https://auth.prohandel.cloud/api/v4')
API_URL = os.environ.get('PROHANDEL_API_URL', 'https://linde.prohandel.de/api/v2')

# List of all potential endpoints to test
ENDPOINTS = [
    # Core data endpoints
    "article", "customer", "order", "sale", "inventory",
    
    # Additional potential endpoints
    "supplier", "branch", "category", "manufacturer", "brand",
    "staff", "user", "role", "permission", "setting",
    "payment", "invoice", "credit", "debit", "refund",
    "shipping", "delivery", "return", "exchange", "warranty",
    "discount", "promotion", "coupon", "voucher", "gift-card",
    "tax", "currency", "country", "region", "city",
    "address", "contact", "email", "phone", "social",
    "report", "statistic", "dashboard", "analytics", "metric",
    "notification", "message", "comment", "review", "rating",
    "tag", "label", "attribute", "property", "option",
    "image", "file", "document", "attachment", "media"
]

def authenticate():
    """Authenticate with the ProHandel API and get access token"""
    try:
        auth_data = {
            "apiKey": API_KEY,
            "secret": API_SECRET
        }
        
        print("Authenticating with ProHandel API...")
        response = requests.post(f"{AUTH_URL}/token", json=auth_data)
        response.raise_for_status()
        
        auth_response = response.json()
        token = auth_response["token"]["token"]["value"]
        print(f"Authentication successful! Token: {token[:10]}...")
        return token
    except Exception as e:
        print(f"Authentication failed: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            if e.response.content:
                print(f"Response content: {e.response.content.decode()}")
        raise

def test_endpoint(endpoint, access_token):
    """Test a specific API endpoint and return results"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-API-Version": "v2.29.1"
    }
    
    params = {
        "page": 1,
        "pagesize": 5
    }
    
    # URL patterns to try
    url_patterns = [
        f"{API_URL}/{endpoint}",
        f"https://linde.prohandel.de/api/v2/{endpoint}",
        f"{API_URL}/v2/{endpoint}",
        f"{API_URL}/api/v2/{endpoint}",
        f"{API_URL}/v2.29.1/{endpoint}"
    ]
    
    result = {
        "endpoint": endpoint,
        "status": "FAILED",
        "url": "",
        "status_code": 0,
        "data_count": 0,
        "sample": None,
        "error": None,
        "headers": None
    }
    
    for url in url_patterns:
        try:
            print(f"Testing endpoint: {endpoint} at URL: {url}")
            response = requests.get(url, headers=headers, params=params)
            
            result["url"] = url
            result["status_code"] = response.status_code
            
            if response.status_code == 200:
                data = response.json()
                result["status"] = "SUCCESS"
                result["headers"] = dict(response.headers)
                
                # Process the data based on its structure
                if isinstance(data, list):
                    result["data_count"] = len(data)
                    if data:
                        result["sample"] = data[0]
                elif isinstance(data, dict):
                    if 'data' in data:
                        items = data['data']
                        if isinstance(items, list):
                            result["data_count"] = len(items)
                            if items:
                                result["sample"] = items[0]
                    else:
                        result["data_count"] = 1
                        result["sample"] = data
                
                # We found a working URL, no need to try others
                break
        except Exception as e:
            result["error"] = str(e)
            # Continue trying other URL patterns
    
    return result

def main():
    """Main function to test all endpoints"""
    try:
        # Authenticate
        access_token = authenticate()
        
        # Create results directory
        os.makedirs("results", exist_ok=True)
        
        # Timestamp for the results file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"results/prohandel_endpoints_{timestamp}.json"
        
        # Test all endpoints
        results = []
        
        # Use ThreadPoolExecutor for parallel testing
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_endpoint = {executor.submit(test_endpoint, endpoint, access_token): endpoint for endpoint in ENDPOINTS}
            
            for future in as_completed(future_to_endpoint):
                endpoint = future_to_endpoint[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Print result summary
                    status_emoji = "✅" if result["status"] == "SUCCESS" else "❌"
                    print(f"{status_emoji} {endpoint}: {result['status']} - {result['status_code']} - Items: {result['data_count']}")
                    
                except Exception as e:
                    print(f"❌ {endpoint}: Error - {str(e)}")
                    results.append({
                        "endpoint": endpoint,
                        "status": "ERROR",
                        "error": str(e)
                    })
        
        # Sort results by status (SUCCESS first) and then by endpoint name
        results.sort(key=lambda x: (0 if x["status"] == "SUCCESS" else 1, x["endpoint"]))
        
        # Save results to file
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Print summary
        success_count = sum(1 for r in results if r["status"] == "SUCCESS")
        print(f"\n=== SUMMARY ===")
        print(f"Total endpoints tested: {len(ENDPOINTS)}")
        print(f"Successful endpoints: {success_count}")
        print(f"Failed endpoints: {len(ENDPOINTS) - success_count}")
        print(f"Results saved to: {results_file}")
        
        # Print list of successful endpoints
        print("\n=== SUCCESSFUL ENDPOINTS ===")
        for result in results:
            if result["status"] == "SUCCESS":
                print(f"- {result['endpoint']}: {result['data_count']} items")
        
    except Exception as e:
        print(f"Error in main: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
