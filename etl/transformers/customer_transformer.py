"""
Customer transformer for the Mercurios.ai ETL pipeline.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from etl.transformers.base_transformer import BaseTransformer
from etl.utils.logger import logger

class CustomerTransformer(BaseTransformer):
    """
    Transformer for customer data.
    Handles normalization, feature engineering, and aggregation for customers.
    """
    
    def __init__(self, sales_data: Optional[List[Dict[str, Any]]] = None, 
                 orders_data: Optional[List[Dict[str, Any]]] = None):
        """
        Initialize the customer transformer.
        
        Args:
            sales_data: Optional sales data for feature engineering
            orders_data: Optional orders data for feature engineering
        """
        super().__init__()
        self.sales_data = sales_data or []
        self.orders_data = orders_data or []
        self.sales_by_customer = self._group_sales_by_customer()
        self.orders_by_customer = self._group_orders_by_customer()
        self.customer_purchase_patterns = {}
    
    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform customer data.
        
        Args:
            data: Customer data to transform
            
        Returns:
            Transformed customer data
        """
        # Create a copy to avoid modifying the original
        transformed = data.copy()
        
        # Normalize timestamps
        for ts_field in ['created_at', 'updated_at', 'last_purchase_date']:
            if ts_field in transformed:
                transformed[ts_field] = self.standardize_timestamp(transformed.get(ts_field), ts_field)
        
        # Add customer metrics
        customer_id = transformed.get('customer_id')
        if customer_id:
            # Calculate customer lifetime value
            transformed['lifetime_value'] = self._calculate_lifetime_value(customer_id)
            
            # Calculate purchase frequency
            transformed['purchase_frequency'] = self._calculate_purchase_frequency(customer_id)
            
            # Calculate average order value
            transformed['average_order_value'] = self._calculate_average_order_value(customer_id)
            
            # Calculate recency
            transformed['recency_days'] = self._calculate_recency(customer_id)
            
            # Calculate customer segment
            transformed['customer_segment'] = self._calculate_customer_segment(transformed)
            
            # Generate purchase patterns
            self._generate_purchase_patterns(customer_id, transformed)
        
        return transformed
    
    def _group_sales_by_customer(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group sales data by customer ID.
        
        Returns:
            Dictionary of sales data grouped by customer ID
        """
        result = {}
        for sale in self.sales_data:
            customer_id = sale.get('customer_id')
            if customer_id:
                if customer_id not in result:
                    result[customer_id] = []
                result[customer_id].append(sale)
        return result
    
    def _group_orders_by_customer(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group orders data by customer ID.
        
        Returns:
            Dictionary of orders data grouped by customer ID
        """
        result = {}
        for order in self.orders_data:
            customer_id = order.get('customer_id')
            if customer_id:
                if customer_id not in result:
                    result[customer_id] = []
                result[customer_id].append(order)
        return result
    
    def _calculate_lifetime_value(self, customer_id: str) -> float:
        """
        Calculate customer lifetime value.
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Customer lifetime value
        """
        # Get sales for this customer
        sales = self.sales_by_customer.get(customer_id, [])
        if not sales:
            return 0.0
        
        # Calculate total revenue
        total_revenue = sum(sale.get('total_amount_eur', 0) for sale in sales)
        
        return total_revenue
    
    def _calculate_purchase_frequency(self, customer_id: str) -> float:
        """
        Calculate customer purchase frequency (orders per month).
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Purchase frequency (orders per month)
        """
        # Get orders for this customer
        orders = self.orders_by_customer.get(customer_id, [])
        if not orders:
            return 0.0
        
        # Get order dates
        order_dates = []
        for order in orders:
            order_date = order.get('order_date')
            if not order_date:
                continue
            
            if isinstance(order_date, str):
                try:
                    order_date = datetime.fromisoformat(order_date.replace('Z', '+00:00'))
                except ValueError:
                    continue
            
            order_dates.append(order_date)
        
        if not order_dates:
            return 0.0
        
        # Calculate date range
        min_date = min(order_dates)
        max_date = max(order_dates)
        
        # Calculate months between first and last order
        months = (max_date.year - min_date.year) * 12 + max_date.month - min_date.month
        if months == 0:
            months = 1  # Minimum 1 month to avoid division by zero
        
        # Calculate frequency
        frequency = len(order_dates) / months
        
        return frequency
    
    def _calculate_average_order_value(self, customer_id: str) -> float:
        """
        Calculate customer average order value.
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Average order value
        """
        # Get orders for this customer
        orders = self.orders_by_customer.get(customer_id, [])
        if not orders:
            return 0.0
        
        # Calculate total order value
        total_value = sum(order.get('total_amount_eur', 0) for order in orders)
        
        # Calculate average
        return total_value / len(orders)
    
    def _calculate_recency(self, customer_id: str) -> int:
        """
        Calculate customer recency (days since last purchase).
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Days since last purchase
        """
        # Get sales for this customer
        sales = self.sales_by_customer.get(customer_id, [])
        if not sales:
            return 365  # Default to 1 year if no sales
        
        # Get sale dates
        sale_dates = []
        for sale in sales:
            sale_date = sale.get('sale_date')
            if not sale_date:
                continue
            
            if isinstance(sale_date, str):
                try:
                    sale_date = datetime.fromisoformat(sale_date.replace('Z', '+00:00'))
                except ValueError:
                    continue
            
            sale_dates.append(sale_date)
        
        if not sale_dates:
            return 365  # Default to 1 year if no valid sale dates
        
        # Calculate days since last purchase
        last_purchase = max(sale_dates)
        days_since = (datetime.now() - last_purchase).days
        
        return max(0, days_since)
    
    def _calculate_customer_segment(self, customer_data: Dict[str, Any]) -> str:
        """
        Calculate customer segment based on RFM (Recency, Frequency, Monetary) analysis.
        
        Args:
            customer_data: Customer data
            
        Returns:
            Customer segment
        """
        # Get RFM values
        recency = customer_data.get('recency_days', 365)
        frequency = customer_data.get('purchase_frequency', 0)
        monetary = customer_data.get('lifetime_value', 0)
        
        # Calculate RFM scores (1-5, 5 being the best)
        recency_score = 5 if recency <= 30 else 4 if recency <= 90 else 3 if recency <= 180 else 2 if recency <= 365 else 1
        frequency_score = 5 if frequency >= 3 else 4 if frequency >= 2 else 3 if frequency >= 1 else 2 if frequency > 0 else 1
        monetary_score = 5 if monetary >= 10000 else 4 if monetary >= 5000 else 3 if monetary >= 1000 else 2 if monetary > 0 else 1
        
        # Calculate overall RFM score
        rfm_score = recency_score * 100 + frequency_score * 10 + monetary_score
        
        # Determine segment
        if rfm_score >= 500:
            return 'champions'
        elif rfm_score >= 400:
            return 'loyal_customers'
        elif rfm_score >= 300:
            return 'potential_loyalists'
        elif recency_score >= 4 and (frequency_score + monetary_score) <= 5:
            return 'new_customers'
        elif recency_score <= 2 and (frequency_score + monetary_score) <= 5:
            return 'at_risk'
        elif recency_score <= 2 and (frequency_score + monetary_score) > 5:
            return 'cant_lose_them'
        elif recency_score >= 3 and (frequency_score + monetary_score) <= 4:
            return 'promising'
        elif recency_score >= 3 and (frequency_score + monetary_score) > 4:
            return 'need_attention'
        else:
            return 'about_to_sleep'
    
    def _generate_purchase_patterns(self, customer_id: str, customer_data: Dict[str, Any]):
        """
        Generate purchase patterns for a customer.
        
        Args:
            customer_id: Customer ID
            customer_data: Customer data
        """
        # Get sales for this customer
        sales = self.sales_by_customer.get(customer_id, [])
        if not sales:
            return
        
        # Analyze purchase patterns
        patterns = {
            'preferred_categories': self._get_preferred_categories(sales),
            'preferred_products': self._get_preferred_products(sales),
            'purchase_time_distribution': self._get_purchase_time_distribution(sales),
            'purchase_day_distribution': self._get_purchase_day_distribution(sales),
            'purchase_month_distribution': self._get_purchase_month_distribution(sales),
            'basket_analysis': self._get_basket_analysis(sales),
            'average_basket_size': self._get_average_basket_size(sales)
        }
        
        # Store patterns
        self.customer_purchase_patterns[customer_id] = patterns
    
    def _get_preferred_categories(self, sales: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Get preferred categories for a customer.
        
        Args:
            sales: Sales data for the customer
            
        Returns:
            Dictionary of category counts
        """
        category_counts = defaultdict(int)
        
        for sale in sales:
            category = sale.get('category', 'unknown')
            category_counts[category] += 1
        
        # Sort by count
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        
        return dict(sorted_categories[:5])  # Return top 5
    
    def _get_preferred_products(self, sales: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Get preferred products for a customer.
        
        Args:
            sales: Sales data for the customer
            
        Returns:
            Dictionary of product counts
        """
        product_counts = defaultdict(int)
        
        for sale in sales:
            product_id = sale.get('article_id', 'unknown')
            product_counts[product_id] += 1
        
        # Sort by count
        sorted_products = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)
        
        return dict(sorted_products[:10])  # Return top 10
    
    def _get_purchase_time_distribution(self, sales: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Get purchase time distribution for a customer.
        
        Args:
            sales: Sales data for the customer
            
        Returns:
            Dictionary of hour counts
        """
        hour_counts = defaultdict(int)
        
        for sale in sales:
            sale_date = sale.get('sale_date')
            if not sale_date or not isinstance(sale_date, datetime):
                continue
            
            hour = sale_date.hour
            hour_counts[str(hour)] += 1
        
        return dict(hour_counts)
    
    def _get_purchase_day_distribution(self, sales: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Get purchase day distribution for a customer.
        
        Args:
            sales: Sales data for the customer
            
        Returns:
            Dictionary of day counts
        """
        day_counts = defaultdict(int)
        
        for sale in sales:
            sale_date = sale.get('sale_date')
            if not sale_date or not isinstance(sale_date, datetime):
                continue
            
            day = sale_date.strftime('%A')  # Day name
            day_counts[day] += 1
        
        return dict(day_counts)
    
    def _get_purchase_month_distribution(self, sales: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Get purchase month distribution for a customer.
        
        Args:
            sales: Sales data for the customer
            
        Returns:
            Dictionary of month counts
        """
        month_counts = defaultdict(int)
        
        for sale in sales:
            sale_date = sale.get('sale_date')
            if not sale_date or not isinstance(sale_date, datetime):
                continue
            
            month = sale_date.strftime('%B')  # Month name
            month_counts[month] += 1
        
        return dict(month_counts)
    
    def _get_basket_analysis(self, sales: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get basket analysis for a customer.
        
        Args:
            sales: Sales data for the customer
            
        Returns:
            List of basket analyses
        """
        # Group sales by transaction
        transactions = defaultdict(list)
        
        for sale in sales:
            transaction_id = sale.get('transaction_id', 'unknown')
            transactions[transaction_id].append(sale)
        
        # Analyze baskets
        basket_analyses = []
        
        for transaction_id, transaction_sales in transactions.items():
            if len(transaction_sales) <= 1:
                continue  # Skip single-item baskets
            
            # Get products in this basket
            products = [sale.get('article_id', 'unknown') for sale in transaction_sales]
            
            # Get total amount
            total_amount = sum(sale.get('total_amount_eur', 0) for sale in transaction_sales)
            
            # Get date
            sale_date = None
            for sale in transaction_sales:
                if sale.get('sale_date'):
                    sale_date = sale.get('sale_date')
                    break
            
            basket_analyses.append({
                'transaction_id': transaction_id,
                'date': sale_date,
                'products': products,
                'product_count': len(products),
                'total_amount': total_amount
            })
        
        return basket_analyses
    
    def _get_average_basket_size(self, sales: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Get average basket size for a customer.
        
        Args:
            sales: Sales data for the customer
            
        Returns:
            Dictionary with average basket metrics
        """
        # Group sales by transaction
        transactions = defaultdict(list)
        
        for sale in sales:
            transaction_id = sale.get('transaction_id', 'unknown')
            transactions[transaction_id].append(sale)
        
        if not transactions:
            return {
                'average_items': 0.0,
                'average_amount': 0.0
            }
        
        # Calculate metrics
        total_items = sum(len(transaction_sales) for transaction_sales in transactions.values())
        total_amount = sum(sum(sale.get('total_amount_eur', 0) for sale in transaction_sales) 
                          for transaction_sales in transactions.values())
        
        return {
            'average_items': total_items / len(transactions),
            'average_amount': total_amount / len(transactions)
        }
    
    def get_customer_purchase_patterns(self) -> Dict[str, Dict[str, Any]]:
        """
        Get customer purchase patterns.
        
        Returns:
            Dictionary of customer purchase patterns
        """
        return self.customer_purchase_patterns
