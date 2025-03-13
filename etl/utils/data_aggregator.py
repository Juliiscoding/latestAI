"""
Data aggregation utilities for the Mercurios.ai ETL pipeline.
"""
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

from etl.utils.logger import logger

def aggregate_sales_by_date(sales_data: List[Dict[Any, Any]]) -> List[Dict[Any, Any]]:
    """
    Aggregate sales data by date.
    
    Args:
        sales_data: List of sale records
        
    Returns:
        List of aggregated sales records by date
    """
    try:
        # Convert to DataFrame
        df = pd.DataFrame(sales_data)
        
        # Extract date from timestamp
        df['sale_date'] = pd.to_datetime(df['date']).dt.date.astype(str)
        
        # Group by date and aggregate
        agg_df = df.groupby('sale_date').agg(
            sale_count=('id', 'count'),
            total_quantity=('quantity', 'sum'),
            total_amount=('amount', 'sum')
        ).reset_index()
        
        # Add aggregation type
        agg_df['aggregation_type'] = 'daily'
        
        # Convert to list of dictionaries
        return agg_df.to_dict('records')
    except Exception as e:
        logger.error(f"Error aggregating sales by date: {str(e)}")
        return []

def aggregate_sales_by_article(sales_data: List[Dict[Any, Any]]) -> List[Dict[Any, Any]]:
    """
    Aggregate sales data by article.
    
    Args:
        sales_data: List of sale records
        
    Returns:
        List of aggregated sales records by article
    """
    try:
        # Convert to DataFrame
        df = pd.DataFrame(sales_data)
        
        # Group by article number and aggregate
        agg_df = df.groupby('articleNumber').agg(
            sale_count=('id', 'count'),
            total_quantity=('quantity', 'sum'),
            total_amount=('amount', 'sum')
        ).reset_index()
        
        # Add aggregation type
        agg_df['aggregation_type'] = 'article'
        
        # Convert to list of dictionaries
        return agg_df.to_dict('records')
    except Exception as e:
        logger.error(f"Error aggregating sales by article: {str(e)}")
        return []

def aggregate_inventory_by_warehouse(inventory_data: List[Dict[Any, Any]]) -> List[Dict[Any, Any]]:
    """
    Aggregate inventory data by warehouse.
    
    Args:
        inventory_data: List of inventory records
        
    Returns:
        List of aggregated inventory records by warehouse
    """
    try:
        # Convert to DataFrame
        df = pd.DataFrame(inventory_data)
        
        # Group by warehouse code and aggregate
        agg_df = df.groupby('warehouseCode').agg(
            article_count=('articleNumber', 'nunique'),
            total_quantity=('quantity', 'sum')
        ).reset_index()
        
        # Add aggregation type
        agg_df['aggregation_type'] = 'warehouse'
        
        # Convert to list of dictionaries
        return agg_df.to_dict('records')
    except Exception as e:
        logger.error(f"Error aggregating inventory by warehouse: {str(e)}")
        return []
