import json
import os
from prohandel_api import ProHandelAPI
from datetime import datetime, timedelta

def fetch_and_save_data():
    """Fetch data from all available endpoints and save to JSON files"""
    # Initialize API client
    api = ProHandelAPI(
        api_key="7e7c639358434c4fa215d4e3978739d0",
        api_secret="1cjnuux79d"
    )
    
    # Create data directory if it doesn't exist
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Define date ranges for time-based queries
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)  # Last 30 days
    
    # Dictionary to store sample data from each endpoint
    endpoint_data = {}
    
    # 1. Articles
    print("Fetching articles data...")
    try:
        articles = api.get_articles()
        endpoint_data["articles"] = articles
        with open(f"{data_dir}/articles.json", "w") as f:
            json.dump(articles, f, indent=2)
        print(f"✓ Saved {len(articles)} articles")
    except Exception as e:
        print(f"✗ Error fetching articles: {str(e)}")
    
    # 2. Customers
    print("Fetching customers data...")
    try:
        customers = api.get_customers()
        endpoint_data["customers"] = customers
        with open(f"{data_dir}/customers.json", "w") as f:
            json.dump(customers, f, indent=2)
        print(f"✓ Saved {len(customers)} customers")
    except Exception as e:
        print(f"✗ Error fetching customers: {str(e)}")
    
    # 3. Orders
    print("Fetching orders data...")
    try:
        orders = api.get_orders()
        endpoint_data["orders"] = orders
        with open(f"{data_dir}/orders.json", "w") as f:
            json.dump(orders, f, indent=2)
        print(f"✓ Saved {len(orders)} orders")
    except Exception as e:
        print(f"✗ Error fetching orders: {str(e)}")
    
    # 4. Sales
    print("Fetching sales data...")
    try:
        sales = api.get_sales()
        endpoint_data["sales"] = sales
        with open(f"{data_dir}/sales.json", "w") as f:
            json.dump(sales, f, indent=2)
        print(f"✓ Saved {len(sales)} sales")
    except Exception as e:
        print(f"✗ Error fetching sales: {str(e)}")
    
    # 5. Inventory
    print("Fetching inventory data...")
    try:
        inventory = api.get_inventory()
        endpoint_data["inventory"] = inventory
        with open(f"{data_dir}/inventory.json", "w") as f:
            json.dump(inventory, f, indent=2)
        print(f"✓ Saved {len(inventory)} inventory items")
    except Exception as e:
        print(f"✗ Error fetching inventory: {str(e)}")
    
    # 6. Customer Cards
    print("Fetching customer cards data...")
    try:
        customer_cards = api.get_customer_cards()
        endpoint_data["customer_cards"] = customer_cards
        with open(f"{data_dir}/customer_cards.json", "w") as f:
            json.dump(customer_cards, f, indent=2)
        print(f"✓ Saved {len(customer_cards)} customer cards")
    except Exception as e:
        print(f"✗ Error fetching customer cards: {str(e)}")
    
    # 7. Suppliers
    print("Fetching suppliers data...")
    try:
        suppliers = api.get_suppliers()
        endpoint_data["suppliers"] = suppliers
        with open(f"{data_dir}/suppliers.json", "w") as f:
            json.dump(suppliers, f, indent=2)
        print(f"✓ Saved {len(suppliers)} suppliers")
    except Exception as e:
        print(f"✗ Error fetching suppliers: {str(e)}")
    
    # 8. Branches
    print("Fetching branches data...")
    try:
        branches = api.get_branches()
        endpoint_data["branches"] = branches
        with open(f"{data_dir}/branches.json", "w") as f:
            json.dump(branches, f, indent=2)
        print(f"✓ Saved {len(branches)} branches")
    except Exception as e:
        print(f"✗ Error fetching branches: {str(e)}")
    
    # 9. Categories
    print("Fetching categories data...")
    try:
        categories = api.get_categories()
        endpoint_data["categories"] = categories
        with open(f"{data_dir}/categories.json", "w") as f:
            json.dump(categories, f, indent=2)
        print(f"✓ Saved {len(categories)} categories")
    except Exception as e:
        print(f"✗ Error fetching categories: {str(e)}")
    
    # 10. Vouchers
    print("Fetching vouchers data...")
    try:
        vouchers = api.get_vouchers()
        endpoint_data["vouchers"] = vouchers
        with open(f"{data_dir}/vouchers.json", "w") as f:
            json.dump(vouchers, f, indent=2)
        print(f"✓ Saved {len(vouchers)} vouchers")
    except Exception as e:
        print(f"✗ Error fetching vouchers: {str(e)}")
    
    # 11. Invoices
    print("Fetching invoices data...")
    try:
        invoices = api.get_invoices()
        endpoint_data["invoices"] = invoices
        with open(f"{data_dir}/invoices.json", "w") as f:
            json.dump(invoices, f, indent=2)
        print(f"✓ Saved {len(invoices)} invoices")
    except Exception as e:
        print(f"✗ Error fetching invoices: {str(e)}")
    
    # 12. Payments
    print("Fetching payments data...")
    try:
        payments = api.get_payments()
        endpoint_data["payments"] = payments
        with open(f"{data_dir}/payments.json", "w") as f:
            json.dump(payments, f, indent=2)
        print(f"✓ Saved {len(payments)} payments")
    except Exception as e:
        print(f"✗ Error fetching payments: {str(e)}")
    
    print("\nData fetching complete!")
    return endpoint_data

if __name__ == "__main__":
    fetch_and_save_data()
