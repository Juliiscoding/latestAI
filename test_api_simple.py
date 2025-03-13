#!/usr/bin/env python3
import sys
import traceback

# Add the enhanced_lambda directory to the path
sys.path.append('./enhanced_lambda')

# Import the ProHandelAPI class
from prohandel_api import ProHandelAPI

def main():
    """Test the ProHandel API methods"""
    api_key = '7e7c639358434c4fa215d4e3978739d0'
    api_secret = '1cjnuux79d'
    
    print("Initializing API client...")
    api = ProHandelAPI(api_key, api_secret)
    
    print("Testing authentication...")
    api.authenticate()
    print("Authentication successful!")
    
    # Test each method directly
    print("\nTesting API methods:")
    
    try:
        print("Testing get_articles...")
        response = api.get_articles(page=1, pagesize=1)
        # Handle both list and dictionary responses
        if isinstance(response, list):
            data_count = len(response)
        else:
            data_count = len(response.get('data', []))
        print(f"  - Success: {data_count} records")
    except Exception as e:
        print(f"  - Error: {str(e)}")
        traceback.print_exc()
    
    try:
        print("Testing get_customers...")
        response = api.get_customers(page=1, pagesize=1)
        # Handle both list and dictionary responses
        if isinstance(response, list):
            data_count = len(response)
        else:
            data_count = len(response.get('data', []))
        print(f"  - Success: {data_count} records")
    except Exception as e:
        print(f"  - Error: {str(e)}")
        traceback.print_exc()
    
    try:
        print("Testing get_countries...")
        response = api.get_countries(page=1, pagesize=1)
        # Handle both list and dictionary responses
        if isinstance(response, list):
            data_count = len(response)
        else:
            data_count = len(response.get('data', []))
        print(f"  - Success: {data_count} records")
    except Exception as e:
        print(f"  - Error: {str(e)}")
        traceback.print_exc()
    
    try:
        print("Testing get_suppliers...")
        response = api.get_suppliers(page=1, pagesize=1)
        # Handle both list and dictionary responses
        if isinstance(response, list):
            data_count = len(response)
        else:
            data_count = len(response.get('data', []))
        print(f"  - Success: {data_count} records")
    except Exception as e:
        print(f"  - Error: {str(e)}")
        traceback.print_exc()
    
    try:
        print("Testing get_branches...")
        response = api.get_branches(page=1, pagesize=1)
        # Handle both list and dictionary responses
        if isinstance(response, list):
            data_count = len(response)
        else:
            data_count = len(response.get('data', []))
        print(f"  - Success: {data_count} records")
    except Exception as e:
        print(f"  - Error: {str(e)}")
        traceback.print_exc()
    
    try:
        print("Testing get_categories...")
        response = api.get_categories(page=1, pagesize=1)
        # Handle both list and dictionary responses
        if isinstance(response, list):
            data_count = len(response)
        else:
            data_count = len(response.get('data', []))
        print(f"  - Success: {data_count} records")
    except Exception as e:
        print(f"  - Error: {str(e)}")
        traceback.print_exc()
    
    try:
        print("Testing get_credits...")
        response = api.get_credits(page=1, pagesize=1)
        # Handle both list and dictionary responses
        if isinstance(response, list):
            data_count = len(response)
        else:
            data_count = len(response.get('data', []))
        print(f"  - Success: {data_count} records")
    except Exception as e:
        print(f"  - Error: {str(e)}")
        traceback.print_exc()
    
    try:
        print("Testing get_currencies...")
        response = api.get_currencies(page=1, pagesize=1)
        # Handle both list and dictionary responses
        if isinstance(response, list):
            data_count = len(response)
        else:
            data_count = len(response.get('data', []))
        print(f"  - Success: {data_count} records")
    except Exception as e:
        print(f"  - Error: {str(e)}")
        traceback.print_exc()
    
    try:
        print("Testing get_invoices...")
        response = api.get_invoices(page=1, pagesize=1)
        # Handle both list and dictionary responses
        if isinstance(response, list):
            data_count = len(response)
        else:
            data_count = len(response.get('data', []))
        print(f"  - Success: {data_count} records")
    except Exception as e:
        print(f"  - Error: {str(e)}")
        traceback.print_exc()
    
    try:
        print("Testing get_labels...")
        response = api.get_labels(page=1, pagesize=1)
        # Handle both list and dictionary responses
        if isinstance(response, list):
            data_count = len(response)
        else:
            data_count = len(response.get('data', []))
        print(f"  - Success: {data_count} records")
    except Exception as e:
        print(f"  - Error: {str(e)}")
        traceback.print_exc()
    
    try:
        print("Testing get_payments...")
        response = api.get_payments(page=1, pagesize=1)
        # Handle both list and dictionary responses
        if isinstance(response, list):
            data_count = len(response)
        else:
            data_count = len(response.get('data', []))
        print(f"  - Success: {data_count} records")
    except Exception as e:
        print(f"  - Error: {str(e)}")
        traceback.print_exc()
    
    try:
        print("Testing get_staff...")
        response = api.get_staff(page=1, pagesize=1)
        # Handle both list and dictionary responses
        if isinstance(response, list):
            data_count = len(response)
        else:
            data_count = len(response.get('data', []))
        print(f"  - Success: {data_count} records")
    except Exception as e:
        print(f"  - Error: {str(e)}")
        traceback.print_exc()
    
    try:
        print("Testing get_vouchers...")
        response = api.get_vouchers(page=1, pagesize=1)
        # Handle both list and dictionary responses
        if isinstance(response, list):
            data_count = len(response)
        else:
            data_count = len(response.get('data', []))
        print(f"  - Success: {data_count} records")
    except Exception as e:
        print(f"  - Error: {str(e)}")
        traceback.print_exc()
    
    # Test core endpoints that were missing
    try:
        print("Testing get_orders...")
        response = api.get_orders(page=1, pagesize=1)
        # Handle both list and dictionary responses
        if isinstance(response, list):
            data_count = len(response)
        else:
            data_count = len(response.get('data', []))
        print(f"  - Success: {data_count} records")
    except Exception as e:
        print(f"  - Error: {str(e)}")
        traceback.print_exc()
    
    try:
        print("Testing get_sales...")
        response = api.get_sales(page=1, pagesize=1)
        # Handle both list and dictionary responses
        if isinstance(response, list):
            data_count = len(response)
        else:
            data_count = len(response.get('data', []))
        print(f"  - Success: {data_count} records")
    except Exception as e:
        print(f"  - Error: {str(e)}")
        traceback.print_exc()
    
    try:
        print("Testing get_inventory...")
        response = api.get_inventory(page=1, pagesize=1)
        # Handle both list and dictionary responses
        if isinstance(response, list):
            data_count = len(response)
        else:
            data_count = len(response.get('data', []))
        print(f"  - Success: {data_count} records")
    except Exception as e:
        print(f"  - Error: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
