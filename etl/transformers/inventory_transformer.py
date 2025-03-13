"""
Inventory transformer for the Mercurios.ai ETL pipeline.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from etl.transformers.base_transformer import BaseTransformer
from etl.utils.logger import logger

class InventoryTransformer(BaseTransformer):
    """
    Transformer for inventory data.
    Handles normalization, feature engineering, and aggregation for inventory.
    """
    
    def __init__(self, sales_data: Optional[List[Dict[str, Any]]] = None):
        """
        Initialize the inventory transformer.
        
        Args:
            sales_data: Optional sales data for feature engineering
        """
        super().__init__()
        self.sales_data = sales_data or []
        self.inventory_data = []
        self.inventory_history = {}
        self.sales_by_article = self._group_sales_by_article()
    
    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform inventory data.
        
        Args:
            data: Inventory data to transform
            
        Returns:
            Transformed inventory data
        """
        # Create a copy to avoid modifying the original
        transformed = data.copy()
        
        # Normalize timestamps
        for ts_field in ['timestamp', 'created_at', 'updated_at']:
            if ts_field in transformed:
                transformed[ts_field] = self.standardize_timestamp(transformed.get(ts_field), ts_field)
        
        # Normalize product ID
        if 'article_id' in transformed:
            transformed['normalized_article_id'] = self.normalize_product_id(transformed['article_id'])
        
        # Add inventory metrics
        article_id = transformed.get('article_id')
        if article_id:
            # Calculate days of supply
            transformed['days_of_supply'] = self._calculate_days_of_supply(article_id, transformed)
            
            # Calculate reorder point
            transformed['reorder_point'] = self._calculate_reorder_point(article_id, transformed)
            
            # Calculate safety stock
            transformed['safety_stock'] = self._calculate_safety_stock(article_id, transformed)
            
            # Calculate stock status
            transformed['stock_status'] = self._calculate_stock_status(transformed)
        
        # Store the transformed data for history tracking
        self.inventory_data.append(transformed)
        
        return transformed
    
    def transform_batch(self, data_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform a batch of inventory data and generate history.
        
        Args:
            data_batch: Batch of inventory data to transform
            
        Returns:
            Batch of transformed inventory data
        """
        # Reset inventory data
        self.inventory_data = []
        
        # Transform individual records
        transformed_batch = super().transform_batch(data_batch)
        
        # Generate inventory history
        self._generate_inventory_history()
        
        return transformed_batch
    
    def _group_sales_by_article(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group sales data by article ID.
        
        Returns:
            Dictionary of sales data grouped by article ID
        """
        result = {}
        for sale in self.sales_data:
            article_id = sale.get('article_id')
            if article_id:
                if article_id not in result:
                    result[article_id] = []
                result[article_id].append(sale)
        return result
    
    def _calculate_days_of_supply(self, article_id: str, inventory: Dict[str, Any]) -> float:
        """
        Calculate days of supply for an article.
        Days of Supply = Current Inventory / Average Daily Sales
        
        Args:
            article_id: Article ID
            inventory: Inventory data
            
        Returns:
            Days of supply
        """
        # Get current inventory
        current_inventory = inventory.get('quantity', 0)
        if current_inventory == 0:
            return 0.0
        
        # Get sales for this article
        sales = self.sales_by_article.get(article_id, [])
        if not sales:
            return 30.0  # Default to 30 days if no sales data
        
        # Calculate average daily sales
        # Group sales by date
        sales_by_date = defaultdict(list)
        for sale in sales:
            sale_date = sale.get('sale_date')
            if not sale_date:
                continue
            
            if isinstance(sale_date, str):
                try:
                    sale_date = datetime.fromisoformat(sale_date.replace('Z', '+00:00'))
                except ValueError:
                    continue
            
            date_key = sale_date.strftime('%Y-%m-%d')
            sales_by_date[date_key].append(sale)
        
        if not sales_by_date:
            return 30.0  # Default to 30 days if no valid sales data
        
        # Calculate total quantity sold per day
        daily_quantities = []
        for date_key, date_sales in sales_by_date.items():
            daily_quantity = sum(sale.get('quantity', 0) for sale in date_sales)
            daily_quantities.append(daily_quantity)
        
        # Calculate average daily sales
        avg_daily_sales = sum(daily_quantities) / len(daily_quantities)
        
        if avg_daily_sales == 0:
            return 30.0  # Default to 30 days if no sales
        
        # Calculate days of supply
        days_of_supply = current_inventory / avg_daily_sales
        
        return days_of_supply
    
    def _calculate_reorder_point(self, article_id: str, inventory: Dict[str, Any]) -> int:
        """
        Calculate reorder point for an article.
        Reorder Point = (Average Daily Sales * Lead Time) + Safety Stock
        
        Args:
            article_id: Article ID
            inventory: Inventory data
            
        Returns:
            Reorder point
        """
        # Get sales for this article
        sales = self.sales_by_article.get(article_id, [])
        if not sales:
            return 0
        
        # Calculate average daily sales
        # Group sales by date
        sales_by_date = defaultdict(list)
        for sale in sales:
            sale_date = sale.get('sale_date')
            if not sale_date:
                continue
            
            if isinstance(sale_date, str):
                try:
                    sale_date = datetime.fromisoformat(sale_date.replace('Z', '+00:00'))
                except ValueError:
                    continue
            
            date_key = sale_date.strftime('%Y-%m-%d')
            sales_by_date[date_key].append(sale)
        
        if not sales_by_date:
            return 0
        
        # Calculate total quantity sold per day
        daily_quantities = []
        for date_key, date_sales in sales_by_date.items():
            daily_quantity = sum(sale.get('quantity', 0) for sale in date_sales)
            daily_quantities.append(daily_quantity)
        
        # Calculate average daily sales
        avg_daily_sales = sum(daily_quantities) / len(daily_quantities)
        
        # Get lead time (default to 7 days)
        lead_time = inventory.get('lead_time_days', 7)
        
        # Calculate safety stock
        safety_stock = self._calculate_safety_stock(article_id, inventory)
        
        # Calculate reorder point
        reorder_point = int((avg_daily_sales * lead_time) + safety_stock)
        
        return reorder_point
    
    def _calculate_safety_stock(self, article_id: str, inventory: Dict[str, Any]) -> int:
        """
        Calculate safety stock for an article.
        Safety Stock = Z * Standard Deviation of Demand * Square Root of Lead Time
        
        Args:
            article_id: Article ID
            inventory: Inventory data
            
        Returns:
            Safety stock
        """
        # Get sales for this article
        sales = self.sales_by_article.get(article_id, [])
        if not sales:
            return 0
        
        # Calculate standard deviation of daily sales
        # Group sales by date
        sales_by_date = defaultdict(list)
        for sale in sales:
            sale_date = sale.get('sale_date')
            if not sale_date:
                continue
            
            if isinstance(sale_date, str):
                try:
                    sale_date = datetime.fromisoformat(sale_date.replace('Z', '+00:00'))
                except ValueError:
                    continue
            
            date_key = sale_date.strftime('%Y-%m-%d')
            sales_by_date[date_key].append(sale)
        
        if not sales_by_date:
            return 0
        
        # Calculate total quantity sold per day
        daily_quantities = []
        for date_key, date_sales in sales_by_date.items():
            daily_quantity = sum(sale.get('quantity', 0) for sale in date_sales)
            daily_quantities.append(daily_quantity)
        
        if not daily_quantities:
            return 0
        
        # Calculate mean
        mean = sum(daily_quantities) / len(daily_quantities)
        
        # Calculate standard deviation
        variance = sum((x - mean) ** 2 for x in daily_quantities) / len(daily_quantities)
        std_dev = variance ** 0.5
        
        # Get lead time (default to 7 days)
        lead_time = inventory.get('lead_time_days', 7)
        
        # Calculate safety stock (using Z = 1.645 for 95% service level)
        z = 1.645
        safety_stock = int(z * std_dev * (lead_time ** 0.5))
        
        return safety_stock
    
    def _calculate_stock_status(self, inventory: Dict[str, Any]) -> str:
        """
        Calculate stock status for an article.
        
        Args:
            inventory: Inventory data
            
        Returns:
            Stock status
        """
        quantity = inventory.get('quantity', 0)
        reorder_point = inventory.get('reorder_point', 0)
        
        if quantity <= 0:
            return 'out_of_stock'
        elif quantity <= reorder_point:
            return 'low_stock'
        else:
            return 'in_stock'
    
    def _generate_inventory_history(self):
        """Generate inventory history by product and location."""
        if not self.inventory_data:
            logger.warning("No inventory data available for history tracking")
            return
        
        logger.info(f"Generating inventory history for {len(self.inventory_data)} inventory records")
        
        # Reset inventory history
        self.inventory_history = {}
        
        # Group inventory by article and location
        inventory_by_article_location = defaultdict(list)
        
        for inventory in self.inventory_data:
            article_id = inventory.get('article_id', 'unknown')
            location_id = inventory.get('branch_id', 'unknown')
            timestamp = inventory.get('timestamp')
            
            if not timestamp or not isinstance(timestamp, datetime):
                continue
            
            key = f"{article_id}_{location_id}"
            inventory_by_article_location[key].append(inventory)
        
        # Sort inventory records by timestamp
        for key, records in inventory_by_article_location.items():
            sorted_records = sorted(records, key=lambda x: x.get('timestamp', datetime.min))
            self.inventory_history[key] = sorted_records
        
        logger.info(f"Generated inventory history for {len(self.inventory_history)} article-location combinations")
    
    def get_inventory_history(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get inventory history by product and location.
        
        Returns:
            Dictionary of inventory history by product and location
        """
        return self.inventory_history
