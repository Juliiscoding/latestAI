"""
Data enhancement and aggregation module for the ProHandel Lambda function.

This module provides functions to enhance and aggregate data from the ProHandel API
before sending it to Fivetran.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

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
        
        # Add full address field
        address_columns = ['street', 'zipCode', 'city', 'country']
        if all(col in df.columns for col in address_columns):
            df['full_address'] = df.apply(
                lambda row: f"{row['street']}, {row['zipCode']} {row['city']}, {row['country']}",
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
        
        # Calculate delivery time (days between order and delivery)
        if 'orderDate' in df.columns and 'deliveryDate' in df.columns:
            df['orderDate'] = pd.to_datetime(df['orderDate'])
            df['deliveryDate'] = pd.to_datetime(df['deliveryDate'])
            df['delivery_time_days'] = (df['deliveryDate'] - df['orderDate']).dt.days
        
        # Add order age (days since order date)
        if 'orderDate' in df.columns:
            df['orderDate'] = pd.to_datetime(df['orderDate'])
            df['order_age_days'] = (datetime.now() - df['orderDate']).dt.days
        
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
        
        # Calculate unit price if not present
        if 'total' in df.columns and 'quantity' in df.columns and 'price' not in df.columns:
            df['price'] = (df['total'] / df['quantity']).round(2)
        
        # Add sale age (days since sale date)
        if 'saleDate' in df.columns:
            df['saleDate'] = pd.to_datetime(df['saleDate'])
            df['sale_age_days'] = (datetime.now() - df['saleDate']).dt.days
        
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
        
        # Ensure date column is datetime
        if 'saleDate' in df.columns:
            df['saleDate'] = pd.to_datetime(df['saleDate'])
            df['sale_date'] = df['saleDate'].dt.date
        else:
            return []
        
        # Aggregate by date
        agg_df = df.groupby('sale_date').agg({
            'quantity': 'sum',
            'total': 'sum',
            'number': 'count'  # Count of sales
        }).reset_index()
        
        # Rename columns
        agg_df = agg_df.rename(columns={
            'number': 'sale_count',
            'quantity': 'total_quantity',
            'total': 'total_amount'
        })
        
        # Convert date back to string for JSON serialization
        agg_df['sale_date'] = agg_df['sale_date'].astype(str)
        
        # Add aggregation type identifier
        agg_df['aggregation_type'] = 'daily_sales'
        
        return agg_df.to_dict('records')
    
    @staticmethod
    def aggregate_sales_by_article(sales: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Aggregate sales by article.
        
        Args:
            sales: List of sale data
            
        Returns:
            Aggregated sales data by article
        """
        if not sales:
            return []
            
        # Convert to DataFrame
        df = pd.DataFrame(sales)
        
        # Check if required columns exist
        if 'articleNumber' not in df.columns:
            return []
        
        # Aggregate by article
        agg_df = df.groupby('articleNumber').agg({
            'quantity': 'sum',
            'total': 'sum',
            'number': 'count'  # Count of sales
        }).reset_index()
        
        # Rename columns
        agg_df = agg_df.rename(columns={
            'number': 'sale_count',
            'quantity': 'total_quantity',
            'total': 'total_amount'
        })
        
        # Add aggregation type identifier
        agg_df['aggregation_type'] = 'article_sales'
        
        return agg_df.to_dict('records')
    
    @staticmethod
    def aggregate_inventory_by_warehouse(inventory: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Aggregate inventory by warehouse.
        
        Args:
            inventory: List of inventory data
            
        Returns:
            Aggregated inventory data by warehouse
        """
        if not inventory:
            return []
            
        # Convert to DataFrame
        df = pd.DataFrame(inventory)
        
        # Check if required columns exist
        if 'warehouseCode' not in df.columns or 'quantity' not in df.columns:
            return []
        
        # Aggregate by warehouse
        agg_df = df.groupby('warehouseCode').agg({
            'quantity': 'sum',
            'articleNumber': 'count'  # Count of articles
        }).reset_index()
        
        # Rename columns
        agg_df = agg_df.rename(columns={
            'articleNumber': 'article_count',
            'quantity': 'total_quantity'
        })
        
        # Add aggregation type identifier
        agg_df['aggregation_type'] = 'warehouse_inventory'
        
        return agg_df.to_dict('records')


# Create singleton instances
data_enhancer = DataEnhancer()
data_aggregator = DataAggregator()
