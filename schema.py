#!/usr/bin/env python3
"""
Schema definition for the ProHandel API connector
"""

def get_schema():
    """
    Returns the schema for the ProHandel API connector.
    This defines the tables and columns that will be synced to Fivetran.
    """
    return {
        "tables": {
            "articles": {
                "primary_key": ["article_id"],
                "columns": {
                    "article_id": "string",
                    "article_number": "string",
                    "name": "string",
                    "description": "string",
                    "price": "number",
                    "cost": "number",
                    "tax_rate": "number",
                    "category": "string",
                    "brand": "string",
                    "created_at": "timestamp",
                    "updated_at": "timestamp"
                }
            },
            "customers": {
                "primary_key": ["customer_id"],
                "columns": {
                    "customer_id": "string",
                    "customer_number": "string",
                    "first_name": "string",
                    "last_name": "string",
                    "email": "string",
                    "phone": "string",
                    "address": "string",
                    "city": "string",
                    "postal_code": "string",
                    "country": "string",
                    "created_at": "timestamp",
                    "updated_at": "timestamp"
                }
            },
            "orders": {
                "primary_key": ["order_id"],
                "columns": {
                    "order_id": "string",
                    "order_number": "string",
                    "customer_id": "string",
                    "order_date": "timestamp",
                    "total_amount": "number",
                    "tax_amount": "number",
                    "shipping_amount": "number",
                    "status": "string",
                    "payment_method": "string",
                    "shipping_method": "string",
                    "notes": "string",
                    "created_at": "timestamp",
                    "updated_at": "timestamp"
                }
            },
            "sales": {
                "primary_key": ["sale_id"],
                "columns": {
                    "sale_id": "string",
                    "order_id": "string",
                    "article_id": "string",
                    "quantity": "number",
                    "unit_price": "number",
                    "total_price": "number",
                    "tax_amount": "number",
                    "discount_amount": "number",
                    "created_at": "timestamp",
                    "updated_at": "timestamp"
                }
            },
            "inventory": {
                "primary_key": ["inventory_id"],
                "columns": {
                    "inventory_id": "string",
                    "article_id": "string",
                    "warehouse_id": "string",
                    "quantity": "number",
                    "min_stock_level": "number",
                    "max_stock_level": "number",
                    "reorder_point": "number",
                    "last_stock_check": "timestamp",
                    "created_at": "timestamp",
                    "updated_at": "timestamp"
                }
            }
        }
    }
