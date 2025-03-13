#!/usr/bin/env python
"""
Script to monitor data quality for all ProHandel entities.
This script will fetch data from the ProHandel API and run data quality checks.
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from etl.utils.auth import TokenManager
from etl.utils.api_connector import ProHandelConnector
from etl.monitoring.data_quality import monitor_entity_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"data_quality_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger(__name__)

# Entity configuration with field types
ENTITY_CONFIG = {
    "article": {
        "endpoint": "/articles",
        "numeric_fields": ["price", "cost", "stock", "min_stock", "max_stock", "weight"],
        "date_fields": ["created_at", "updated_at", "last_sold_at"],
        "categorical_fields": ["status", "category_id", "supplier_id", "tax_class"]
    },
    "customer": {
        "endpoint": "/customers",
        "numeric_fields": ["discount", "credit_limit", "balance"],
        "date_fields": ["created_at", "updated_at", "last_order_at", "birthday"],
        "categorical_fields": ["status", "customer_group", "payment_terms", "country"]
    },
    "order": {
        "endpoint": "/orders",
        "numeric_fields": ["total_amount", "tax_amount", "discount_amount", "shipping_cost"],
        "date_fields": ["created_at", "updated_at", "order_date", "delivery_date"],
        "categorical_fields": ["status", "payment_status", "shipping_method", "customer_id"]
    },
    "orderposition": {
        "endpoint": "/order-positions",
        "numeric_fields": ["quantity", "price", "discount", "tax_rate", "total"],
        "date_fields": ["created_at", "updated_at"],
        "categorical_fields": ["order_id", "article_id", "status"]
    },
    "inventory": {
        "endpoint": "/inventory",
        "numeric_fields": ["quantity", "min_quantity", "max_quantity", "reorder_point"],
        "date_fields": ["created_at", "updated_at", "last_count_at"],
        "categorical_fields": ["article_id", "warehouse_id", "status"]
    },
    "customercard": {
        "endpoint": "/customer-cards",
        "numeric_fields": ["balance", "points"],
        "date_fields": ["created_at", "updated_at", "expiry_date", "last_used_at"],
        "categorical_fields": ["customer_id", "status", "card_type"]
    },
    "supplier": {
        "endpoint": "/suppliers",
        "numeric_fields": ["credit_limit", "payment_terms_days"],
        "date_fields": ["created_at", "updated_at", "last_order_at"],
        "categorical_fields": ["status", "country", "payment_method"]
    },
    "branch": {
        "endpoint": "/branches",
        "numeric_fields": ["sales_target", "employee_count"],
        "date_fields": ["created_at", "updated_at", "opening_date"],
        "categorical_fields": ["status", "region", "type"]
    },
    "category": {
        "endpoint": "/categories",
        "numeric_fields": ["sort_order", "product_count"],
        "date_fields": ["created_at", "updated_at"],
        "categorical_fields": ["parent_id", "status"]
    },
    "voucher": {
        "endpoint": "/vouchers",
        "numeric_fields": ["amount", "min_order_value", "usage_count", "max_usage_count"],
        "date_fields": ["created_at", "updated_at", "valid_from", "valid_to"],
        "categorical_fields": ["type", "status", "customer_id"]
    },
    "invoice": {
        "endpoint": "/invoices",
        "numeric_fields": ["total_amount", "tax_amount", "discount_amount", "paid_amount"],
        "date_fields": ["created_at", "updated_at", "invoice_date", "due_date", "paid_at"],
        "categorical_fields": ["status", "order_id", "customer_id", "payment_method"]
    },
    "payment": {
        "endpoint": "/payments",
        "numeric_fields": ["amount", "fee_amount"],
        "date_fields": ["created_at", "updated_at", "payment_date", "processed_at"],
        "categorical_fields": ["status", "payment_method", "invoice_id", "customer_id"]
    }
}

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Monitor data quality for ProHandel entities')
    parser.add_argument('--entity', type=str, help='Specific entity to monitor (default: all)')
    parser.add_argument('--output-dir', type=str, default='./data_quality_reports',
                        help='Directory to save data quality reports')
    parser.add_argument('--limit', type=int, default=1000,
                        help='Maximum number of records to fetch per entity')
    parser.add_argument('--auth-url', type=str, 
                        default=os.environ.get('PROHANDEL_AUTH_URL', 'https://auth.prohandel.cloud/api/v4'),
                        help='ProHandel authentication URL')
    parser.add_argument('--api-url', type=str, 
                        default=os.environ.get('PROHANDEL_API_URL', 'https://api.prohandel.cloud/api/v4'),
                        help='ProHandel API URL')
    parser.add_argument('--api-key', type=str, 
                        default=os.environ.get('PROHANDEL_API_KEY'),
                        help='ProHandel API key')
    parser.add_argument('--api-secret', type=str, 
                        default=os.environ.get('PROHANDEL_API_SECRET'),
                        help='ProHandel API secret')
    return parser.parse_args()

def main():
    """Main function to run data quality monitoring."""
    args = parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Check if API credentials are provided
    if not args.api_key or not args.api_secret:
        logger.error("API key and secret are required. Set them as environment variables or provide them as arguments.")
        sys.exit(1)
    
    # Initialize token manager and API connector
    token_manager = TokenManager(
        auth_url=args.auth_url,
        api_key=args.api_key,
        api_secret=args.api_secret
    )
    
    connector = ProHandelConnector(
        api_url=args.api_url,
        token_manager=token_manager
    )
    
    # Determine which entities to monitor
    entities_to_monitor = [args.entity] if args.entity else ENTITY_CONFIG.keys()
    
    # Monitor each entity
    for entity_name in entities_to_monitor:
        if entity_name not in ENTITY_CONFIG:
            logger.warning(f"Unknown entity: {entity_name}. Skipping.")
            continue
        
        logger.info(f"Monitoring data quality for entity: {entity_name}")
        
        try:
            # Fetch data from API
            endpoint = ENTITY_CONFIG[entity_name]["endpoint"]
            params = {"limit": args.limit}
            
            logger.info(f"Fetching data from {endpoint} with limit {args.limit}")
            data = connector.get_data(endpoint, params)
            
            if not data:
                logger.warning(f"No data returned for {entity_name}")
                continue
            
            logger.info(f"Fetched {len(data)} records for {entity_name}")
            
            # Define output path for this entity
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(args.output_dir, f"{entity_name}_quality_{timestamp}.json")
            
            # Monitor data quality
            metrics = monitor_entity_data(
                entity_name=entity_name,
                data=data,
                numeric_fields=ENTITY_CONFIG[entity_name].get("numeric_fields"),
                date_fields=ENTITY_CONFIG[entity_name].get("date_fields"),
                categorical_fields=ENTITY_CONFIG[entity_name].get("categorical_fields"),
                output_path=output_path
            )
            
            logger.info(f"Data quality monitoring completed for {entity_name}")
            
            # Generate summary report
            summary_path = os.path.join(args.output_dir, f"{entity_name}_summary_{timestamp}.md")
            with open(summary_path, 'w') as f:
                f.write(f"# Data Quality Summary for {entity_name}\n\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n\n")
                f.write(f"Records analyzed: {len(data)}\n\n")
                
                # Add completeness summary
                if f"{entity_name}_completeness" in metrics:
                    f.write("## Data Completeness\n\n")
                    f.write("| Field | Completeness % | Null Count |\n")
                    f.write("|-------|---------------|------------|\n")
                    
                    for field, stats in metrics[f"{entity_name}_completeness"]["fields"].items():
                        f.write(f"| {field} | {stats['completeness_pct']}% | {stats['null_count']} |\n")
                    
                    f.write("\n")
                
                # Add anomaly summary if available
                if f"{entity_name}_anomalies" in metrics:
                    f.write("## Data Anomalies\n\n")
                    f.write("| Field | Anomaly Count | Anomaly % |\n")
                    f.write("|-------|--------------|----------|\n")
                    
                    for field, stats in metrics[f"{entity_name}_anomalies"]["fields"].items():
                        f.write(f"| {field} | {stats['anomaly_count']} | {stats['anomaly_pct']}% |\n")
                    
                    f.write("\n")
            
            logger.info(f"Summary report saved to {summary_path}")
            
        except Exception as e:
            logger.error(f"Error monitoring {entity_name}: {str(e)}", exc_info=True)
    
    logger.info("Data quality monitoring completed for all entities")

if __name__ == "__main__":
    main()
