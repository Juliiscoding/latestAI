#!/usr/bin/env python
"""
Demo script for integrating data quality monitoring with the ETL pipeline
in the Mercurios.ai Predictive Inventory Management tool.
"""
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import json

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_quality.manager import DataQualityManager
from data_quality.monitors.completeness_monitor import CompletenessMonitor
from data_quality.monitors.outlier_monitor import OutlierMonitor
from data_quality.monitors.consistency_monitor import ConsistencyMonitor


def generate_sample_etl_data(include_quality_issues=False):
    """
    Generate sample ETL data for demonstration purposes.
    
    Args:
        include_quality_issues (bool): Whether to include data quality issues
        
    Returns:
        dict: Dictionary of DataFrames representing different entity types
    """
    np.random.seed(42)
    
    # Generate dates for the past month
    start_date = datetime.now() - timedelta(days=30)
    dates = [start_date + timedelta(days=i) for i in range(30)]
    
    # Generate sample article data
    article_ids = list(range(1001, 1021))
    article_rows = []
    
    for article_id in article_ids:
        article_name = f"Article {article_id}"
        article_category = np.random.choice(["Electronics", "Clothing", "Food", "Home"])
        unit_price = np.random.uniform(10, 100)
        supplier_id = np.random.randint(101, 106)
        
        article_rows.append({
            "article_id": article_id,
            "article_name": article_name,
            "category": article_category,
            "unit_price": unit_price,
            "supplier_id": supplier_id,
            "created_at": start_date,
            "updated_at": datetime.now()
        })
    
    # Generate sample sales data
    sales_rows = []
    
    for _ in range(200):
        sale_date = np.random.choice(dates)
        article_id = np.random.choice(article_ids)
        customer_id = np.random.randint(1, 51)
        quantity = np.random.randint(1, 10)
        
        # Get article price from article data
        article = next(a for a in article_rows if a["article_id"] == article_id)
        unit_price = article["unit_price"]
        
        total_price = quantity * unit_price
        
        sales_rows.append({
            "sale_id": len(sales_rows) + 1,
            "sale_date": sale_date,
            "article_id": article_id,
            "customer_id": customer_id,
            "quantity": quantity,
            "unit_price": unit_price,
            "total_price": total_price
        })
    
    # Generate sample inventory data
    inventory_rows = []
    
    for article_id in article_ids:
        current_stock = np.random.randint(10, 100)
        min_stock = np.random.randint(5, 20)
        max_stock = min_stock + np.random.randint(30, 80)
        
        inventory_rows.append({
            "article_id": article_id,
            "current_stock": current_stock,
            "min_stock": min_stock,
            "max_stock": max_stock,
            "last_restock_date": np.random.choice(dates[:-7]),
            "updated_at": datetime.now()
        })
    
    # Create DataFrames
    articles_df = pd.DataFrame(article_rows)
    sales_df = pd.DataFrame(sales_rows)
    inventory_df = pd.DataFrame(inventory_rows)
    
    # Add data quality issues if requested
    if include_quality_issues:
        # Add missing values to articles
        missing_mask = np.random.random(len(articles_df)) < 0.1  # 10% missing values
        articles_df.loc[missing_mask, "unit_price"] = np.nan
        
        # Add outliers to sales
        outlier_mask = np.random.random(len(sales_df)) < 0.05  # 5% outliers
        sales_df.loc[outlier_mask, "quantity"] = np.random.randint(50, 100, outlier_mask.sum())
        
        # Recalculate total price with outlier quantities
        sales_df.loc[outlier_mask, "total_price"] = sales_df.loc[outlier_mask, "quantity"] * sales_df.loc[outlier_mask, "unit_price"]
        
        # Add duplicates to sales
        duplicate_count = int(len(sales_df) * 0.03)  # 3% duplicates
        duplicate_indices = np.random.choice(len(sales_df), duplicate_count, replace=False)
        duplicate_rows = sales_df.iloc[duplicate_indices].copy()
        duplicate_rows["sale_id"] = duplicate_rows["sale_id"] + 1000  # Change IDs to avoid primary key conflicts
        sales_df = pd.concat([sales_df, duplicate_rows])
        
        # Add inconsistencies to inventory
        inconsistent_mask = np.random.random(len(inventory_df)) < 0.1  # 10% inconsistencies
        inventory_df.loc[inconsistent_mask, "min_stock"] = inventory_df.loc[inconsistent_mask, "max_stock"] + 10
    
    return {
        "articles": articles_df,
        "sales": sales_df,
        "inventory": inventory_df
    }


def demo_etl_with_quality_monitoring():
    """
    Demonstrate ETL with data quality monitoring.
    """
    logger.info("Demonstrating ETL with data quality monitoring")
    
    # Create output directory for data quality reports
    os.makedirs("data_quality_reports", exist_ok=True)
    
    # Generate sample data with quality issues
    logger.info("Generating sample ETL data with quality issues")
    etl_data = generate_sample_etl_data(include_quality_issues=True)
    
    # Initialize data quality manager
    logger.info("Initializing data quality manager")
    
    data_quality_config = {
        "output_dir": "data_quality_reports",
        "monitors": {
            "completeness": {
                "threshold": 0.95,
                "severity": "critical"
            },
            "outlier": {
                "method": "zscore",
                "threshold": 3.0,
                "max_outlier_ratio": 0.05,
                "severity": "warning"
            },
            "consistency": {
                "duplicate_columns": ["article_id", "sale_date", "customer_id", "quantity"],
                "unique_columns": ["sale_id"],
                "constraints": [
                    {
                        "name": "min_stock_less_than_max",
                        "type": "comparison",
                        "columns": ["min_stock", "max_stock"],
                        "operator": "<"
                    }
                ],
                "severity": "error"
            }
        }
    }
    
    manager = DataQualityManager(config=data_quality_config)
    
    # Track all alerts by entity
    all_alerts_by_entity = {}
    
    # Check data quality for each entity type
    for entity_name, entity_data in etl_data.items():
        logger.info(f"Checking data quality for {entity_name}")
        
        # Run data quality checks
        results = manager.run_monitors(entity_data)
        
        # Add entity name to each alert
        for alert in results.get("all_alerts", []):
            alert["entity"] = entity_name
        
        # Store alerts by entity
        all_alerts_by_entity[entity_name] = results.get("all_alerts", [])
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data_quality_{entity_name}_{timestamp}.json"
        filepath = manager.save_results(filename)
        
        # Log alerts
        alerts = results.get("all_alerts", [])
        if alerts:
            logger.warning(f"Found {len(alerts)} data quality issues in {entity_name}")
            for alert in alerts:
                logger.warning(f"  {alert['severity'].upper()}: {alert['message']}")
        else:
            logger.info(f"No data quality issues found in {entity_name}")
        
        # Simulate ETL decision based on data quality
        critical_alerts = [alert for alert in alerts if alert["severity"] == "critical"]
        if critical_alerts:
            logger.error(f"ETL process would be aborted for {entity_name} due to critical data quality issues")
            
            # In a real ETL pipeline, you might:
            # 1. Send alerts to data engineers
            # 2. Log the issues in a database
            # 3. Skip processing this entity or apply fallback strategies
            
            # Example of how to handle critical issues:
            logger.info(f"Attempting to fix critical issues in {entity_name}")
            
            if entity_name == "articles":
                # Fix missing unit prices
                missing_mask = entity_data["unit_price"].isna()
                if missing_mask.any():
                    logger.info(f"Fixing {missing_mask.sum()} missing unit prices")
                    # Use median price as a fallback
                    median_price = entity_data["unit_price"].median()
                    entity_data.loc[missing_mask, "unit_price"] = median_price
            
            # Re-run data quality checks after fixes
            logger.info(f"Re-checking data quality for {entity_name} after fixes")
            results = manager.run_monitors(entity_data)
            
            # Add entity name to each alert
            for alert in results.get("all_alerts", []):
                alert["entity"] = entity_name
            
            # Update stored alerts
            all_alerts_by_entity[entity_name] = results.get("all_alerts", [])
            
            # Save updated results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data_quality_{entity_name}_after_fix_{timestamp}.json"
            filepath = manager.save_results(filename)
            
            # Check if critical issues remain
            alerts = results.get("all_alerts", [])
            critical_alerts = [alert for alert in alerts if alert["severity"] == "critical"]
            if critical_alerts:
                logger.error(f"Critical issues remain in {entity_name} after fixes")
            else:
                logger.info(f"All critical issues in {entity_name} have been fixed")
        
        # For non-critical issues, we might proceed with warnings
        error_alerts = [alert for alert in alerts if alert["severity"] == "error"]
        warning_alerts = [alert for alert in alerts if alert["severity"] == "warning"]
        
        if error_alerts:
            logger.warning(f"Proceeding with {len(error_alerts)} error-level issues in {entity_name}")
        
        if warning_alerts:
            logger.info(f"Proceeding with {len(warning_alerts)} warning-level issues in {entity_name}")
        
        # Simulate ETL transformation and loading
        logger.info(f"Simulating ETL transformation and loading for {entity_name}")
        
        # Example of how data would flow through the ETL pipeline
        if entity_name == "sales":
            # Calculate daily sales aggregates
            daily_sales = entity_data.groupby("sale_date").agg({
                "quantity": "sum",
                "total_price": "sum"
            }).reset_index()
            
            logger.info(f"Generated daily sales aggregates: {len(daily_sales)} rows")
            
            # Check quality of transformed data
            logger.info("Checking quality of transformed data")
            transform_results = manager.run_monitors(daily_sales)
            
            # Add entity name to each alert
            for alert in transform_results.get("all_alerts", []):
                alert["entity"] = "daily_sales"
            
            # Update stored alerts
            all_alerts_by_entity["daily_sales"] = transform_results.get("all_alerts", [])
            
            # Save transformed data quality results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data_quality_daily_sales_{timestamp}.json"
            filepath = manager.save_results(filename)
    
    # Flatten all alerts
    all_alerts = []
    for entity_alerts in all_alerts_by_entity.values():
        all_alerts.extend(entity_alerts)
    
    # Generate a summary report
    logger.info("Generating data quality summary report")
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "entities_checked": list(etl_data.keys()),
        "total_records": {name: len(data) for name, data in etl_data.items()},
        "quality_issues_found": {
            entity: len(alerts) for entity, alerts in all_alerts_by_entity.items()
        },
        "critical_issues": len([a for a in all_alerts if a["severity"] == "critical"]),
        "error_issues": len([a for a in all_alerts if a["severity"] == "error"]),
        "warning_issues": len([a for a in all_alerts if a["severity"] == "warning"]),
        "info_issues": len([a for a in all_alerts if a["severity"] == "info"])
    }
    
    # Save summary report
    with open("data_quality_reports/etl_quality_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    logger.info("ETL with data quality monitoring demonstration completed")
    logger.info(f"Summary: {summary['critical_issues']} critical, {summary['error_issues']} error, {summary['warning_issues']} warning issues found")


if __name__ == "__main__":
    logger.info("Starting ETL with data quality monitoring demonstration")
    demo_etl_with_quality_monitoring()
