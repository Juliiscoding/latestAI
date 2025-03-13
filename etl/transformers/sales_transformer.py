"""
Sales transformer for the Mercurios.ai ETL pipeline.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from etl.transformers.base_transformer import BaseTransformer
from etl.utils.logger import logger

class SalesTransformer(BaseTransformer):
    """
    Transformer for sales data.
    Handles normalization, feature engineering, and aggregation for sales.
    """
    
    def __init__(self):
        """Initialize the sales transformer."""
        super().__init__()
        self.sales_data = []
        self.daily_aggregations = {}
        self.weekly_aggregations = {}
        self.monthly_aggregations = {}
    
    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform sales data.
        
        Args:
            data: Sales data to transform
            
        Returns:
            Transformed sales data
        """
        # Create a copy to avoid modifying the original
        transformed = data.copy()
        
        # Normalize timestamps
        for ts_field in ['sale_date', 'created_at', 'updated_at']:
            if ts_field in transformed:
                transformed[ts_field] = self.standardize_timestamp(transformed.get(ts_field), ts_field)
        
        # Normalize product ID
        if 'article_id' in transformed:
            transformed['normalized_article_id'] = self.normalize_product_id(transformed['article_id'])
        
        # Handle currency conversions if needed
        if 'total_amount' in transformed and 'currency' in transformed:
            transformed['total_amount_eur'] = self.convert_currency(
                transformed.get('total_amount', 0.0),
                transformed.get('currency', 'EUR')
            )
        
        # Store the transformed data for aggregation
        self.sales_data.append(transformed)
        
        return transformed
    
    def transform_batch(self, data_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform a batch of sales data and generate aggregations.
        
        Args:
            data_batch: Batch of sales data to transform
            
        Returns:
            Batch of transformed sales data
        """
        # Reset sales data
        self.sales_data = []
        
        # Transform individual records
        transformed_batch = super().transform_batch(data_batch)
        
        # Generate aggregations
        self._generate_aggregations()
        
        return transformed_batch
    
    def _generate_aggregations(self):
        """Generate daily, weekly, and monthly sales aggregations."""
        if not self.sales_data:
            logger.warning("No sales data available for aggregation")
            return
        
        logger.info(f"Generating aggregations for {len(self.sales_data)} sales records")
        
        # Reset aggregations
        self.daily_aggregations = {}
        self.weekly_aggregations = {}
        self.monthly_aggregations = {}
        
        # Generate daily aggregations
        self._generate_daily_aggregations()
        
        # Generate weekly aggregations
        self._generate_weekly_aggregations()
        
        # Generate monthly aggregations
        self._generate_monthly_aggregations()
        
        logger.info(f"Generated {len(self.daily_aggregations)} daily, "
                   f"{len(self.weekly_aggregations)} weekly, and "
                   f"{len(self.monthly_aggregations)} monthly aggregations")
    
    def _generate_daily_aggregations(self):
        """Generate daily sales aggregations."""
        # Group sales by date, article, and location
        daily_sales = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        
        for sale in self.sales_data:
            sale_date = sale.get('sale_date')
            if not sale_date or not isinstance(sale_date, datetime):
                continue
            
            date_key = sale_date.strftime('%Y-%m-%d')
            article_id = sale.get('article_id', 'unknown')
            location_id = sale.get('branch_id', 'unknown')
            
            daily_sales[date_key][article_id][location_id].append(sale)
        
        # Calculate aggregations
        for date_key, articles in daily_sales.items():
            for article_id, locations in articles.items():
                for location_id, sales in locations.items():
                    # Calculate total quantity and amount
                    total_quantity = sum(sale.get('quantity', 0) for sale in sales)
                    total_amount = sum(sale.get('total_amount_eur', 0) for sale in sales)
                    avg_price = total_amount / total_quantity if total_quantity > 0 else 0
                    
                    # Store aggregation
                    agg_key = f"{date_key}_{article_id}_{location_id}"
                    self.daily_aggregations[agg_key] = {
                        'date': date_key,
                        'article_id': article_id,
                        'location_id': location_id,
                        'total_quantity': total_quantity,
                        'total_amount': total_amount,
                        'average_price': avg_price,
                        'transaction_count': len(sales)
                    }
    
    def _generate_weekly_aggregations(self):
        """Generate weekly sales aggregations."""
        # Group sales by week, article, and location
        weekly_sales = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        
        for sale in self.sales_data:
            sale_date = sale.get('sale_date')
            if not sale_date or not isinstance(sale_date, datetime):
                continue
            
            # Calculate the start of the week (Monday)
            start_of_week = sale_date - timedelta(days=sale_date.weekday())
            week_key = start_of_week.strftime('%Y-%m-%d')
            
            article_id = sale.get('article_id', 'unknown')
            location_id = sale.get('branch_id', 'unknown')
            
            weekly_sales[week_key][article_id][location_id].append(sale)
        
        # Calculate aggregations
        for week_key, articles in weekly_sales.items():
            for article_id, locations in articles.items():
                for location_id, sales in locations.items():
                    # Calculate total quantity and amount
                    total_quantity = sum(sale.get('quantity', 0) for sale in sales)
                    total_amount = sum(sale.get('total_amount_eur', 0) for sale in sales)
                    avg_price = total_amount / total_quantity if total_quantity > 0 else 0
                    
                    # Store aggregation
                    agg_key = f"{week_key}_{article_id}_{location_id}"
                    self.weekly_aggregations[agg_key] = {
                        'week_start_date': week_key,
                        'article_id': article_id,
                        'location_id': location_id,
                        'total_quantity': total_quantity,
                        'total_amount': total_amount,
                        'average_price': avg_price,
                        'transaction_count': len(sales),
                        'daily_average_quantity': total_quantity / 7
                    }
    
    def _generate_monthly_aggregations(self):
        """Generate monthly sales aggregations."""
        # Group sales by month, article, and location
        monthly_sales = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        
        for sale in self.sales_data:
            sale_date = sale.get('sale_date')
            if not sale_date or not isinstance(sale_date, datetime):
                continue
            
            month_key = sale_date.strftime('%Y-%m')
            article_id = sale.get('article_id', 'unknown')
            location_id = sale.get('branch_id', 'unknown')
            
            monthly_sales[month_key][article_id][location_id].append(sale)
        
        # Calculate aggregations
        for month_key, articles in monthly_sales.items():
            for article_id, locations in articles.items():
                for location_id, sales in locations.items():
                    # Calculate total quantity and amount
                    total_quantity = sum(sale.get('quantity', 0) for sale in sales)
                    total_amount = sum(sale.get('total_amount_eur', 0) for sale in sales)
                    avg_price = total_amount / total_quantity if total_quantity > 0 else 0
                    
                    # Get the number of days in the month
                    year, month = map(int, month_key.split('-'))
                    if month == 12:
                        next_month = datetime(year + 1, 1, 1)
                    else:
                        next_month = datetime(year, month + 1, 1)
                    days_in_month = (next_month - datetime(year, month, 1)).days
                    
                    # Store aggregation
                    agg_key = f"{month_key}_{article_id}_{location_id}"
                    self.monthly_aggregations[agg_key] = {
                        'month': month_key,
                        'article_id': article_id,
                        'location_id': location_id,
                        'total_quantity': total_quantity,
                        'total_amount': total_amount,
                        'average_price': avg_price,
                        'transaction_count': len(sales),
                        'daily_average_quantity': total_quantity / days_in_month
                    }
    
    def get_daily_aggregations(self) -> List[Dict[str, Any]]:
        """
        Get daily sales aggregations.
        
        Returns:
            List of daily sales aggregations
        """
        return list(self.daily_aggregations.values())
    
    def get_weekly_aggregations(self) -> List[Dict[str, Any]]:
        """
        Get weekly sales aggregations.
        
        Returns:
            List of weekly sales aggregations
        """
        return list(self.weekly_aggregations.values())
    
    def get_monthly_aggregations(self) -> List[Dict[str, Any]]:
        """
        Get monthly sales aggregations.
        
        Returns:
            List of monthly sales aggregations
        """
        return list(self.monthly_aggregations.values())
