"""
Data enhancement and aggregation module for the ProHandel Lambda function.

This module provides functions to enhance and aggregate data from the ProHandel API
before sending it to Fivetran.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DataEnhancer:
    """
    Enhances data with additional fields, calculations, and aggregations.
    """
    
    @staticmethod
    def enhance_article_data(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enhance article data with additional fields.
        
        Args:
            articles: List of article data
            
        Returns:
            Enhanced article data
        """
        if not articles:
            return articles
            
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(articles)
        
        # Calculate profit margin
        if 'price' in df.columns and 'cost' in df.columns:
            df['profit_margin'] = ((df['price'] - df['cost']) / df['price'] * 100).round(2)
            
        # Calculate price tier
        if 'price' in df.columns:
            df['price_tier'] = pd.cut(
                df['price'], 
                bins=[0, 10, 50, 100, 500, float('inf')],
                labels=['Budget', 'Economy', 'Standard', 'Premium', 'Luxury']
            ).astype(str)
        
        # Convert back to list of dictionaries
        return df.to_dict('records')
    
    @staticmethod
    def enhance_customer_data(customers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enhance customer data with additional fields.
        
        Args:
            customers: List of customer data
            
        Returns:
            Enhanced customer data
        """
        if not customers:
            return customers
            
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(customers)
        
        # Create full address
        address_fields = ['street', 'postalCode', 'city', 'country']
        if all(field in df.columns for field in address_fields):
            df['full_address'] = df.apply(
                lambda row: f"{row['street']}, {row['postalCode']} {row['city']}, {row['country']}",
                axis=1
            )
        
        # Convert back to list of dictionaries
        return df.to_dict('records')
    
    @staticmethod
    def enhance_order_data(orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enhance order data with additional fields.
        
        Args:
            orders: List of order data
            
        Returns:
            Enhanced order data
        """
        if not orders:
            return orders
            
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(orders)
        
        # Calculate delivery time
        if 'orderDate' in df.columns and 'deliveryDate' in df.columns:
            df['orderDate'] = pd.to_datetime(df['orderDate'])
            df['deliveryDate'] = pd.to_datetime(df['deliveryDate'])
            
            # Calculate delivery time in days
            df['delivery_time_days'] = (df['deliveryDate'] - df['orderDate']).dt.days
            
            # Calculate order age in days
            now = datetime.now()
            df['order_age_days'] = (now - df['orderDate']).dt.days
        
        # Convert back to list of dictionaries
        return df.to_dict('records')
    
    @staticmethod
    def enhance_sale_data(sales: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enhance sale data with additional fields.
        
        Args:
            sales: List of sale data
            
        Returns:
            Enhanced sale data
        """
        if not sales:
            return sales
            
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(sales)
        
        # Calculate sale age
        if 'saleDate' in df.columns:
            df['saleDate'] = pd.to_datetime(df['saleDate'])
            
            # Calculate sale age in days
            now = datetime.now()
            df['sale_age_days'] = (now - df['saleDate']).dt.days
        
        # Convert back to list of dictionaries
        return df.to_dict('records')
    
    @staticmethod
    def enhance_inventory_data(inventory: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enhance inventory data with additional fields.
        
        Args:
            inventory: List of inventory data
            
        Returns:
            Enhanced inventory data
        """
        if not inventory:
            return inventory
            
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(inventory)
        
        # Add stock status
        if 'quantity' in df.columns:
            df['stock_status'] = pd.cut(
                df['quantity'], 
                bins=[-float('inf'), 0, 5, 20, float('inf')],
                labels=['Out of Stock', 'Low Stock', 'Medium Stock', 'Well Stocked']
            ).astype(str)
        
        # Convert back to list of dictionaries
        return df.to_dict('records')
    
    @staticmethod
    def enhance_shop(shop_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance shop data with additional fields.
        
        Args:
            shop_data: Shop data dictionary (branch data from ProHandel API)
            
        Returns:
            Enhanced shop data
        """
        # Create a copy to avoid modifying the original
        enhanced_shop = shop_data.copy()
        
        # Add shop type categorization based on name or other attributes
        # Branch data uses name1, name2, name3 instead of a single name field
        shop_name = ""
        if 'name1' in enhanced_shop and enhanced_shop['name1']:
            shop_name = enhanced_shop['name1'].lower()
        
        # Also check searchTerm which might be more useful for categorization
        search_term = ""
        if 'searchTerm' in enhanced_shop and enhanced_shop['searchTerm']:
            search_term = enhanced_shop['searchTerm'].lower()
        
        # Check isWebshop field if available
        is_webshop = enhanced_shop.get('isWebshop', False)
        
        # Determine shop type based on available information
        if is_webshop or 'online' in shop_name or 'web' in shop_name or 'digital' in shop_name or 'online' in search_term:
            enhanced_shop['shop_type'] = 'Online'
            enhanced_shop['is_online'] = True
        elif 'warehouse' in shop_name or 'storage' in shop_name or 'warehouse' in search_term:
            enhanced_shop['shop_type'] = 'Warehouse'
            enhanced_shop['is_online'] = False
        elif 'outlet' in shop_name or 'outlet' in search_term:
            enhanced_shop['shop_type'] = 'Outlet'
            enhanced_shop['is_online'] = False
        else:
            enhanced_shop['shop_type'] = 'Retail'
            enhanced_shop['is_online'] = False
            
        return enhanced_shop
    
    # Add instance methods that call the static methods for easier use
    def enhance_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Instance method wrapper for enhance_article_data."""
        return self.enhance_article_data([article])[0] if article else article
        
    def enhance_customer(self, customer: Dict[str, Any]) -> Dict[str, Any]:
        """Instance method wrapper for enhance_customer_data."""
        return self.enhance_customer_data([customer])[0] if customer else customer
        
    def enhance_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Instance method wrapper for enhance_order_data."""
        return self.enhance_order_data([order])[0] if order else order
        
    def enhance_sale(self, sale: Dict[str, Any]) -> Dict[str, Any]:
        """Instance method wrapper for enhance_sale_data."""
        return self.enhance_sale_data([sale])[0] if sale else sale
        
    def enhance_inventory(self, inventory: Dict[str, Any]) -> Dict[str, Any]:
        """Instance method wrapper for enhance_inventory_data."""
        return self.enhance_inventory_data([inventory])[0] if inventory else inventory


class DataAggregator:
    """
    Aggregates data for reporting and analysis.
    """
    
    @staticmethod
    def aggregate_sales_by_date(sales: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Aggregate sales by date.
        
        Args:
            sales: List of sale data
            
        Returns:
            Aggregated sales data by date
        """
        if not sales:
            return []
            
        # Convert to DataFrame
        df = pd.DataFrame(sales)
        
        # Check if required date column exists
        date_column = None
        for col in ['date', 'saleDate', 'orderDate', 'createdAt']:
            if col in df.columns:
                date_column = col
                break
                
        if not date_column:
            logger.warning("No date column found in sales data")
            return []
            
        # Convert date to datetime if it's not already
        if df[date_column].dtype != 'datetime64[ns]':
            try:
                df[date_column] = pd.to_datetime(df[date_column])
            except Exception as e:
                logger.warning(f"Failed to convert {date_column} to datetime: {str(e)}")
                return []
        
        # Extract date part only
        df['sale_date'] = df[date_column].dt.date
        
        # Determine which columns to use for aggregation based on what's available
        agg_columns = {}
        
        if 'quantity' in df.columns:
            agg_columns['quantity'] = 'sum'
        
        # Check for price/amount columns - different APIs might use different names
        amount_column = None
        for col in ['total', 'amount', 'price']:
            if col in df.columns:
                amount_column = col
                break
                
        if amount_column:
            agg_columns[amount_column] = 'sum'
            
        # Add count aggregation using a column that's guaranteed to exist
        count_column = df.columns[0]  # Use first column for counting
        agg_columns[count_column] = 'count'
        
        # If we don't have enough columns to aggregate, return empty
        if len(agg_columns) < 2:  # Need at least 2 aggregations to be useful
            logger.warning(f"Not enough columns for meaningful aggregation. Available columns: {df.columns.tolist()}")
            return []
        
        # Aggregate by date
        agg_df = df.groupby('sale_date').agg(agg_columns).reset_index()
        
        # Rename columns to standardized names
        column_mapping = {'sale_date': 'date'}
        
        if 'quantity' in agg_columns:
            column_mapping['quantity'] = 'total_quantity'
            
        if amount_column:
            column_mapping[amount_column] = 'total_amount'
            
        column_mapping[count_column] = 'sale_count'
        
        agg_df = agg_df.rename(columns=column_mapping)
        
        # Add aggregation type
        agg_df['aggregation_type'] = 'daily'
        
        # Convert dates to string for JSON serialization
        agg_df['date'] = agg_df['date'].astype(str)
        
        # Convert to list of dictionaries
        return agg_df.to_dict('records')
        
    @staticmethod
    def aggregate_sales_by_article(sales: List[Dict[str, Any]], articles: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Aggregate sales by article.
        
        Args:
            sales: List of sale data
            articles: Optional list of article data to enrich the aggregation
            
        Returns:
            Aggregated sales data by article
        """
        if not sales:
            return []
            
        # Convert to DataFrame
        df = pd.DataFrame(sales)
        
        # Identify the article column
        article_column = None
        for col in ['articleNumber', 'article', 'articleId']:
            if col in df.columns:
                article_column = col
                break
                
        if not article_column:
            logger.warning("No article column found in sales data")
            return []
            
        # Identify the amount column
        amount_column = None
        for col in ['amount', 'total', 'price', 'totalAmount']:
            if col in df.columns:
                amount_column = col
                break
                
        # Identify the count column (for counting sales)
        count_column = 'id' if 'id' in df.columns else df.columns[0]
        
        # Define aggregation columns
        agg_columns = {}
        if 'quantity' in df.columns:
            agg_columns['quantity'] = 'sum'
            
        if amount_column:
            agg_columns[amount_column] = 'sum'
            
        agg_columns[count_column] = 'count'
        
        # Aggregate by article
        agg_df = df.groupby(article_column).agg(agg_columns).reset_index()
        
        # Rename columns
        column_mapping = {}
        
        # We'll keep the original article column name to avoid conflicts
        # DO NOT rename the article column as it causes the "cannot insert articleNumber, already exists" error
        
        if 'quantity' in agg_columns:
            column_mapping['quantity'] = 'total_quantity'
            
        if amount_column:
            column_mapping[amount_column] = 'total_amount'
            
        column_mapping[count_column] = 'sale_count'
        
        agg_df = agg_df.rename(columns=column_mapping)
        
        # Add aggregation type
        agg_df['aggregation_type'] = 'article'
        
        # Add a unique ID for each row to avoid conflicts
        agg_df['agg_id'] = agg_df.apply(lambda row: f"agg_{row[article_column]}_{row.name}", axis=1)
        
        # Enrich with article data if provided
        if articles:
            article_df = pd.DataFrame(articles)
            
            # Check if the article dataframe has the required columns
            if article_column in article_df.columns:
                # Select relevant columns from article data
                article_cols = [article_column]
                
                for col in ['description', 'name', 'category', 'supplier']:
                    if col in article_df.columns:
                        article_cols.append(col)
                        
                article_subset = article_df[article_cols].drop_duplicates(subset=[article_column])
                
                # Merge with aggregated data
                agg_df = pd.merge(agg_df, article_subset, on=article_column, how='left')
        
        # Convert back to list of dictionaries
        result = agg_df.to_dict('records')
        
        return result
    
    @staticmethod
    def aggregate_inventory_by_warehouse(inventory: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Aggregate inventory data by warehouse.
        
        Args:
            inventory (list): List of inventory dictionaries
            
        Returns:
            list: Aggregated inventory by warehouse
        """
        if not inventory:
            return []
            
        # Convert to DataFrame
        df = pd.DataFrame(inventory)
        
        # Check if required columns exist
        warehouse_column = None
        for col in ['warehouseNumber', 'warehouse', 'warehouseId', 'location', 'locationId', 'storeId', 'store']:
            if col in df.columns:
                warehouse_column = col
                break
                
        if not warehouse_column:
            logger.warning("No warehouse column found in inventory data")
            # Create a default warehouse column if none exists
            df['warehouse'] = 'default'
            warehouse_column = 'warehouse'
            
        # Determine which columns to use for aggregation
        agg_columns = {}
        
        # Look for quantity columns
        quantity_column = None
        for col in ['quantity', 'stock', 'inventoryQuantity', 'amount', 'count']:
            if col in df.columns:
                quantity_column = col
                break
                
        if quantity_column:
            agg_columns[quantity_column] = 'sum'
        else:
            # If no quantity column exists, create a default one with value 1
            logger.warning("No quantity column found in inventory data")
            df['quantity'] = 1
            quantity_column = 'quantity'
            agg_columns[quantity_column] = 'sum'
            
        # Add count aggregation
        count_column = df.columns[0]  # Use first column for counting
        agg_columns[count_column] = 'count'
        
        # Aggregate by warehouse
        agg_df = df.groupby(warehouse_column).agg(agg_columns).reset_index()
        
        # Rename columns
        column_mapping = {warehouse_column: 'warehouse'}
        
        if quantity_column:
            column_mapping[quantity_column] = 'total_quantity'
            
        column_mapping[count_column] = 'article_count'
        
        agg_df = agg_df.rename(columns=column_mapping)
        
        # Add aggregation type
        agg_df['aggregation_type'] = 'warehouse'
        
        # Add a unique ID for each row to avoid conflicts
        agg_df['agg_id'] = agg_df.apply(lambda row: f"wh_agg_{row.name}", axis=1)
        
        # Convert to list of dictionaries
        return agg_df.to_dict('records')

    # Add instance methods for compatibility with the lambda function
    def aggregate_daily_sales(self, sales: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Instance method wrapper for aggregate_sales_by_date."""
        return self.aggregate_sales_by_date(sales)
        
    def aggregate_article_sales(self, sales: List[Dict[str, Any]], articles: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Instance method wrapper for aggregate_sales_by_article."""
        return self.aggregate_sales_by_article(sales, articles)
        
    def aggregate_warehouse_inventory(self, inventory: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Instance method wrapper for aggregate_inventory_by_warehouse."""
        return self.aggregate_inventory_by_warehouse(inventory)


# Create singleton instances
data_enhancer = DataEnhancer()
data_aggregator = DataAggregator()
