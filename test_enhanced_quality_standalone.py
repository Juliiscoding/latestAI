"""
Standalone test for enhanced data quality monitoring.

This script tests the enhanced data quality monitoring features without relying on the
full ETL pipeline, using mock data that resembles ProHandel API data.
"""
import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import logging

from data_quality.manager import DataQualityManager
from data_quality.monitors.format_monitor import FormatMonitor
from data_quality.monitors.freshness_monitor import FreshnessMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create output directory
OUTPUT_DIR = "test_results/standalone_quality"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_mock_article_data(num_records=1000, error_rate=0.05):
    """
    Generate mock article data resembling ProHandel API data.
    
    Args:
        num_records: Number of records to generate
        error_rate: Rate of data quality issues to introduce
        
    Returns:
        pd.DataFrame: Mock article data
    """
    # Generate base data
    data = {
        "number": [f"{np.random.randint(10000, 99999)}" for _ in range(num_records)],
        "name": [f"Article {i}" for i in range(num_records)],
        "description": [f"Description for article {i}" for i in range(num_records)],
        "purchasePrice": [round(np.random.uniform(10, 100), 2) for _ in range(num_records)],
        "salePrice": [round(np.random.uniform(20, 200), 2) for _ in range(num_records)],
        "isActive": [True for _ in range(num_records)],
        "manufacturerNumber": [np.random.randint(1000, 9999) for _ in range(num_records)],
        "supplierArticleNumber": [f"S-{np.random.randint(10000, 99999)}" for _ in range(num_records)],
        "firstPurchaseDate": [(datetime.now() - timedelta(days=np.random.randint(30, 365))).isoformat() for _ in range(num_records)],
        "lastPurchaseDate": [(datetime.now() - timedelta(days=np.random.randint(1, 30))).isoformat() for _ in range(num_records)],
        "lastChange": [(datetime.now() - timedelta(days=np.random.randint(1, 60))).isoformat() for _ in range(num_records)]
    }
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Introduce data quality issues
    num_errors = int(num_records * error_rate)
    
    # Format errors in article numbers
    error_indices = np.random.choice(num_records, num_errors, replace=False)
    for idx in error_indices[:num_errors//3]:
        df.loc[idx, "number"] = f"INV-{np.random.randint(1000, 9999)}"  # Invalid format
    
    # Format errors in supplier article numbers
    for idx in error_indices[num_errors//3:2*num_errors//3]:
        df.loc[idx, "supplierArticleNumber"] = f"{np.random.randint(10000, 99999)}"  # Missing S- prefix
    
    # Freshness issues (old data)
    for idx in error_indices[2*num_errors//3:]:
        df.loc[idx, "lastChange"] = (datetime.now() - timedelta(days=np.random.randint(180, 365))).isoformat()
    
    # Missing values
    for idx in np.random.choice(num_records, num_errors//5, replace=False):
        df.loc[idx, "description"] = None
    
    # Convert date strings to datetime objects
    for col in ["firstPurchaseDate", "lastPurchaseDate", "lastChange"]:
        df[col] = pd.to_datetime(df[col])
    
    return df


def generate_mock_customer_data(num_records=1000, error_rate=0.05):
    """
    Generate mock customer data resembling ProHandel API data.
    
    Args:
        num_records: Number of records to generate
        error_rate: Rate of data quality issues to introduce
        
    Returns:
        pd.DataFrame: Mock customer data
    """
    # Generate base data
    data = {
        "number": [np.random.randint(10000, 99999) for _ in range(num_records)],
        "name1": [f"Customer {i}" for i in range(num_records)],
        "name2": [f"Company {i}" for i in range(num_records)],
        "name3": [f"Department {i}" if i % 3 == 0 else "" for i in range(num_records)],
        "email": [f"customer{i}@example.com" for i in range(num_records)],
        "phone": [f"+49{np.random.randint(1000000000, 9999999999)}" for _ in range(num_records)],
        "isActive": [True for _ in range(num_records)],
        "lastChange": [(datetime.now() - timedelta(days=np.random.randint(1, 60))).isoformat() for _ in range(num_records)]
    }
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Introduce data quality issues
    num_errors = int(num_records * error_rate)
    
    # Format errors in emails
    error_indices = np.random.choice(num_records, num_errors, replace=False)
    for idx in error_indices[:num_errors//3]:
        df.loc[idx, "email"] = f"customer{idx}@example"  # Invalid email format
    
    # Format errors in phone numbers
    for idx in error_indices[num_errors//3:2*num_errors//3]:
        df.loc[idx, "phone"] = f"{np.random.randint(10000000, 99999999)}"  # Invalid phone format
    
    # Freshness issues (old data)
    for idx in error_indices[2*num_errors//3:]:
        df.loc[idx, "lastChange"] = (datetime.now() - timedelta(days=np.random.randint(180, 365))).isoformat()
    
    # Convert date strings to datetime objects
    df["lastChange"] = pd.to_datetime(df["lastChange"])
    
    return df


def configure_data_quality():
    """
    Configure data quality monitoring.
    
    Returns:
        dict: Data quality configuration
    """
    return {
        "output_dir": OUTPUT_DIR,
        "sampling": {
            "enabled": True,
            "min_data_size_for_sampling": 500,
            "default_sample_size": 200,
            "strategy": "outlier_biased",
            "outlier_fraction": 0.3,
            "outlier_method": "zscore",
            "outlier_threshold": 3.0
        },
        "monitors": {
            "completeness": {
                "min_completeness_ratio": 0.95,
                "severity": "warning"
            },
            "outlier": {
                "method": "zscore",
                "threshold": 3.0,
                "max_outlier_ratio": 0.05,
                "severity": "warning"
            },
            "consistency": {
                "max_violation_ratio": 0.05,
                "severity": "error"
            },
            "format": {
                "format_rules": [
                    {
                        "name": "article_number_format",
                        "columns": ["number"],
                        "custom_pattern": r"^\d+$",
                        "description": "Article number must be numeric"
                    },
                    {
                        "name": "supplier_article_number_format",
                        "columns": ["supplierArticleNumber"],
                        "custom_pattern": r"^S-\d+$",
                        "description": "Supplier article number must start with S- followed by digits"
                    },
                    {
                        "name": "email_format",
                        "columns": ["email"],
                        "pattern_type": "email",
                        "description": "Email must be in valid format"
                    },
                    {
                        "name": "phone_format",
                        "columns": ["phone"],
                        "custom_pattern": r"^\+\d{10,15}$",
                        "description": "Phone must start with + followed by 10-15 digits"
                    }
                ],
                "max_violation_ratio": 0.03,
                "severity": "error"
            },
            "freshness": {
                "freshness_rules": [
                    {
                        "name": "recent_update",
                        "column": "lastChange",
                        "max_age": 30,
                        "max_age_unit": "days",
                        "threshold": 0.2,
                        "severity": "warning",
                        "description": "Data should be updated within the last 30 days"
                    },
                    {
                        "name": "very_old_data",
                        "column": "lastChange",
                        "max_age": 180,
                        "max_age_unit": "days",
                        "threshold": 0.5,
                        "severity": "error",
                        "description": "Data should not be older than 180 days"
                    }
                ],
                "severity": "warning"
            }
        }
    }


def visualize_quality_results(entity_name, results):
    """
    Visualize data quality results for an entity.
    
    Args:
        entity_name: Name of the entity
        results: Data quality results
    """
    if not results or "metrics" not in results:
        logger.warning(f"No metrics available for {entity_name}")
        return
    
    metrics = results.get("metrics", {})
    if not metrics:
        logger.warning(f"No metrics available for {entity_name}")
        return
    
    plt.figure(figsize=(15, 10))
    plt.suptitle(f"Data Quality Metrics for {entity_name}", fontsize=16)
    
    # Plot completeness metrics
    if "completeness" in metrics:
        plt.subplot(2, 2, 1)
        completeness_data = metrics["completeness"].get("column_completeness", {})
        if completeness_data:
            columns = list(completeness_data.keys())
            values = [data.get("completeness_ratio", 0) for data in completeness_data.values()]
            sns.barplot(x=columns, y=values)
            plt.title("Completeness Ratio by Column")
            plt.xticks(rotation=45, ha="right")
            plt.ylim(0, 1.05)
    
    # Plot outlier metrics
    if "outlier" in metrics:
        plt.subplot(2, 2, 2)
        outlier_data = metrics["outlier"].get("column_metrics", {})
        if outlier_data:
            columns = list(outlier_data.keys())
            values = [data.get("outlier_ratio", 0) for data in outlier_data.values()]
            sns.barplot(x=columns, y=values)
            plt.title("Outlier Ratio by Column")
            plt.xticks(rotation=45, ha="right")
            plt.ylim(0, max(values) * 1.2 if values else 0.1)
    
    # Plot format validation metrics
    if "format" in metrics:
        plt.subplot(2, 2, 3)
        format_data = metrics["format"].get("violation_ratios", {})
        if format_data:
            rules = list(format_data.keys())
            values = list(format_data.values())
            sns.barplot(x=rules, y=values)
            plt.title("Format Violation Ratio by Rule")
            plt.xticks(rotation=45, ha="right")
            plt.ylim(0, max(values) * 1.2 if values else 0.1)
    
    # Plot freshness metrics
    if "freshness" in metrics:
        plt.subplot(2, 2, 4)
        freshness_data = metrics["freshness"].get("stale_ratios", {})
        if freshness_data:
            rules = list(freshness_data.keys())
            values = list(freshness_data.values())
            sns.barplot(x=rules, y=values)
            plt.title("Stale Data Ratio by Rule")
            plt.xticks(rotation=45, ha="right")
            plt.ylim(0, max(values) * 1.2 if values else 0.1)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, f"{entity_name}_quality_metrics.png"))
    plt.close()
    
    logger.info(f"Saved quality visualization for {entity_name}")


def main():
    """Main function to test enhanced data quality monitoring."""
    logger.info("Starting standalone enhanced data quality monitoring test")
    
    # Configure data quality
    dq_config = configure_data_quality()
    
    # Initialize data quality manager
    dq_manager = DataQualityManager(dq_config)
    
    # Generate mock data
    logger.info("Generating mock article data")
    article_data = generate_mock_article_data(num_records=1000, error_rate=0.05)
    logger.info(f"Generated {len(article_data)} article records")
    
    logger.info("Generating mock customer data")
    customer_data = generate_mock_customer_data(num_records=1000, error_rate=0.05)
    logger.info(f"Generated {len(customer_data)} customer records")
    
    # Run data quality checks on article data
    logger.info("Running data quality checks on article data")
    article_results = dq_manager.run_monitors(article_data, entity_name="article")
    
    # Save article results
    article_results_file = os.path.join(OUTPUT_DIR, "article_quality_results.json")
    with open(article_results_file, "w") as f:
        json.dump(article_results, f, indent=2)
    logger.info(f"Saved article quality results to {article_results_file}")
    
    # Run data quality checks on customer data
    logger.info("Running data quality checks on customer data")
    customer_results = dq_manager.run_monitors(customer_data, entity_name="customer")
    
    # Save customer results
    customer_results_file = os.path.join(OUTPUT_DIR, "customer_quality_results.json")
    with open(customer_results_file, "w") as f:
        json.dump(customer_results, f, indent=2)
    logger.info(f"Saved customer quality results to {customer_results_file}")
    
    # Visualize results
    logger.info("Visualizing results")
    visualize_quality_results("article", article_results)
    visualize_quality_results("customer", customer_results)
    
    # Print summary
    logger.info("Data Quality Summary:")
    
    # Article summary
    article_alerts = article_results.get("all_alerts", [])
    article_alerts_by_severity = {}
    for alert in article_alerts:
        severity = alert.get("severity", "info")
        if severity not in article_alerts_by_severity:
            article_alerts_by_severity[severity] = []
        article_alerts_by_severity[severity].append(alert)
    
    logger.info("Article Data Quality:")
    for severity, alerts in article_alerts_by_severity.items():
        logger.info(f"  {severity.upper()}: {len(alerts)} alerts")
    
    # Customer summary
    customer_alerts = customer_results.get("all_alerts", [])
    customer_alerts_by_severity = {}
    for alert in customer_alerts:
        severity = alert.get("severity", "info")
        if severity not in customer_alerts_by_severity:
            customer_alerts_by_severity[severity] = []
        customer_alerts_by_severity[severity].append(alert)
    
    logger.info("Customer Data Quality:")
    for severity, alerts in customer_alerts_by_severity.items():
        logger.info(f"  {severity.upper()}: {len(alerts)} alerts")
    
    logger.info("Standalone enhanced data quality monitoring test completed")


if __name__ == "__main__":
    main()
