#!/usr/bin/env python
"""
ProHandel API Data Explorer

This script fetches data from the ProHandel API, analyzes it, and demonstrates
potential data enhancements that could be implemented in the Lambda function.
"""
import os
import sys
import json
import time
import pandas as pd
import numpy as np
import requests
import argparse
from datetime import datetime, timedelta
from dotenv import load_dotenv
from tabulate import tabulate

# Load environment variables
load_dotenv(override=True)

# API credentials
API_KEY = os.getenv("PROHANDEL_API_KEY")
API_SECRET = os.getenv("PROHANDEL_API_SECRET")
AUTH_URL = os.getenv("PROHANDEL_AUTH_URL", "https://auth.prohandel.cloud/api/v4")
API_URL = os.getenv("PROHANDEL_API_URL", "https://linde.prohandel.de/api/v2")

# Global token storage
TOKEN_INFO = None

def authenticate():
    """Authenticate with the ProHandel API and get an access token."""
    global TOKEN_INFO
    
    # Check if we have a valid token
    if TOKEN_INFO and TOKEN_INFO["expiry"] > datetime.now():
        return TOKEN_INFO["token"]
    
    auth_url = AUTH_URL  # Use the environment variable
    print(f"Authenticating with {auth_url}...")
    
    # Prepare authentication data
    auth_data = {
        "apiKey": API_KEY,
        "secret": API_SECRET
    }
    
    try:
        # Make authentication request
        response = requests.post(f"{auth_url}/token", json=auth_data)
        response.raise_for_status()
        
        # Parse response
        auth_response = response.json()
        
        # Extract token from the correct response structure
        if "token" in auth_response and "token" in auth_response["token"] and "value" in auth_response["token"]["token"]:
            token = auth_response["token"]["token"]["value"]
        elif "accessToken" in auth_response:
            token = auth_response["accessToken"]
        else:
            print(f"Error: Unexpected token format in response: {auth_response}")
            return None
        
        # Get token and expiry
        expires_in = auth_response.get("expiresIn", 3600)  # Default to 1 hour
        expiry = datetime.now() + timedelta(seconds=expires_in)
        
        print(f"Authentication successful! Token expires at {expiry}")
        
        TOKEN_INFO = {
            "token": token,
            "expiry": expiry
        }
        
        return token
    except Exception as e:
        print(f"Authentication failed: {e}")
        return None

def fetch_data(endpoint, params=None, limit=None):
    """Fetch data from the ProHandel API."""
    token = authenticate()
    if not token:
        print("Authentication failed. Exiting.")
        return None
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    all_data = []
    page = 1
    page_size = 100
    
    if params is None:
        params = {}
    
    print(f"Fetching data from {API_URL}/{endpoint}...")
    print(f"  Using URL: {API_URL}/{endpoint}")
    
    try:
        while True:
            # Update pagination parameters
            params.update({"page": page, "pagesize": page_size})
            
            # Make API request
            response = requests.get(f"{API_URL}/{endpoint}", headers=headers, params=params)
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            
            if not data:
                break
            
            all_data.extend(data)
            print(f"  Fetched page {page}, got {len(data)} records, total: {len(all_data)}")
            
            # Check if we've reached the limit
            if limit and len(all_data) >= limit:
                all_data = all_data[:limit]
                break
            
            # Check if we've reached the end
            if len(data) < page_size:
                break
            
            # Next page
            page += 1
            
            # Sleep to avoid rate limiting
            time.sleep(0.5)
    
    except Exception as e:
        print(f"API call failed: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
    
    print(f"Fetched {len(all_data)} records from {endpoint}")
    return all_data

def enhance_article_data(articles):
    """Enhance article data with calculated fields."""
    if not articles:
        return []
    
    enhanced_articles = []
    
    for article in articles:
        # Create a copy of the original article
        enhanced = article.copy()
        
        # Add calculated fields
        
        # 1. Profit margin (if price and cost are available)
        if 'price' in article and 'cost' in article and article['price'] and article['cost']:
            price = float(article['price'])
            cost = float(article['cost'])
            if cost > 0:
                enhanced['profit_margin'] = round((price - cost) / price * 100, 2)
            else:
                enhanced['profit_margin'] = None
        else:
            enhanced['profit_margin'] = None
        
        # 2. Price tier based on price
        if 'price' in article and article['price']:
            price = float(article['price'])
            if price < 10:
                enhanced['price_tier'] = 'Budget'
            elif price < 50:
                enhanced['price_tier'] = 'Standard'
            elif price < 100:
                enhanced['price_tier'] = 'Premium'
            else:
                enhanced['price_tier'] = 'Luxury'
        else:
            enhanced['price_tier'] = None
        
        # 3. Stock level category
        if 'stock' in article and article['stock'] is not None:
            stock = float(article['stock'])
            if stock <= 0:
                enhanced['stock_level'] = 'Out of Stock'
            elif stock < 10:
                enhanced['stock_level'] = 'Low'
            elif stock < 50:
                enhanced['stock_level'] = 'Medium'
            else:
                enhanced['stock_level'] = 'High'
        else:
            enhanced['stock_level'] = None
        
        # 4. Full product name (combining name and variant if available)
        if 'name' in article:
            if 'variant' in article and article['variant']:
                enhanced['full_product_name'] = f"{article['name']} - {article['variant']}"
            else:
                enhanced['full_product_name'] = article['name']
        
        enhanced_articles.append(enhanced)
    
    return enhanced_articles

def enhance_customer_data(customers):
    """Enhance customer data with calculated fields."""
    if not customers:
        return []
    
    enhanced_customers = []
    
    for customer in customers:
        # Create a copy of the original customer
        enhanced = customer.copy()
        
        # Add calculated fields
        
        # 1. Full address
        address_parts = []
        for field in ['street', 'houseNumber', 'postalCode', 'city', 'country']:
            if field in customer and customer[field]:
                address_parts.append(str(customer[field]))
        
        if address_parts:
            enhanced['full_address'] = ', '.join(address_parts)
        else:
            enhanced['full_address'] = None
        
        # 2. Customer type based on business/private
        if 'businessCustomer' in customer:
            enhanced['customer_type'] = 'Business' if customer['businessCustomer'] else 'Private'
        else:
            enhanced['customer_type'] = None
        
        # 3. Full name
        name_parts = []
        for field in ['title', 'firstName', 'lastName']:
            if field in customer and customer[field]:
                name_parts.append(customer[field])
        
        if name_parts:
            enhanced['full_name'] = ' '.join(name_parts)
        else:
            enhanced['full_name'] = None
        
        enhanced_customers.append(enhanced)
    
    return enhanced_customers

def enhance_order_data(orders):
    """Enhance order data with calculated fields."""
    if not orders:
        return []
    
    enhanced_orders = []
    
    for order in orders:
        # Create a copy of the original order
        enhanced = order.copy()
        
        # Add calculated fields
        
        # 1. Order age in days
        if 'orderDate' in order and order['orderDate']:
            try:
                order_date = datetime.fromisoformat(order['orderDate'].replace('Z', '+00:00'))
                enhanced['order_age_days'] = (datetime.now(order_date.tzinfo) - order_date).days
            except (ValueError, TypeError):
                enhanced['order_age_days'] = None
        else:
            enhanced['order_age_days'] = None
        
        # 2. Order status category
        if 'status' in order:
            status = order['status']
            if status in ['COMPLETED', 'DELIVERED']:
                enhanced['status_category'] = 'Completed'
            elif status in ['CANCELLED', 'REJECTED']:
                enhanced['status_category'] = 'Cancelled'
            elif status in ['PENDING', 'PROCESSING']:
                enhanced['status_category'] = 'In Progress'
            else:
                enhanced['status_category'] = 'Other'
        else:
            enhanced['status_category'] = None
        
        # 3. Total order value
        if 'items' in order and order['items']:
            total_value = sum(
                float(item.get('price', 0)) * float(item.get('quantity', 0))
                for item in order['items']
                if 'price' in item and 'quantity' in item
            )
            enhanced['total_order_value'] = round(total_value, 2)
        else:
            enhanced['total_order_value'] = None
        
        # 4. Order size category
        if 'total_order_value' in enhanced and enhanced['total_order_value'] is not None:
            value = enhanced['total_order_value']
            if value < 50:
                enhanced['order_size'] = 'Small'
            elif value < 200:
                enhanced['order_size'] = 'Medium'
            elif value < 500:
                enhanced['order_size'] = 'Large'
            else:
                enhanced['order_size'] = 'Very Large'
        else:
            enhanced['order_size'] = None
        
        enhanced_orders.append(enhanced)
    
    return enhanced_orders

def analyze_data(data, entity_type):
    """Analyze the data and print statistics."""
    if not data:
        print(f"No {entity_type} data to analyze")
        return
    
    print(f"\n--- {entity_type.capitalize()} Data Analysis ---")
    
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(data)
    
    # Print basic statistics
    print(f"Total records: {len(df)}")
    print(f"Columns: {', '.join(df.columns)}")
    
    # Print sample data
    print("\nSample data:")
    print(tabulate(df.head(5).to_dict('records'), headers='keys', tablefmt='pretty'))
    
    # Entity-specific analysis
    if entity_type == 'articles':
        if 'price' in df.columns:
            print("\nPrice statistics:")
            price_stats = df['price'].astype(float).describe()
            print(f"  Min: {price_stats['min']:.2f}")
            print(f"  Max: {price_stats['max']:.2f}")
            print(f"  Mean: {price_stats['mean']:.2f}")
            print(f"  Median: {df['price'].astype(float).median():.2f}")
        
        if 'profit_margin' in df.columns:
            print("\nProfit margin statistics:")
            margin_stats = df['profit_margin'].describe()
            print(f"  Min: {margin_stats['min']:.2f}%")
            print(f"  Max: {margin_stats['max']:.2f}%")
            print(f"  Mean: {margin_stats['mean']:.2f}%")
            print(f"  Median: {df['profit_margin'].median():.2f}%")
        
        if 'stock_level' in df.columns:
            print("\nStock level distribution:")
            stock_counts = df['stock_level'].value_counts()
            for level, count in stock_counts.items():
                print(f"  {level}: {count} ({count/len(df)*100:.1f}%)")
    
    elif entity_type == 'customers':
        if 'customer_type' in df.columns:
            print("\nCustomer type distribution:")
            type_counts = df['customer_type'].value_counts()
            for ctype, count in type_counts.items():
                print(f"  {ctype}: {count} ({count/len(df)*100:.1f}%)")
    
    elif entity_type == 'orders':
        if 'status_category' in df.columns:
            print("\nOrder status distribution:")
            status_counts = df['status_category'].value_counts()
            for status, count in status_counts.items():
                print(f"  {status}: {count} ({count/len(df)*100:.1f}%)")
        
        if 'total_order_value' in df.columns:
            print("\nOrder value statistics:")
            value_stats = df['total_order_value'].describe()
            print(f"  Min: {value_stats['min']:.2f}")
            print(f"  Max: {value_stats['max']:.2f}")
            print(f"  Mean: {value_stats['mean']:.2f}")
            print(f"  Median: {df['total_order_value'].median():.2f}")
        
        if 'order_size' in df.columns:
            print("\nOrder size distribution:")
            size_counts = df['order_size'].value_counts()
            for size, count in size_counts.items():
                print(f"  {size}: {count} ({count/len(df)*100:.1f}%)")

def save_data(data, filename):
    """Save data to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Data saved to {filename}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="ProHandel API Data Explorer")
    parser.add_argument("--entity", choices=["articles", "customers", "orders", "all"], default="all",
                      help="Entity type to fetch and analyze")
    parser.add_argument("--limit", type=int, default=100,
                      help="Maximum number of records to fetch per entity type")
    parser.add_argument("--save", action="store_true",
                      help="Save the fetched data to JSON files")
    parser.add_argument("--enhanced", action="store_true",
                      help="Apply data enhancements")
    
    args = parser.parse_args()
    
    # Print environment variables for debugging
    print(f"AUTH_URL: {AUTH_URL}")
    print(f"API_URL: {API_URL}")
    
    entities = []
    if args.entity == "all":
        entities = ["article", "customer", "order"]
    else:
        # Convert plural to singular for API endpoint
        entity = args.entity[:-1] if args.entity.endswith('s') else args.entity
        entities = [entity]
    
    for entity in entities:
        # Fetch data
        data = fetch_data(entity, limit=args.limit)
        
        if not data:
            continue
        
        # Apply enhancements if requested
        if args.enhanced:
            if entity == "article":
                data = enhance_article_data(data)
            elif entity == "customer":
                data = enhance_customer_data(data)
            elif entity == "order":
                data = enhance_order_data(data)
        
        # Analyze data
        analyze_data(data, f"{entity}s")
        
        # Save data if requested
        if args.save:
            filename = f"{entity}s_data.json"
            if args.enhanced:
                filename = f"{entity}s_enhanced_data.json"
            save_data(data, filename)

if __name__ == "__main__":
    main()
