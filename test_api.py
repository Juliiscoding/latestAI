#!/usr/bin/env python3
import sys
import json
from datetime import datetime

# Add the enhanced_lambda directory to the path
sys.path.append('./enhanced_lambda')

# Import the necessary modules
from prohandel_api import ProHandelAPI
from data_processor import DataProcessor

def test_api_connection():
    """Test the connection to the ProHandel API"""
    api_key = '7e7c639358434c4fa215d4e3978739d0'
    api_secret = '1cjnuux79d'
    
    print("Initializing API client...")
    api = ProHandelAPI(api_key, api_secret)
    
    print("Testing authentication...")
    api.authenticate()
    print("Authentication successful!")
    
    return api

def test_endpoints(api):
    """Test all the available endpoints"""
    print("\nTesting all endpoints with a single record request...")
    
    # Test all endpoints with a small page size
    endpoints = [
        ("articles", api.get_articles),
        ("customers", api.get_customers),
        ("orders", api.get_orders),
        ("sales", api.get_sales),
        ("inventory", api.get_inventory),
        ("suppliers", api.get_suppliers),
        ("branches", api.get_branches),
        ("categories", api.get_categories),
        ("countries", api.get_countries),
        ("credits", api.get_credits),
        ("currencies", api.get_currencies),
        ("invoices", api.get_invoices),
        ("labels", api.get_labels),
        ("payments", api.get_payments),
        ("staff", api.get_staff),
        ("vouchers", api.get_vouchers)
    ]
    
    results = {}
    
    for name, endpoint_func in endpoints:
        try:
            print(f"Testing {name} endpoint...")
            response = endpoint_func(page=1, pagesize=1)
            data_count = len(response.get('data', []))
            status = "Success" if data_count > 0 else "Empty response"
            results[name] = {
                "status": status,
                "count": data_count,
                "sample": response.get('data', [])[0] if data_count > 0 else None
            }
            print(f"  - {status}: Retrieved {data_count} records")
        except Exception as e:
            print(f"  - Error: {str(e)}")
            results[name] = {"status": "Error", "error": str(e)}
    
    return results

def test_data_processor():
    """Test the data processor with all endpoints"""
    api_key = '7e7c639358434c4fa215d4e3978739d0'
    api_secret = '1cjnuux79d'
    
    print("\nInitializing data processor...")
    data_processor = DataProcessor(api_key, api_secret)
    
    print("Testing data processing for all endpoints...")
    
    # Test all processing methods with a small sample
    endpoints = [
        ("articles", data_processor.process_articles),
        ("customers", data_processor.process_customers),
        ("orders", data_processor.process_orders),
        ("sales", data_processor.process_sales),
        ("inventory", data_processor.process_inventory),
        ("suppliers", data_processor.process_suppliers),
        ("branches", data_processor.process_branches),
        ("categories", data_processor.process_categories),
        ("countries", data_processor.process_countries),
        ("credits", data_processor.process_credits),
        ("currencies", data_processor.process_currencies),
        ("invoices", data_processor.process_invoices),
        ("labels", data_processor.process_labels),
        ("payments", data_processor.process_payments),
        ("staff", data_processor.process_staff),
        ("vouchers", data_processor.process_vouchers)
    ]
    
    results = {}
    
    for name, process_func in endpoints:
        try:
            print(f"Processing {name}...")
            # Use a recent timestamp to limit data
            yesterday = (datetime.now()).isoformat()
            
            if name == "orders" or name == "sales":
                # These return a dict with multiple keys
                response = process_func(updated_since=yesterday)
                main_data = response.get(name, [])
                data_count = len(main_data)
                results[name] = {
                    "status": "Success",
                    "count": data_count,
                    "sample": main_data[0] if data_count > 0 else None
                }
            else:
                # These return a list directly
                data = process_func(updated_since=yesterday)
                data_count = len(data)
                results[name] = {
                    "status": "Success",
                    "count": data_count,
                    "sample": data[0] if data_count > 0 else None
                }
            
            print(f"  - Success: Processed {data_count} records")
        except Exception as e:
            print(f"  - Error: {str(e)}")
            results[name] = {"status": "Error", "error": str(e)}
    
    return results

if __name__ == "__main__":
    print("=== ProHandel API Integration Test ===")
    
    try:
        # Test API connection
        api = test_api_connection()
        
        # Test all endpoints
        endpoint_results = test_endpoints(api)
        
        # Test data processor
        processor_results = test_data_processor()
        
        # Save results to a file
        with open('test_results.json', 'w') as f:
            json.dump({
                "endpoint_tests": endpoint_results,
                "processor_tests": processor_results,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)
        
        print("\n=== Test completed successfully ===")
        print("Results saved to test_results.json")
        
    except Exception as e:
        print(f"\n!!! Test failed: {str(e)}")
