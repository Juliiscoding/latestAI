"""
Article transformer for the Mercurios.ai ETL pipeline.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from etl.transformers.base_transformer import BaseTransformer
from etl.utils.logger import logger

class ArticleTransformer(BaseTransformer):
    """
    Transformer for article data.
    Handles normalization, feature engineering, and aggregation for articles.
    """
    
    def __init__(self, inventory_data: Optional[List[Dict[str, Any]]] = None, 
                 sales_data: Optional[List[Dict[str, Any]]] = None):
        """
        Initialize the article transformer.
        
        Args:
            inventory_data: Optional inventory data for feature engineering
            sales_data: Optional sales data for feature engineering
        """
        super().__init__()
        self.inventory_data = inventory_data or []
        self.sales_data = sales_data or []
        self.inventory_by_article = self._group_inventory_by_article()
        self.sales_by_article = self._group_sales_by_article()
    
    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform article data.
        
        Args:
            data: Article data to transform
            
        Returns:
            Transformed article data
        """
        # Create a copy to avoid modifying the original
        transformed = data.copy()
        
        # Normalize timestamps
        for ts_field in ['created_at', 'updated_at', 'last_sold_at', 'last_ordered_at']:
            if ts_field in transformed:
                transformed[ts_field] = self.standardize_timestamp(transformed.get(ts_field), ts_field)
        
        # Normalize product ID
        if 'article_id' in transformed:
            transformed['normalized_article_id'] = self.normalize_product_id(transformed['article_id'])
        
        # Handle currency conversions if needed
        if 'price' in transformed and 'currency' in transformed:
            transformed['price_eur'] = self.convert_currency(
                transformed.get('price', 0.0),
                transformed.get('currency', 'EUR')
            )
        
        # Add feature engineering
        article_id = transformed.get('article_id')
        if article_id:
            # Calculate inventory turnover rate
            transformed['inventory_turnover_rate'] = self._calculate_inventory_turnover(article_id)
            
            # Generate seasonal indices
            transformed['seasonal_indices'] = self._calculate_seasonal_indices(article_id)
            
            # Calculate lead time metrics
            transformed['lead_time_days'] = self._calculate_lead_time(article_id)
            
            # Categorize product
            transformed['product_category'] = self._categorize_product(transformed)
        
        return transformed
    
    def _group_inventory_by_article(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group inventory data by article ID.
        
        Returns:
            Dictionary of inventory data grouped by article ID
        """
        result = {}
        for inv in self.inventory_data:
            article_id = inv.get('article_id')
            if article_id:
                if article_id not in result:
                    result[article_id] = []
                result[article_id].append(inv)
        return result
    
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
    
    def _calculate_inventory_turnover(self, article_id: str) -> float:
        """
        Calculate inventory turnover rate for an article.
        Inventory Turnover = Cost of Goods Sold / Average Inventory
        
        Args:
            article_id: Article ID
            
        Returns:
            Inventory turnover rate
        """
        # Get sales for this article
        sales = self.sales_by_article.get(article_id, [])
        if not sales:
            return 0.0
        
        # Calculate cost of goods sold (sum of all sales)
        cogs = sum(sale.get('total_amount', 0) for sale in sales)
        
        # Get inventory for this article
        inventory = self.inventory_by_article.get(article_id, [])
        if not inventory:
            return 0.0
        
        # Calculate average inventory
        avg_inventory = sum(inv.get('quantity', 0) * inv.get('cost', 0) for inv in inventory) / len(inventory)
        
        # Calculate inventory turnover
        if avg_inventory == 0:
            return 0.0
        
        return cogs / avg_inventory
    
    def _calculate_seasonal_indices(self, article_id: str) -> Dict[str, float]:
        """
        Calculate seasonal indices for an article.
        
        Args:
            article_id: Article ID
            
        Returns:
            Dictionary of seasonal indices by month
        """
        # Get sales for this article
        sales = self.sales_by_article.get(article_id, [])
        if not sales:
            return {str(i): 1.0 for i in range(1, 13)}
        
        # Group sales by month
        sales_by_month = {}
        for sale in sales:
            sale_date = sale.get('sale_date')
            if not sale_date:
                continue
            
            if isinstance(sale_date, str):
                try:
                    sale_date = datetime.fromisoformat(sale_date.replace('Z', '+00:00'))
                except ValueError:
                    continue
            
            month = sale_date.month
            if month not in sales_by_month:
                sales_by_month[month] = []
            sales_by_month[month].append(sale)
        
        # Calculate average sales per month
        avg_sales_by_month = {}
        for month, month_sales in sales_by_month.items():
            avg_sales_by_month[month] = sum(sale.get('quantity', 0) for sale in month_sales) / len(month_sales)
        
        # Calculate overall average
        if not avg_sales_by_month:
            return {str(i): 1.0 for i in range(1, 13)}
        
        overall_avg = sum(avg_sales_by_month.values()) / len(avg_sales_by_month)
        
        # Calculate seasonal indices
        seasonal_indices = {}
        for month in range(1, 13):
            if month in avg_sales_by_month and overall_avg > 0:
                seasonal_indices[str(month)] = avg_sales_by_month[month] / overall_avg
            else:
                seasonal_indices[str(month)] = 1.0
        
        return seasonal_indices
    
    def _calculate_lead_time(self, article_id: str) -> float:
        """
        Calculate lead time for an article.
        Lead time is the average time between order and delivery.
        
        Args:
            article_id: Article ID
            
        Returns:
            Average lead time in days
        """
        # In a real implementation, this would use order and delivery data
        # For now, return a default value
        return 7.0
    
    def _categorize_product(self, article_data: Dict[str, Any]) -> str:
        """
        Categorize a product based on its attributes.
        
        Args:
            article_data: Article data
            
        Returns:
            Product category
        """
        # In a real implementation, this would use a more sophisticated categorization algorithm
        # For now, use the category from the data if available
        if 'category' in article_data:
            return article_data['category']
        
        # Try to categorize based on name or description
        name = article_data.get('name', '').lower()
        description = article_data.get('description', '').lower()
        
        # Simple keyword-based categorization
        keywords = {
            'food': ['food', 'meal', 'snack', 'drink', 'beverage'],
            'electronics': ['electronic', 'device', 'gadget', 'computer', 'phone'],
            'clothing': ['cloth', 'shirt', 'pant', 'dress', 'shoe'],
            'furniture': ['furniture', 'chair', 'table', 'desk', 'sofa'],
            'household': ['household', 'kitchen', 'bathroom', 'cleaning'],
        }
        
        for category, category_keywords in keywords.items():
            for keyword in category_keywords:
                if keyword in name or keyword in description:
                    return category
        
        return 'uncategorized'
