"""
Schema definitions for the ProHandel API data
"""

def get_schema():
    """
    Returns the schema for all tables in the ProHandel API
    """
    return {
            "articles": {
                "primary_key": ["article_id"],
                "columns": {
                    "article_id": "string",
                    "name": "string",
                    "description": "string",
                    "price": "number",
                    "cost": "number",
                    "margin": "number",
                    "sku": "string",
                    "barcode": "string",
                    "category_id": "string",
                    "supplier_id": "string",
                    "created_at": "timestamp",
                    "updated_at": "timestamp",
                    "stock_quantity": "number",
                    "min_stock_level": "number",
                    "max_stock_level": "number",
                    "reorder_point": "number",
                    "status": "string",
                    "tax_rate": "number",
                    "weight": "number",
                    "dimensions": "string",
                    "image_url": "string"
                }
            },
            "customers": {
                "primary_key": ["customer_id"],
                "columns": {
                    "customer_id": "string",
                    "first_name": "string",
                    "last_name": "string",
                    "email": "string",
                    "phone": "string",
                    "address_line1": "string",
                    "address_line2": "string",
                    "city": "string",
                    "state": "string",
                    "postal_code": "string",
                    "country": "string",
                    "full_address": "string",
                    "customer_type": "string",
                    "company_name": "string",
                    "tax_id": "string",
                    "created_at": "timestamp",
                    "updated_at": "timestamp",
                    "last_purchase_date": "timestamp",
                    "total_purchases": "number",
                    "loyalty_points": "number",
                    "customer_status": "string"
                }
            },
            "orders": {
                "primary_key": ["order_id"],
                "columns": {
                    "order_id": "string",
                    "customer_id": "string",
                    "order_date": "timestamp",
                    "total_amount": "number",
                    "tax_amount": "number",
                    "discount_amount": "number",
                    "shipping_amount": "number",
                    "status": "string",
                    "payment_status": "string",
                    "shipping_status": "string",
                    "shipping_method": "string",
                    "payment_method": "string",
                    "notes": "string",
                    "created_at": "timestamp",
                    "updated_at": "timestamp",
                    "branch_id": "string",
                    "employee_id": "string",
                    "order_age_days": "number",
                    "items_count": "number"
                }
            },
            "order_items": {
                "primary_key": ["order_id", "article_id"],
                "columns": {
                    "order_id": "string",
                    "article_id": "string",
                    "quantity": "number",
                    "unit_price": "number",
                    "total_price": "number",
                    "discount": "number",
                    "tax_rate": "number",
                    "tax_amount": "number",
                    "created_at": "timestamp",
                    "updated_at": "timestamp"
                }
            },
            "sales": {
                "primary_key": ["sale_id"],
                "columns": {
                    "sale_id": "string",
                    "order_id": "string",
                    "customer_id": "string",
                    "sale_date": "timestamp",
                    "total_amount": "number",
                    "tax_amount": "number",
                    "discount_amount": "number",
                    "payment_method": "string",
                    "status": "string",
                    "branch_id": "string",
                    "employee_id": "string",
                    "created_at": "timestamp",
                    "updated_at": "timestamp",
                    "sale_age_days": "number"
                }
            },
            "sale_items": {
                "primary_key": ["sale_id", "article_id"],
                "columns": {
                    "sale_id": "string",
                    "article_id": "string",
                    "quantity": "number",
                    "unit_price": "number",
                    "total_price": "number",
                    "discount": "number",
                    "tax_rate": "number",
                    "tax_amount": "number",
                    "cost_price": "number",
                    "profit_margin": "number",
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
                    "stock_status": "string",
                    "last_count_date": "timestamp",
                    "created_at": "timestamp",
                    "updated_at": "timestamp"
                }
            },
            "suppliers": {
                "primary_key": ["supplier_id"],
                "columns": {
                    "supplier_id": "string",
                    "name": "string",
                    "contact_name": "string",
                    "email": "string",
                    "phone": "string",
                    "address_line1": "string",
                    "address_line2": "string",
                    "city": "string",
                    "state": "string",
                    "postal_code": "string",
                    "country": "string",
                    "full_address": "string",
                    "tax_id": "string",
                    "payment_terms": "string",
                    "lead_time_days": "number",
                    "created_at": "timestamp",
                    "updated_at": "timestamp"
                }
            },
            "branches": {
                "primary_key": ["branch_id"],
                "columns": {
                    "branch_id": "string",
                    "name": "string",
                    "address_line1": "string",
                    "address_line2": "string",
                    "city": "string",
                    "state": "string",
                    "postal_code": "string",
                    "country": "string",
                    "full_address": "string",
                    "phone": "string",
                    "email": "string",
                    "manager_id": "string",
                    "created_at": "timestamp",
                    "updated_at": "timestamp"
                }
            },
            "categories": {
                "primary_key": ["category_id"],
                "columns": {
                    "category_id": "string",
                    "name": "string",
                    "description": "string",
                    "parent_id": "string",
                    "level": "number",
                    "is_active": "boolean",
                    "created_at": "timestamp",
                    "updated_at": "timestamp"
                }
            },
            "countries": {
                "primary_key": ["country_id"],
                "columns": {
                    "country_id": "string",
                    "name": "string",
                    "code": "string",
                    "iso_code": "string",
                    "currency_code": "string",
                    "is_active": "boolean",
                    "created_at": "timestamp",
                    "updated_at": "timestamp"
                }
            },
            "credits": {
                "primary_key": ["credit_id"],
                "columns": {
                    "credit_id": "string",
                    "customer_id": "string",
                    "order_id": "string",
                    "amount": "number",
                    "reason": "string",
                    "status": "string",
                    "created_at": "timestamp",
                    "updated_at": "timestamp",
                    "expiry_date": "timestamp",
                    "used_amount": "number",
                    "remaining_amount": "number"
                }
            },
            "currencies": {
                "primary_key": ["currency_id"],
                "columns": {
                    "currency_id": "string",
                    "name": "string",
                    "code": "string",
                    "symbol": "string",
                    "exchange_rate": "number",
                    "is_base_currency": "boolean",
                    "is_active": "boolean",
                    "created_at": "timestamp",
                    "updated_at": "timestamp"
                }
            },
            "invoices": {
                "primary_key": ["invoice_id"],
                "columns": {
                    "invoice_id": "string",
                    "order_id": "string",
                    "customer_id": "string",
                    "invoice_number": "string",
                    "invoice_date": "timestamp",
                    "due_date": "timestamp",
                    "total_amount": "number",
                    "tax_amount": "number",
                    "discount_amount": "number",
                    "status": "string",
                    "payment_status": "string",
                    "notes": "string",
                    "created_at": "timestamp",
                    "updated_at": "timestamp",
                    "paid_amount": "number",
                    "remaining_amount": "number"
                }
            },
            "labels": {
                "primary_key": ["label_id"],
                "columns": {
                    "label_id": "string",
                    "name": "string",
                    "description": "string",
                    "color": "string",
                    "type": "string",
                    "is_active": "boolean",
                    "created_at": "timestamp",
                    "updated_at": "timestamp"
                }
            },
            "payments": {
                "primary_key": ["payment_id"],
                "columns": {
                    "payment_id": "string",
                    "order_id": "string",
                    "invoice_id": "string",
                    "customer_id": "string",
                    "amount": "number",
                    "payment_method": "string",
                    "payment_date": "timestamp",
                    "status": "string",
                    "reference_number": "string",
                    "notes": "string",
                    "created_at": "timestamp",
                    "updated_at": "timestamp",
                    "currency_code": "string",
                    "exchange_rate": "number"
                }
            },
            "staff": {
                "primary_key": ["staff_id"],
                "columns": {
                    "staff_id": "string",
                    "first_name": "string",
                    "last_name": "string",
                    "email": "string",
                    "phone": "string",
                    "position": "string",
                    "department": "string",
                    "branch_id": "string",
                    "is_active": "boolean",
                    "hire_date": "timestamp",
                    "created_at": "timestamp",
                    "updated_at": "timestamp"
                }
            },
            "vouchers": {
                "primary_key": ["voucher_id"],
                "columns": {
                    "voucher_id": "string",
                    "code": "string",
                    "type": "string",
                    "amount": "number",
                    "percentage": "number",
                    "start_date": "timestamp",
                    "end_date": "timestamp",
                    "is_active": "boolean",
                    "usage_limit": "number",
                    "usage_count": "number",
                    "created_at": "timestamp",
                    "updated_at": "timestamp",
                    "minimum_order_amount": "number",
                    "maximum_discount_amount": "number"
                }
            }
    }
