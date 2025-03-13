"""Data processor for the ProHandel API data"""
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import json
import traceback
from prohandel_api import ProHandelAPI

class DataProcessor:
    def __init__(self, api_key: str, api_secret: str):
        self.api = ProHandelAPI(api_key, api_secret)
    
    def _safe_float(self, value, default=0.0):
        """Safely convert a value to float"""
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def _safe_get(self, obj, key, default=None):
        """Safely get a value from a dictionary or return default if key doesn't exist or obj is not a dict"""
        if not isinstance(obj, dict):
            return default
        return obj.get(key, default)
        
    def process_articles(self, updated_since: Optional[str] = None) -> List[Dict]:
        """
        Process articles data with incremental loading
        """
        print(f"Processing articles data since {updated_since}")
        page = 1
        pagesize = 100
        all_articles = []
        has_more = True
        max_pages = 5  # Limit to 5 pages for testing
        
        while has_more and page <= max_pages:
            try:
                print(f"Fetching articles page {page}")
                response = self.api.get_articles(page=page, pagesize=pagesize, updated_since=updated_since)
                articles = response.get('data', [])
                print(f"Received {len(articles)} articles")
                
                if not articles:
                    print("No articles found, breaking loop")
                    break
                
                # Transform articles data
                transformed_articles = []
                for article in articles:
                    try:
                        # Add calculated fields
                        price = self._safe_float(self._safe_get(article, 'price'))
                        cost = self._safe_float(self._safe_get(article, 'cost'))
                        margin = 0
                        if price > 0 and cost > 0:
                            margin = (price - cost) / price * 100
                            
                        transformed_article = {
                            "article_id": str(self._safe_get(article, 'id', '')),
                            "name": self._safe_get(article, 'name', ''),
                            "description": self._safe_get(article, 'description', ''),
                            "price": price,
                            "cost": cost,
                            "margin": round(margin, 2),
                            "sku": self._safe_get(article, 'sku', ''),
                            "barcode": self._safe_get(article, 'barcode', ''),
                            "category_id": self._safe_get(article, 'category_id', ''),
                            "supplier_id": self._safe_get(article, 'supplier_id', ''),
                            "created_at": self._safe_get(article, 'created_at'),
                            "updated_at": self._safe_get(article, 'updated_at'),
                            "stock_quantity": self._safe_float(self._safe_get(article, 'stock_quantity')),
                            "min_stock_level": self._safe_float(self._safe_get(article, 'min_stock_level')),
                            "max_stock_level": self._safe_float(self._safe_get(article, 'max_stock_level')),
                            "reorder_point": self._safe_float(self._safe_get(article, 'reorder_point')),
                            "status": self._safe_get(article, 'status', 'active'),
                            "tax_rate": self._safe_float(self._safe_get(article, 'tax_rate')),
                            "weight": self._safe_float(self._safe_get(article, 'weight')),
                            "dimensions": self._safe_get(article, 'dimensions', ''),
                            "image_url": self._safe_get(article, 'image_url', '')
                        }
                        transformed_articles.append(transformed_article)
                    except Exception as e:
                        print(f"Error transforming article: {str(e)}")
                        traceback.print_exc()
                
                print(f"Transformed {len(transformed_articles)} articles")
                all_articles.extend(transformed_articles)
                
                # Check if there are more pages
                total_pages = self._safe_get(response, 'meta', {}).get('pagination', {}).get('total_pages', 0)
                has_more = page < total_pages
                page += 1
                
            except Exception as e:
                print(f"Error processing articles page {page}: {str(e)}")
                traceback.print_exc()
                break
                
        print(f"Returning {len(all_articles)} articles total")
        return all_articles
        
    def process_customers(self, updated_since: Optional[str] = None) -> List[Dict]:
        """
        Process customers data with incremental loading
        """
        print(f"Processing customers data since {updated_since}")
        page = 1
        pagesize = 100
        all_customers = []
        has_more = True
        max_pages = 5  # Limit to 5 pages for testing
        
        while has_more and page <= max_pages:
            try:
                print(f"Fetching customers page {page}")
                response = self.api.get_customers(page=page, pagesize=pagesize, updated_since=updated_since)
                customers = response.get('data', [])
                print(f"Received {len(customers)} customers")
                
                if not customers:
                    print("No customers found, breaking loop")
                    break
                
                # Transform customers data
                transformed_customers = []
                for customer in customers:
                    try:
                        # Create full address
                        address_parts = [
                            self._safe_get(customer, 'address_line1', ''),
                            self._safe_get(customer, 'address_line2', ''),
                            self._safe_get(customer, 'city', ''),
                            self._safe_get(customer, 'state', ''),
                            self._safe_get(customer, 'postal_code', ''),
                            self._safe_get(customer, 'country', '')
                        ]
                        full_address = ', '.join([part for part in address_parts if part])
                        
                        transformed_customer = {
                            "customer_id": str(self._safe_get(customer, 'id', '')),
                            "first_name": self._safe_get(customer, 'first_name', ''),
                            "last_name": self._safe_get(customer, 'last_name', ''),
                            "email": self._safe_get(customer, 'email', ''),
                            "phone": self._safe_get(customer, 'phone', ''),
                            "address_line1": self._safe_get(customer, 'address_line1', ''),
                            "address_line2": self._safe_get(customer, 'address_line2', ''),
                            "city": self._safe_get(customer, 'city', ''),
                            "state": self._safe_get(customer, 'state', ''),
                            "postal_code": self._safe_get(customer, 'postal_code', ''),
                            "country": self._safe_get(customer, 'country', ''),
                            "full_address": full_address,
                            "customer_type": self._safe_get(customer, 'customer_type', 'individual'),
                            "company_name": self._safe_get(customer, 'company_name', ''),
                            "tax_id": self._safe_get(customer, 'tax_id', ''),
                            "created_at": self._safe_get(customer, 'created_at'),
                            "updated_at": self._safe_get(customer, 'updated_at'),
                            "last_purchase_date": self._safe_get(customer, 'last_purchase_date'),
                            "total_purchases": self._safe_float(self._safe_get(customer, 'total_purchases')),
                            "loyalty_points": self._safe_float(self._safe_get(customer, 'loyalty_points')),
                            "customer_status": self._safe_get(customer, 'status', 'active')
                        }
                        transformed_customers.append(transformed_customer)
                    except Exception as e:
                        print(f"Error transforming customer: {str(e)}")
                        traceback.print_exc()
                
                print(f"Transformed {len(transformed_customers)} customers")
                all_customers.extend(transformed_customers)
                
                # Check if there are more pages
                total_pages = self._safe_get(response, 'meta', {}).get('pagination', {}).get('total_pages', 0)
                has_more = page < total_pages
                page += 1
                
            except Exception as e:
                print(f"Error processing customers page {page}: {str(e)}")
                traceback.print_exc()
                break
                
        print(f"Returning {len(all_customers)} customers total")
        return all_customers
        
    def process_orders(self, updated_since: Optional[str] = None) -> Dict[str, List[Dict]]:
        """
        Process orders data with incremental loading
        Returns both orders and order_items
        """
        print(f"Processing orders data since {updated_since}")
        page = 1
        pagesize = 100
        all_orders = []
        all_order_items = []
        has_more = True
        max_pages = 5  # Limit to 5 pages for testing
        
        while has_more and page <= max_pages:
            try:
                print(f"Fetching orders page {page}")
                response = self.api.get_orders(page=page, pagesize=pagesize, updated_since=updated_since)
                orders = response.get('data', [])
                print(f"Received {len(orders)} orders")
                
                if not orders:
                    print("No orders found, breaking loop")
                    break
                
                # Transform orders data
                for order in orders:
                    try:
                        # Calculate order age in days
                        order_date = None
                        order_age_days = None
                        order_date_str = self._safe_get(order, 'order_date')
                        if order_date_str:
                            try:
                                order_date = datetime.fromisoformat(order_date_str.replace('Z', '+00:00'))
                                now = datetime.now()
                                order_age_days = (now - order_date).days
                            except Exception as e:
                                print(f"Error parsing order date: {str(e)}")
                        
                        transformed_order = {
                            "order_id": str(self._safe_get(order, 'id', '')),
                            "customer_id": str(self._safe_get(order, 'customer_id', '')),
                            "order_date": order_date_str,
                            "total_amount": self._safe_float(self._safe_get(order, 'total_amount')),
                            "tax_amount": self._safe_float(self._safe_get(order, 'tax_amount')),
                            "discount_amount": self._safe_float(self._safe_get(order, 'discount_amount')),
                            "shipping_amount": self._safe_float(self._safe_get(order, 'shipping_amount')),
                            "status": self._safe_get(order, 'status', ''),
                            "payment_status": self._safe_get(order, 'payment_status', ''),
                            "shipping_status": self._safe_get(order, 'shipping_status', ''),
                            "shipping_method": self._safe_get(order, 'shipping_method', ''),
                            "payment_method": self._safe_get(order, 'payment_method', ''),
                            "notes": self._safe_get(order, 'notes', ''),
                            "created_at": self._safe_get(order, 'created_at'),
                            "updated_at": self._safe_get(order, 'updated_at'),
                            "branch_id": str(self._safe_get(order, 'branch_id', '')),
                            "employee_id": str(self._safe_get(order, 'employee_id', '')),
                            "order_age_days": order_age_days,
                            "items_count": len(self._safe_get(order, 'items', []))
                        }
                        all_orders.append(transformed_order)
                        
                        # Process order items
                        for item in self._safe_get(order, 'items', []):
                            try:
                                transformed_item = {
                                    "order_id": str(self._safe_get(order, 'id', '')),
                                    "article_id": str(self._safe_get(item, 'article_id', '')),
                                    "quantity": self._safe_float(self._safe_get(item, 'quantity')),
                                    "unit_price": self._safe_float(self._safe_get(item, 'unit_price')),
                                    "total_price": self._safe_float(self._safe_get(item, 'total_price')),
                                    "discount": self._safe_float(self._safe_get(item, 'discount')),
                                    "tax_rate": self._safe_float(self._safe_get(item, 'tax_rate')),
                                    "tax_amount": self._safe_float(self._safe_get(item, 'tax_amount')),
                                    "created_at": self._safe_get(item, 'created_at', self._safe_get(order, 'created_at')),
                                    "updated_at": self._safe_get(item, 'updated_at', self._safe_get(order, 'updated_at'))
                                }
                                all_order_items.append(transformed_item)
                            except Exception as e:
                                print(f"Error transforming order item: {str(e)}")
                                traceback.print_exc()
                    except Exception as e:
                        print(f"Error transforming order: {str(e)}")
                        traceback.print_exc()
                
                print(f"Transformed {len(all_orders)} orders")
                
                # Check if there are more pages
                total_pages = self._safe_get(response, 'meta', {}).get('pagination', {}).get('total_pages', 0)
                has_more = page < total_pages
                page += 1
                
            except Exception as e:
                print(f"Error processing orders page {page}: {str(e)}")
                traceback.print_exc()
                break
                
        print(f"Returning {len(all_orders)} orders and {len(all_order_items)} order items total")
        return {
            "orders": all_orders,
            "order_items": all_order_items
        }
        
    def process_sales(self, updated_since: Optional[str] = None) -> Dict[str, List[Dict]]:
        """
        Process sales data with incremental loading
        Returns both sales and sale_items
        """
        print(f"Processing sales data since {updated_since}")
        page = 1
        pagesize = 100
        all_sales = []
        all_sale_items = []
        has_more = True
        max_pages = 5  # Limit to 5 pages for testing
        
        while has_more and page <= max_pages:
            try:
                print(f"Fetching sales page {page}")
                response = self.api.get_sales(page=page, pagesize=pagesize, updated_since=updated_since)
                sales = response.get('data', [])
                print(f"Received {len(sales)} sales")
                
                if not sales:
                    print("No sales found, breaking loop")
                    break
                
                # Transform sales data
                for sale in sales:
                    try:
                        # Calculate sale age in days
                        sale_date = None
                        sale_age_days = None
                        sale_date_str = self._safe_get(sale, 'sale_date')
                        if sale_date_str:
                            try:
                                sale_date = datetime.fromisoformat(sale_date_str.replace('Z', '+00:00'))
                                now = datetime.now()
                                sale_age_days = (now - sale_date).days
                            except Exception as e:
                                print(f"Error parsing sale date: {str(e)}")
                        
                        transformed_sale = {
                            "sale_id": str(self._safe_get(sale, 'id', '')),
                            "order_id": str(self._safe_get(sale, 'order_id', '')),
                            "customer_id": str(self._safe_get(sale, 'customer_id', '')),
                            "sale_date": sale_date_str,
                            "total_amount": self._safe_float(self._safe_get(sale, 'total_amount')),
                            "tax_amount": self._safe_float(self._safe_get(sale, 'tax_amount')),
                            "discount_amount": self._safe_float(self._safe_get(sale, 'discount_amount')),
                            "payment_method": self._safe_get(sale, 'payment_method', ''),
                            "status": self._safe_get(sale, 'status', ''),
                            "branch_id": str(self._safe_get(sale, 'branch_id', '')),
                            "employee_id": str(self._safe_get(sale, 'employee_id', '')),
                            "created_at": self._safe_get(sale, 'created_at'),
                            "updated_at": self._safe_get(sale, 'updated_at'),
                            "sale_age_days": sale_age_days
                        }
                        all_sales.append(transformed_sale)
                        
                        # Process sale items
                        for item in self._safe_get(sale, 'items', []):
                            try:
                                # Calculate profit margin
                                unit_price = self._safe_float(self._safe_get(item, 'unit_price'))
                                cost_price = self._safe_float(self._safe_get(item, 'cost_price'))
                                profit_margin = 0
                                if unit_price > 0 and cost_price > 0:
                                    profit_margin = (unit_price - cost_price) / unit_price * 100
                                    
                                transformed_item = {
                                    "sale_id": str(self._safe_get(sale, 'id', '')),
                                    "article_id": str(self._safe_get(item, 'article_id', '')),
                                    "quantity": self._safe_float(self._safe_get(item, 'quantity')),
                                    "unit_price": unit_price,
                                    "total_price": self._safe_float(self._safe_get(item, 'total_price')),
                                    "discount": self._safe_float(self._safe_get(item, 'discount')),
                                    "tax_rate": self._safe_float(self._safe_get(item, 'tax_rate')),
                                    "tax_amount": self._safe_float(self._safe_get(item, 'tax_amount')),
                                    "cost_price": cost_price,
                                    "profit_margin": round(profit_margin, 2),
                                    "created_at": self._safe_get(item, 'created_at', self._safe_get(sale, 'created_at')),
                                    "updated_at": self._safe_get(item, 'updated_at', self._safe_get(sale, 'updated_at'))
                                }
                                all_sale_items.append(transformed_item)
                            except Exception as e:
                                print(f"Error transforming sale item: {str(e)}")
                                traceback.print_exc()
                    except Exception as e:
                        print(f"Error transforming sale: {str(e)}")
                        traceback.print_exc()
                
                print(f"Transformed {len(all_sales)} sales")
                
                # Check if there are more pages
                total_pages = self._safe_get(response, 'meta', {}).get('pagination', {}).get('total_pages', 0)
                has_more = page < total_pages
                page += 1
                
            except Exception as e:
                print(f"Error processing sales page {page}: {str(e)}")
                traceback.print_exc()
                break
                
        print(f"Returning {len(all_sales)} sales and {len(all_sale_items)} sale items total")
        return {
            "sales": all_sales,
            "sale_items": all_sale_items
        }
        
    def process_inventory(self, updated_since: Optional[str] = None) -> List[Dict]:
        """
        Process inventory data with incremental loading
        """
        print(f"Processing inventory data since {updated_since}")
        page = 1
        pagesize = 100
        all_inventory = []
        has_more = True
        max_pages = 5  # Limit to 5 pages for testing
        
        while has_more and page <= max_pages:
            try:
                print(f"Fetching inventory page {page}")
                response = self.api.get_inventory(page=page, pagesize=pagesize, updated_since=updated_since)
                inventory_items = response.get('data', [])
                print(f"Received {len(inventory_items)} inventory items")
                
                if not inventory_items:
                    print("No inventory items found, breaking loop")
                    break
                
                # Transform inventory data
                for item in inventory_items:
                    try:
                        # Determine stock status
                        quantity = self._safe_float(self._safe_get(item, 'quantity'))
                        reorder_point = self._safe_float(self._safe_get(item, 'reorder_point'))
                        max_stock_level = self._safe_float(self._safe_get(item, 'max_stock_level'))
                        
                        stock_status = 'normal'
                        if quantity <= 0:
                            stock_status = 'out_of_stock'
                        elif quantity < reorder_point:
                            stock_status = 'low_stock'
                        elif max_stock_level > 0 and quantity > max_stock_level:
                            stock_status = 'overstocked'
                        
                        transformed_item = {
                            "inventory_id": str(self._safe_get(item, 'id', '')),
                            "article_id": str(self._safe_get(item, 'article_id', '')),
                            "warehouse_id": str(self._safe_get(item, 'warehouse_id', '')),
                            "quantity": quantity,
                            "min_stock_level": self._safe_float(self._safe_get(item, 'min_stock_level')),
                            "max_stock_level": max_stock_level,
                            "reorder_point": reorder_point,
                            "stock_status": stock_status,
                            "last_count_date": self._safe_get(item, 'last_count_date'),
                            "created_at": self._safe_get(item, 'created_at'),
                            "updated_at": self._safe_get(item, 'updated_at')
                        }
                        all_inventory.append(transformed_item)
                    except Exception as e:
                        print(f"Error transforming inventory item: {str(e)}")
                        traceback.print_exc()
                
                print(f"Transformed {len(inventory_items)} inventory items")
                
                # Check if there are more pages
                total_pages = self._safe_get(response, 'meta', {}).get('pagination', {}).get('total_pages', 0)
                has_more = page < total_pages
                page += 1
                
            except Exception as e:
                print(f"Error processing inventory page {page}: {str(e)}")
                traceback.print_exc()
                break
                
        print(f"Returning {len(all_inventory)} inventory items total")
        return all_inventory
        
    def process_suppliers(self, updated_since: Optional[str] = None) -> List[Dict]:
        """
        Process suppliers data with incremental loading
        """
        print(f"Processing suppliers data since {updated_since}")
        page = 1
        pagesize = 100
        all_suppliers = []
        has_more = True
        max_pages = 5  # Limit to 5 pages for testing
        
        while has_more and page <= max_pages:
            try:
                print(f"Fetching suppliers page {page}")
                response = self.api.get_suppliers(page=page, pagesize=pagesize, updated_since=updated_since)
                suppliers = response.get('data', [])
                print(f"Received {len(suppliers)} suppliers")
                
                if not suppliers:
                    print("No suppliers found, breaking loop")
                    break
                
                # Transform suppliers data
                transformed_suppliers = []
                for supplier in suppliers:
                    try:
                        # Create full address
                        address_parts = [
                            self._safe_get(supplier, 'address_line1', ''),
                            self._safe_get(supplier, 'address_line2', ''),
                            self._safe_get(supplier, 'city', ''),
                            self._safe_get(supplier, 'state', ''),
                            self._safe_get(supplier, 'postal_code', ''),
                            self._safe_get(supplier, 'country', '')
                        ]
                        full_address = ', '.join([part for part in address_parts if part])
                        
                        transformed_supplier = {
                            "supplier_id": str(self._safe_get(supplier, 'id', '')),
                            "name": self._safe_get(supplier, 'name', ''),
                            "contact_name": self._safe_get(supplier, 'contact_name', ''),
                            "email": self._safe_get(supplier, 'email', ''),
                            "phone": self._safe_get(supplier, 'phone', ''),
                            "address_line1": self._safe_get(supplier, 'address_line1', ''),
                            "address_line2": self._safe_get(supplier, 'address_line2', ''),
                            "city": self._safe_get(supplier, 'city', ''),
                            "state": self._safe_get(supplier, 'state', ''),
                            "postal_code": self._safe_get(supplier, 'postal_code', ''),
                            "country": self._safe_get(supplier, 'country', ''),
                            "full_address": full_address,
                            "tax_id": self._safe_get(supplier, 'tax_id', ''),
                            "payment_terms": self._safe_get(supplier, 'payment_terms', ''),
                            "lead_time_days": self._safe_float(self._safe_get(supplier, 'lead_time_days')),
                            "created_at": self._safe_get(supplier, 'created_at'),
                            "updated_at": self._safe_get(supplier, 'updated_at')
                        }
                        transformed_suppliers.append(transformed_supplier)
                    except Exception as e:
                        print(f"Error transforming supplier: {str(e)}")
                        traceback.print_exc()
                
                print(f"Transformed {len(transformed_suppliers)} suppliers")
                all_suppliers.extend(transformed_suppliers)
                
                # Check if there are more pages
                total_pages = self._safe_get(response, 'meta', {}).get('pagination', {}).get('total_pages', 0)
                has_more = page < total_pages
                page += 1
                
            except Exception as e:
                print(f"Error processing suppliers page {page}: {str(e)}")
                traceback.print_exc()
                break
                
        print(f"Returning {len(all_suppliers)} suppliers total")
        return all_suppliers
        
    def process_branches(self, updated_since: Optional[str] = None) -> List[Dict]:
        """
        Process branches data with incremental loading
        """
        print(f"Processing branches data since {updated_since}")
        page = 1
        pagesize = 100
        all_branches = []
        has_more = True
        max_pages = 5  # Limit to 5 pages for testing
        
        while has_more and page <= max_pages:
            try:
                print(f"Fetching branches page {page}")
                response = self.api.get_branches(page=page, pagesize=pagesize, updated_since=updated_since)
                branches = response.get('data', [])
                print(f"Received {len(branches)} branches")
                
                if not branches:
                    print("No branches found, breaking loop")
                    break
                
                # Transform branches data
                transformed_branches = []
                for branch in branches:
                    try:
                        # Create full address
                        address_parts = [
                            self._safe_get(branch, 'address_line1', ''),
                            self._safe_get(branch, 'address_line2', ''),
                            self._safe_get(branch, 'city', ''),
                            self._safe_get(branch, 'state', ''),
                            self._safe_get(branch, 'postal_code', ''),
                            self._safe_get(branch, 'country', '')
                        ]
                        full_address = ', '.join([part for part in address_parts if part])
                        
                        transformed_branch = {
                            "branch_id": str(self._safe_get(branch, 'id', '')),
                            "name": self._safe_get(branch, 'name', ''),
                            "address_line1": self._safe_get(branch, 'address_line1', ''),
                            "address_line2": self._safe_get(branch, 'address_line2', ''),
                            "city": self._safe_get(branch, 'city', ''),
                            "state": self._safe_get(branch, 'state', ''),
                            "postal_code": self._safe_get(branch, 'postal_code', ''),
                            "country": self._safe_get(branch, 'country', ''),
                            "full_address": full_address,
                            "phone": self._safe_get(branch, 'phone', ''),
                            "email": self._safe_get(branch, 'email', ''),
                            "manager_id": self._safe_get(branch, 'manager_id', ''),
                            "created_at": self._safe_get(branch, 'created_at'),
                            "updated_at": self._safe_get(branch, 'updated_at')
                        }
                        transformed_branches.append(transformed_branch)
                    except Exception as e:
                        print(f"Error transforming branch: {str(e)}")
                        traceback.print_exc()
                
                print(f"Transformed {len(transformed_branches)} branches")
                all_branches.extend(transformed_branches)
                
                # Check if there are more pages
                total_pages = self._safe_get(response, 'meta', {}).get('pagination', {}).get('total_pages', 0)
                has_more = page < total_pages
                page += 1
                
            except Exception as e:
                print(f"Error processing branches page {page}: {str(e)}")
                traceback.print_exc()
                break
                
        print(f"Returning {len(all_branches)} branches total")
        return all_branches
        
    def process_categories(self, updated_since: Optional[str] = None) -> List[Dict]:
        """
        Process categories data with incremental loading
        """
        print(f"Processing categories data since {updated_since}")
        page = 1
        pagesize = 100
        all_categories = []
        has_more = True
        max_pages = 5  # Limit to 5 pages for testing
        
        while has_more and page <= max_pages:
            try:
                print(f"Fetching categories page {page}")
                response = self.api.get_categories(page=page, pagesize=pagesize, updated_since=updated_since)
                categories = response.get('data', [])
                print(f"Received {len(categories)} categories")
                
                if not categories:
                    print("No categories found, breaking loop")
                    break
                
                # Transform categories data
                transformed_categories = []
                for category in categories:
                    try:
                        transformed_category = {
                            "category_id": str(self._safe_get(category, 'id', '')),
                            "name": self._safe_get(category, 'name', ''),
                            "description": self._safe_get(category, 'description', ''),
                            "parent_id": str(self._safe_get(category, 'parent_id', '')),
                            "level": self._safe_float(self._safe_get(category, 'level')),
                            "is_active": bool(self._safe_get(category, 'is_active', True)),
                            "created_at": self._safe_get(category, 'created_at'),
                            "updated_at": self._safe_get(category, 'updated_at')
                        }
                        transformed_categories.append(transformed_category)
                    except Exception as e:
                        print(f"Error transforming category: {str(e)}")
                        traceback.print_exc()
                
                print(f"Transformed {len(transformed_categories)} categories")
                all_categories.extend(transformed_categories)
                
                # Check if there are more pages
                total_pages = self._safe_get(response, 'meta', {}).get('pagination', {}).get('total_pages', 0)
                has_more = page < total_pages
                page += 1
                
            except Exception as e:
                print(f"Error processing categories page {page}: {str(e)}")
                traceback.print_exc()
                break
                
        print(f"Returning {len(all_categories)} categories total")
        return all_categories
        
    def process_countries(self, updated_since: Optional[str] = None) -> List[Dict]:
        """
        Process countries data with incremental loading
        """
        print(f"Processing countries data since {updated_since}")
        page = 1
        pagesize = 100
        all_countries = []
        has_more = True
        max_pages = 5  # Limit to 5 pages for testing
        
        while has_more and page <= max_pages:
            try:
                print(f"Fetching countries page {page}")
                response = self.api.get_countries(page=page, pagesize=pagesize, updated_since=updated_since)
                countries = response.get('data', [])
                print(f"Received {len(countries)} countries")
                
                if not countries:
                    print("No countries found, breaking loop")
                    break
                
                # Transform countries data
                transformed_countries = []
                for country in countries:
                    try:
                        transformed_country = {
                            "country_id": str(self._safe_get(country, 'id', '')),
                            "name": self._safe_get(country, 'name', ''),
                            "code": self._safe_get(country, 'code', ''),
                            "iso_code": self._safe_get(country, 'iso_code', ''),
                            "currency_code": self._safe_get(country, 'currency_code', ''),
                            "is_active": bool(self._safe_get(country, 'is_active', True)),
                            "created_at": self._safe_get(country, 'created_at'),
                            "updated_at": self._safe_get(country, 'updated_at')
                        }
                        transformed_countries.append(transformed_country)
                    except Exception as e:
                        print(f"Error transforming country: {str(e)}")
                        traceback.print_exc()
                
                print(f"Transformed {len(transformed_countries)} countries")
                all_countries.extend(transformed_countries)
                
                # Check if there are more pages
                total_pages = self._safe_get(response, 'meta', {}).get('pagination', {}).get('total_pages', 0)
                has_more = page < total_pages
                page += 1
                
            except Exception as e:
                print(f"Error processing countries page {page}: {str(e)}")
                traceback.print_exc()
                break
                
        print(f"Returning {len(all_countries)} countries total")
        return all_countries
        
    def process_credits(self, updated_since: Optional[str] = None) -> List[Dict]:
        """
        Process credits data with incremental loading
        """
        print(f"Processing credits data since {updated_since}")
        page = 1
        pagesize = 100
        all_credits = []
        has_more = True
        max_pages = 5  # Limit to 5 pages for testing
        
        while has_more and page <= max_pages:
            try:
                print(f"Fetching credits page {page}")
                response = self.api.get_credits(page=page, pagesize=pagesize, updated_since=updated_since)
                credits = response.get('data', [])
                print(f"Received {len(credits)} credits")
                
                if not credits:
                    print("No credits found, breaking loop")
                    break
                
                # Transform credits data
                transformed_credits = []
                for credit in credits:
                    try:
                        # Calculate remaining amount if not provided
                        amount = self._safe_float(self._safe_get(credit, 'amount'))
                        used_amount = self._safe_float(self._safe_get(credit, 'used_amount'))
                        remaining_amount = self._safe_float(self._safe_get(credit, 'remaining_amount'))
                        
                        if remaining_amount == 0 and amount > 0:
                            remaining_amount = amount - used_amount
                        
                        transformed_credit = {
                            "credit_id": str(self._safe_get(credit, 'id', '')),
                            "customer_id": str(self._safe_get(credit, 'customer_id', '')),
                            "order_id": str(self._safe_get(credit, 'order_id', '')),
                            "amount": amount,
                            "reason": self._safe_get(credit, 'reason', ''),
                            "status": self._safe_get(credit, 'status', ''),
                            "created_at": self._safe_get(credit, 'created_at'),
                            "updated_at": self._safe_get(credit, 'updated_at'),
                            "expiry_date": self._safe_get(credit, 'expiry_date'),
                            "used_amount": used_amount,
                            "remaining_amount": remaining_amount
                        }
                        transformed_credits.append(transformed_credit)
                    except Exception as e:
                        print(f"Error transforming credit: {str(e)}")
                        traceback.print_exc()
                
                print(f"Transformed {len(transformed_credits)} credits")
                all_credits.extend(transformed_credits)
                
                # Check if there are more pages
                total_pages = self._safe_get(response, 'meta', {}).get('pagination', {}).get('total_pages', 0)
                has_more = page < total_pages
                page += 1
                
            except Exception as e:
                print(f"Error processing credits page {page}: {str(e)}")
                traceback.print_exc()
                break
                
        print(f"Returning {len(all_credits)} credits total")
        return all_credits
        
    def process_currencies(self, updated_since: Optional[str] = None) -> List[Dict]:
        """
        Process currencies data with incremental loading
        """
        print(f"Processing currencies data since {updated_since}")
        page = 1
        pagesize = 100
        all_currencies = []
        has_more = True
        max_pages = 5  # Limit to 5 pages for testing
        
        while has_more and page <= max_pages:
            try:
                print(f"Fetching currencies page {page}")
                response = self.api.get_currencies(page=page, pagesize=pagesize, updated_since=updated_since)
                currencies = response.get('data', [])
                print(f"Received {len(currencies)} currencies")
                
                if not currencies:
                    print("No currencies found, breaking loop")
                    break
                
                # Transform currencies data
                transformed_currencies = []
                for currency in currencies:
                    try:
                        transformed_currency = {
                            "currency_id": str(self._safe_get(currency, 'id', '')),
                            "name": self._safe_get(currency, 'name', ''),
                            "code": self._safe_get(currency, 'code', ''),
                            "symbol": self._safe_get(currency, 'symbol', ''),
                            "exchange_rate": self._safe_float(self._safe_get(currency, 'exchange_rate')),
                            "is_base_currency": bool(self._safe_get(currency, 'is_base_currency', False)),
                            "is_active": bool(self._safe_get(currency, 'is_active', True)),
                            "created_at": self._safe_get(currency, 'created_at'),
                            "updated_at": self._safe_get(currency, 'updated_at')
                        }
                        transformed_currencies.append(transformed_currency)
                    except Exception as e:
                        print(f"Error transforming currency: {str(e)}")
                        traceback.print_exc()
                
                print(f"Transformed {len(transformed_currencies)} currencies")
                all_currencies.extend(transformed_currencies)
                
                # Check if there are more pages
                total_pages = self._safe_get(response, 'meta', {}).get('pagination', {}).get('total_pages', 0)
                has_more = page < total_pages
                page += 1
                
            except Exception as e:
                print(f"Error processing currencies page {page}: {str(e)}")
                traceback.print_exc()
                break
                
        print(f"Returning {len(all_currencies)} currencies total")
        return all_currencies
        
    def process_invoices(self, updated_since: Optional[str] = None) -> List[Dict]:
        """
        Process invoices data with incremental loading
        """
        print(f"Processing invoices data since {updated_since}")
        page = 1
        pagesize = 100
        all_invoices = []
        has_more = True
        max_pages = 5  # Limit to 5 pages for testing
        
        while has_more and page <= max_pages:
            try:
                print(f"Fetching invoices page {page}")
                response = self.api.get_invoices(page=page, pagesize=pagesize, updated_since=updated_since)
                invoices = response.get('data', [])
                print(f"Received {len(invoices)} invoices")
                
                if not invoices:
                    print("No invoices found, breaking loop")
                    break
                
                # Transform invoices data
                transformed_invoices = []
                for invoice in invoices:
                    try:
                        # Calculate remaining amount if not provided
                        total_amount = self._safe_float(self._safe_get(invoice, 'total_amount'))
                        paid_amount = self._safe_float(self._safe_get(invoice, 'paid_amount'))
                        remaining_amount = self._safe_float(self._safe_get(invoice, 'remaining_amount'))
                        
                        if remaining_amount == 0 and total_amount > 0:
                            remaining_amount = total_amount - paid_amount
                        
                        transformed_invoice = {
                            "invoice_id": str(self._safe_get(invoice, 'id', '')),
                            "order_id": str(self._safe_get(invoice, 'order_id', '')),
                            "customer_id": str(self._safe_get(invoice, 'customer_id', '')),
                            "invoice_number": self._safe_get(invoice, 'invoice_number', ''),
                            "invoice_date": self._safe_get(invoice, 'invoice_date'),
                            "due_date": self._safe_get(invoice, 'due_date'),
                            "total_amount": total_amount,
                            "tax_amount": self._safe_float(self._safe_get(invoice, 'tax_amount')),
                            "discount_amount": self._safe_float(self._safe_get(invoice, 'discount_amount')),
                            "status": self._safe_get(invoice, 'status', ''),
                            "payment_status": self._safe_get(invoice, 'payment_status', ''),
                            "notes": self._safe_get(invoice, 'notes', ''),
                            "created_at": self._safe_get(invoice, 'created_at'),
                            "updated_at": self._safe_get(invoice, 'updated_at'),
                            "paid_amount": paid_amount,
                            "remaining_amount": remaining_amount
                        }
                        transformed_invoices.append(transformed_invoice)
                    except Exception as e:
                        print(f"Error transforming invoice: {str(e)}")
                        traceback.print_exc()
                
                print(f"Transformed {len(transformed_invoices)} invoices")
                all_invoices.extend(transformed_invoices)
                
                # Check if there are more pages
                total_pages = self._safe_get(response, 'meta', {}).get('pagination', {}).get('total_pages', 0)
                has_more = page < total_pages
                page += 1
                
            except Exception as e:
                print(f"Error processing invoices page {page}: {str(e)}")
                traceback.print_exc()
                break
                
        print(f"Returning {len(all_invoices)} invoices total")
        return all_invoices
        
    def process_labels(self, updated_since: Optional[str] = None) -> List[Dict]:
        """
        Process labels data with incremental loading
        """
        print(f"Processing labels data since {updated_since}")
        page = 1
        pagesize = 100
        all_labels = []
        has_more = True
        max_pages = 5  # Limit to 5 pages for testing
        
        while has_more and page <= max_pages:
            try:
                print(f"Fetching labels page {page}")
                response = self.api.get_labels(page=page, pagesize=pagesize, updated_since=updated_since)
                labels = response.get('data', [])
                print(f"Received {len(labels)} labels")
                
                if not labels:
                    print("No labels found, breaking loop")
                    break
                
                # Transform labels data
                transformed_labels = []
                for label in labels:
                    try:
                        transformed_label = {
                            "label_id": str(self._safe_get(label, 'id', '')),
                            "name": self._safe_get(label, 'name', ''),
                            "description": self._safe_get(label, 'description', ''),
                            "color": self._safe_get(label, 'color', ''),
                            "type": self._safe_get(label, 'type', ''),
                            "is_active": bool(self._safe_get(label, 'is_active', True)),
                            "created_at": self._safe_get(label, 'created_at'),
                            "updated_at": self._safe_get(label, 'updated_at')
                        }
                        transformed_labels.append(transformed_label)
                    except Exception as e:
                        print(f"Error transforming label: {str(e)}")
                        traceback.print_exc()
                
                print(f"Transformed {len(transformed_labels)} labels")
                all_labels.extend(transformed_labels)
                
                # Check if there are more pages
                total_pages = self._safe_get(response, 'meta', {}).get('pagination', {}).get('total_pages', 0)
                has_more = page < total_pages
                page += 1
                
            except Exception as e:
                print(f"Error processing labels page {page}: {str(e)}")
                traceback.print_exc()
                break
                
        print(f"Returning {len(all_labels)} labels total")
        return all_labels
        
    def process_payments(self, updated_since: Optional[str] = None) -> List[Dict]:
        """
        Process payments data with incremental loading
        """
        print(f"Processing payments data since {updated_since}")
        page = 1
        pagesize = 100
        all_payments = []
        has_more = True
        max_pages = 5  # Limit to 5 pages for testing
        
        while has_more and page <= max_pages:
            try:
                print(f"Fetching payments page {page}")
                response = self.api.get_payments(page=page, pagesize=pagesize, updated_since=updated_since)
                payments = response.get('data', [])
                print(f"Received {len(payments)} payments")
                
                if not payments:
                    print("No payments found, breaking loop")
                    break
                
                # Transform payments data
                transformed_payments = []
                for payment in payments:
                    try:
                        transformed_payment = {
                            "payment_id": str(self._safe_get(payment, 'id', '')),
                            "order_id": str(self._safe_get(payment, 'order_id', '')),
                            "invoice_id": str(self._safe_get(payment, 'invoice_id', '')),
                            "customer_id": str(self._safe_get(payment, 'customer_id', '')),
                            "amount": self._safe_float(self._safe_get(payment, 'amount')),
                            "payment_method": self._safe_get(payment, 'payment_method', ''),
                            "payment_date": self._safe_get(payment, 'payment_date'),
                            "status": self._safe_get(payment, 'status', ''),
                            "reference_number": self._safe_get(payment, 'reference_number', ''),
                            "notes": self._safe_get(payment, 'notes', ''),
                            "created_at": self._safe_get(payment, 'created_at'),
                            "updated_at": self._safe_get(payment, 'updated_at'),
                            "currency_code": self._safe_get(payment, 'currency_code', ''),
                            "exchange_rate": self._safe_float(self._safe_get(payment, 'exchange_rate'))
                        }
                        transformed_payments.append(transformed_payment)
                    except Exception as e:
                        print(f"Error transforming payment: {str(e)}")
                        traceback.print_exc()
                
                print(f"Transformed {len(transformed_payments)} payments")
                all_payments.extend(transformed_payments)
                
                # Check if there are more pages
                total_pages = self._safe_get(response, 'meta', {}).get('pagination', {}).get('total_pages', 0)
                has_more = page < total_pages
                page += 1
                
            except Exception as e:
                print(f"Error processing payments page {page}: {str(e)}")
                traceback.print_exc()
                break
                
        print(f"Returning {len(all_payments)} payments total")
        return all_payments
        
    def process_staff(self, updated_since: Optional[str] = None) -> List[Dict]:
        """
        Process staff data with incremental loading
        """
        print(f"Processing staff data since {updated_since}")
        page = 1
        pagesize = 100
        all_staff = []
        has_more = True
        max_pages = 5  # Limit to 5 pages for testing
        
        while has_more and page <= max_pages:
            try:
                print(f"Fetching staff page {page}")
                response = self.api.get_staff(page=page, pagesize=pagesize, updated_since=updated_since)
                staff_members = response.get('data', [])
                print(f"Received {len(staff_members)} staff members")
                
                if not staff_members:
                    print("No staff members found, breaking loop")
                    break
                
                # Transform staff data
                transformed_staff = []
                for staff in staff_members:
                    try:
                        transformed_staff_member = {
                            "staff_id": str(self._safe_get(staff, 'id', '')),
                            "first_name": self._safe_get(staff, 'first_name', ''),
                            "last_name": self._safe_get(staff, 'last_name', ''),
                            "email": self._safe_get(staff, 'email', ''),
                            "phone": self._safe_get(staff, 'phone', ''),
                            "position": self._safe_get(staff, 'position', ''),
                            "department": self._safe_get(staff, 'department', ''),
                            "branch_id": str(self._safe_get(staff, 'branch_id', '')),
                            "is_active": bool(self._safe_get(staff, 'is_active', True)),
                            "hire_date": self._safe_get(staff, 'hire_date'),
                            "created_at": self._safe_get(staff, 'created_at'),
                            "updated_at": self._safe_get(staff, 'updated_at')
                        }
                        transformed_staff.append(transformed_staff_member)
                    except Exception as e:
                        print(f"Error transforming staff member: {str(e)}")
                        traceback.print_exc()
                
                print(f"Transformed {len(transformed_staff)} staff members")
                all_staff.extend(transformed_staff)
                
                # Check if there are more pages
                total_pages = self._safe_get(response, 'meta', {}).get('pagination', {}).get('total_pages', 0)
                has_more = page < total_pages
                page += 1
                
            except Exception as e:
                print(f"Error processing staff page {page}: {str(e)}")
                traceback.print_exc()
                break
                
        print(f"Returning {len(all_staff)} staff members total")
        return all_staff
        
    def process_vouchers(self, updated_since: Optional[str] = None) -> List[Dict]:
        """
        Process vouchers data with incremental loading
        """
        print(f"Processing vouchers data since {updated_since}")
        page = 1
        pagesize = 100
        all_vouchers = []
        has_more = True
        max_pages = 5  # Limit to 5 pages for testing
        
        while has_more and page <= max_pages:
            try:
                print(f"Fetching vouchers page {page}")
                response = self.api.get_vouchers(page=page, pagesize=pagesize, updated_since=updated_since)
                vouchers = response.get('data', [])
                print(f"Received {len(vouchers)} vouchers")
                
                if not vouchers:
                    print("No vouchers found, breaking loop")
                    break
                
                # Transform vouchers data
                transformed_vouchers = []
                for voucher in vouchers:
                    try:
                        transformed_voucher = {
                            "voucher_id": str(self._safe_get(voucher, 'id', '')),
                            "code": self._safe_get(voucher, 'code', ''),
                            "type": self._safe_get(voucher, 'type', ''),
                            "amount": self._safe_float(self._safe_get(voucher, 'amount')),
                            "percentage": self._safe_float(self._safe_get(voucher, 'percentage')),
                            "start_date": self._safe_get(voucher, 'start_date'),
                            "end_date": self._safe_get(voucher, 'end_date'),
                            "is_active": bool(self._safe_get(voucher, 'is_active', True)),
                            "usage_limit": self._safe_float(self._safe_get(voucher, 'usage_limit')),
                            "usage_count": self._safe_float(self._safe_get(voucher, 'usage_count')),
                            "created_at": self._safe_get(voucher, 'created_at'),
                            "updated_at": self._safe_get(voucher, 'updated_at'),
                            "minimum_order_amount": self._safe_float(self._safe_get(voucher, 'minimum_order_amount')),
                            "maximum_discount_amount": self._safe_float(self._safe_get(voucher, 'maximum_discount_amount'))
                        }
                        transformed_vouchers.append(transformed_voucher)
                    except Exception as e:
                        print(f"Error transforming voucher: {str(e)}")
                        traceback.print_exc()
                
                print(f"Transformed {len(transformed_vouchers)} vouchers")
                all_vouchers.extend(transformed_vouchers)
                
                # Check if there are more pages
                total_pages = self._safe_get(response, 'meta', {}).get('pagination', {}).get('total_pages', 0)
                has_more = page < total_pages
                page += 1
                
            except Exception as e:
                print(f"Error processing vouchers page {page}: {str(e)}")
                traceback.print_exc()
                break
                
        print(f"Returning {len(all_vouchers)} vouchers total")
        return all_vouchers
