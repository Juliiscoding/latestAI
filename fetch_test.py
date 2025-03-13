from prohandel_api import ProHandelAPI
import json

def test_fetch_data():
    # Initialize the API client with credentials
    api = ProHandelAPI(
        api_key="7e7c639358434c4fa215d4e3978739d0",
        api_secret="1cjnuux79d"
    )
    
    # List of working endpoints based on previous test
    working_endpoints = [
        ("article", api.get_articles),
        ("customer", api.get_customers),
        ("order", api.get_orders),
        ("sale", api.get_sales),
        ("inventory", api.get_inventory),
        ("customercard", api.get_customer_cards),
        ("supplier", api.get_suppliers),
        ("branch", api.get_branches),
        ("category", api.get_categories),
        ("voucher", api.get_vouchers),
        ("invoice", api.get_invoices),
        ("payment", api.get_payments)
    ]
    
    # Test each endpoint and print results
    print("\nFetching data from working endpoints...")
    print("-" * 60)
    
    results = {}
    
    for name, func in working_endpoints:
        print(f"\nTesting {name} endpoint:")
        try:
            data = func(page=1, pagesize=5)  # Limit to 5 items for testing
            count = len(data) if isinstance(data, list) else 1
            print(f"✓ Successfully fetched {count} items")
            
            # Save a sample of the data structure
            if isinstance(data, list) and data:
                sample = data[0]
            else:
                sample = data
                
            # Store results
            results[name] = {
                "status": "Success",
                "count": count,
                "sample": sample
            }
            
            # Print a sample of the data structure
            print(f"Sample data structure:")
            print(json.dumps(sample, indent=2, default=str)[:500] + "..." if len(json.dumps(sample, default=str)) > 500 else json.dumps(sample, indent=2, default=str))
            
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            results[name] = {
                "status": "Error",
                "error": str(e)
            }
    
    # Print summary
    print("\nSummary:")
    print("-" * 60)
    for name, result in results.items():
        status = result["status"]
        if status == "Success":
            print(f"✓ {name}: {status} (Retrieved {result['count']} items)")
        else:
            print(f"✗ {name}: {status} - {result.get('error', 'Unknown error')}")
    
    return results

if __name__ == "__main__":
    test_fetch_data()
