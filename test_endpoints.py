#!/usr/bin/env python3
"""
Test script to validate all ProHandel API endpoints and schema validation.
"""
import os
import json
import requests
from dotenv import load_dotenv
import jsonschema

# Load environment variables
load_dotenv()

# Get API credentials from environment variables
api_key = os.environ.get("PROHANDEL_API_KEY")
api_secret = os.environ.get("PROHANDEL_API_SECRET")
auth_url = "https://auth.prohandel.cloud/api/v4"  # Hardcoded for testing
api_url = "https://api.prohandel.de/api/v2"  # Hardcoded for testing

print(f"Auth URL: {auth_url}")
print(f"API URL: {api_url}")

# Authenticate with the ProHandel API
def authenticate():
    """Authenticate with the ProHandel API and get access token."""
    auth_data = {
        "apiKey": api_key,
        "secret": api_secret
    }
    
    print(f"Authenticating with ProHandel API at {auth_url}/token...")
    try:
        response = requests.post(f"{auth_url}/token", json=auth_data)
        response.raise_for_status()
        
        auth_response = response.json()
        print(f"Authentication response status: {response.status_code}")
        
        # Handle different token response formats
        if "token" in auth_response and "token" in auth_response["token"] and "value" in auth_response["token"]["token"]:
            token = auth_response["token"]["token"]["value"]
            print("Token format: token.token.token.value")
            # Also print the server URL from the response
            if "serverUrl" in auth_response:
                print(f"Server URL from response: {auth_response['serverUrl']}")
                global api_url
                api_url = auth_response['serverUrl']
                print(f"Updated API URL to: {api_url}")
        elif "accessToken" in auth_response:
            token = auth_response["accessToken"]
            print("Token format: accessToken")
        else:
            print(f"Unexpected token format in response: {auth_response}")
            return None
        
        print(f"Authentication successful. Token: {token[:10]}...")
        return token
        
    except requests.exceptions.RequestException as e:
        print(f"Authentication failed: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            if e.response.content:
                print(f"Response content: {e.response.content.decode()}")
        return None

# Entity configuration
ENTITY_CONFIG = {
    "article": {
        "endpoint": "/article",
        "schema_path": "etl/validators/schemas/article.json"
    },
    "customer": {
        "endpoint": "/customer",
        "schema_path": "etl/validators/schemas/customer.json"
    },
    "order": {
        "endpoint": "/order",
        "schema_path": "etl/validators/schemas/order.json"
    },
    "sale": {
        "endpoint": "/sale",
        "schema_path": "etl/validators/schemas/sale.json"
    },
    "inventory": {
        "endpoint": "/inventory",
        "schema_path": "etl/validators/schemas/inventory.json"
    },
    "branch": {
        "endpoint": "/branch",
        "schema_path": "etl/validators/schemas/branch.json"
    },
    "supplier": {
        "endpoint": "/supplier",
        "schema_path": "etl/validators/schemas/supplier.json"
    },
    "category": {
        "endpoint": "/category",
        "schema_path": "etl/validators/schemas/category.json"
    },
    "staff": {
        "endpoint": "/staff",
        "schema_path": "etl/validators/schemas/staff.json"
    },
    "shop": {
        "endpoint": "/shop",
        "schema_path": "etl/validators/schemas/shop.json"
    },
    "articlesize": {
        "endpoint": "/articlesize",
        "schema_path": "etl/validators/schemas/articlesize.json"
    },
    "country": {
        "endpoint": "/country",
        "schema_path": "etl/validators/schemas/country.json"
    },
    "currency": {
        "endpoint": "/currency",
        "schema_path": "etl/validators/schemas/currency.json"
    },
    "invoice": {
        "endpoint": "/invoice",
        "schema_path": "etl/validators/schemas/invoice.json"
    },
    "payment": {
        "endpoint": "/payment",
        "schema_path": "etl/validators/schemas/payment.json"
    },
    "season": {
        "endpoint": "/season",
        "schema_path": "etl/validators/schemas/season.json"
    },
    "size": {
        "endpoint": "/size",
        "schema_path": "etl/validators/schemas/size.json"
    },
    "voucher": {
        "endpoint": "/voucher",
        "schema_path": "etl/validators/schemas/voucher.json"
    }
}

# Test an API endpoint with the authentication token
def test_endpoint(token, entity_name):
    """Test an API endpoint with the authentication token."""
    if not token:
        print("No token available. Cannot test endpoint.")
        return False
    
    if entity_name not in ENTITY_CONFIG:
        print(f"Entity {entity_name} not found in configuration.")
        return False
    
    entity_config = ENTITY_CONFIG[entity_name]
    endpoint = entity_config["endpoint"]
    schema_path = entity_config["schema_path"]
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Ensure the API URL includes the version according to documentation
    if not api_url.endswith('/api/v2'):
        url = f"{api_url}/api/v2{endpoint}"
    else:
        url = f"{api_url}{endpoint}"
    
    print(f"\nTesting endpoint: {url}")
    
    try:
        # Add paging parameters as mentioned in the documentation
        params = {"pagesize": 5, "page": 1}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        print(f"Endpoint response status: {response.status_code}")
        print(f"Received {len(data) if isinstance(data, list) else 'non-list'} records")
        
        # Print paging information from headers
        if 'x-page' in response.headers:
            print(f"Page: {response.headers['x-page']}")
        if 'x-pagesize' in response.headers:
            print(f"Page size: {response.headers['x-pagesize']}")
        if 'x-more-pages-available' in response.headers:
            print(f"More pages available: {response.headers['x-more-pages-available']}")
        
        # Validate schema if schema file exists
        if os.path.exists(schema_path):
            print(f"Validating schema using {schema_path}...")
            try:
                with open(schema_path, 'r') as f:
                    schema = json.load(f)
                
                # If data is a list, validate the first item
                if isinstance(data, list) and data:
                    jsonschema.validate(data[0], schema)
                    print("Schema validation successful for the first record.")
                elif not isinstance(data, list):
                    jsonschema.validate(data, schema)
                    print("Schema validation successful.")
                else:
                    print("No data to validate schema.")
                    
            except FileNotFoundError:
                print(f"Schema file not found: {schema_path}")
            except json.JSONDecodeError:
                print(f"Invalid JSON in schema file: {schema_path}")
            except jsonschema.exceptions.ValidationError as e:
                print(f"Schema validation failed: {str(e)}")
                # Print the data that failed validation
                if isinstance(data, list) and data:
                    print(f"First record: {json.dumps(data[0], indent=2)}")
                return False
        else:
            print(f"Schema file not found: {schema_path}. Skipping validation.")
        
        # Print the first record if available
        if isinstance(data, list) and data:
            print(f"First record fields: {list(data[0].keys())}")
            # Save schema to file if it doesn't exist
            if not os.path.exists(schema_path):
                os.makedirs(os.path.dirname(schema_path), exist_ok=True)
                schema = {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": {k: {"type": "string"} for k in data[0].keys()},
                    "required": list(data[0].keys())
                }
                with open(schema_path, 'w') as f:
                    json.dump(schema, f, indent=2)
                print(f"Created schema file: {schema_path}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Endpoint test failed: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            if e.response.content:
                print(f"Response content: {e.response.content.decode()}")
        return False

if __name__ == "__main__":
    # Test authentication
    token = authenticate()
    
    if token:
        # Test all endpoints
        for entity_name in ENTITY_CONFIG.keys():
            success = test_endpoint(token, entity_name)
            print(f"Endpoint {entity_name}: {'SUCCESS' if success else 'FAILED'}")
    else:
        print("Authentication failed. Cannot test endpoints.")
