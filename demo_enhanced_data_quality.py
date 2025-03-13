"""
Demo script for enhanced data quality monitoring with format validation, 
freshness checks, and sampling strategies.

This script demonstrates the use of the enhanced data quality monitoring system
with the new FormatMonitor and FreshnessMonitor, as well as sampling strategies
for large datasets.
"""
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import logging
import matplotlib.pyplot as plt
import seaborn as sns

from data_quality.manager import DataQualityManager
from data_quality.monitors.completeness_monitor import CompletenessMonitor
from data_quality.monitors.outlier_monitor import OutlierMonitor
from data_quality.monitors.consistency_monitor import ConsistencyMonitor
from data_quality.monitors.format_monitor import FormatMonitor
from data_quality.monitors.freshness_monitor import FreshnessMonitor
from data_quality.sampling import DataSampler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create output directory
OUTPUT_DIR = "test_results/enhanced_data_quality"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_sample_data(size=10000):
    """Generate sample data for testing."""
    np.random.seed(42)
    
    # Generate dates with some being old (stale)
    current_date = datetime.now()
    dates = [current_date - timedelta(days=np.random.randint(0, 365)) for _ in range(size)]
    
    # Generate emails with some format violations
    emails = []
    for i in range(size):
        if i % 20 == 0:  # 5% format violations
            emails.append(f"invalid-email-{i}")
        else:
            emails.append(f"user{i}@example.com")
    
    # Generate phone numbers with some format violations
    phones = []
    for i in range(size):
        if i % 25 == 0:  # 4% format violations
            phones.append(f"invalid-phone-{i}")
        else:
            phones.append(f"+{np.random.randint(1, 99)}{np.random.randint(1000000000, 9999999999)}")
    
    # Generate numerical data with outliers
    values = np.random.normal(100, 15, size)
    # Add some outliers
    outlier_indices = np.random.choice(size, size=int(size * 0.03), replace=False)
    values[outlier_indices] = np.random.choice(
        [np.random.uniform(200, 300), np.random.uniform(-100, 0)],
        size=len(outlier_indices)
    )
    
    # Generate categorical data with some consistency issues
    categories = np.random.choice(['A', 'B', 'C', 'D'], size=size)
    subcategories = []
    for cat in categories:
        if cat == 'A' and np.random.random() < 0.05:  # 5% consistency violations
            subcategories.append(np.random.choice(['X', 'Y', 'Z']))
        elif cat == 'A':
            subcategories.append(np.random.choice(['A1', 'A2', 'A3']))
        elif cat == 'B':
            subcategories.append(np.random.choice(['B1', 'B2']))
        elif cat == 'C':
            subcategories.append(np.random.choice(['C1', 'C2', 'C3', 'C4']))
        else:
            subcategories.append(np.random.choice(['D1', 'D2']))
    
    # Generate IDs with some missing values
    ids = [f"ID-{i}" if np.random.random() > 0.02 else None for i in range(size)]
    
    # Create DataFrame
    df = pd.DataFrame({
        'id': ids,
        'date': dates,
        'email': emails,
        'phone': phones,
        'value': values,
        'category': categories,
        'subcategory': subcategories
    })
    
    return df


def configure_data_quality_manager():
    """Configure the DataQualityManager with all monitors."""
    config = {
        "output_dir": OUTPUT_DIR,
        "sampling": {
            "enabled": True,
            "min_data_size_for_sampling": 5000,
            "default_sample_size": 2000,
            "strategy": "outlier_biased",
            "outlier_fraction": 0.3,
            "outlier_method": "zscore",
            "outlier_threshold": 3.0
        },
        "monitors": {
            "completeness": {
                "columns": ["id", "date", "email", "phone", "value", "category", "subcategory"],
                "min_completeness_ratio": 0.98,
                "severity": "warning"
            },
            "outlier": {
                "columns": ["value"],
                "method": "zscore",
                "threshold": 3.0,
                "max_outlier_ratio": 0.05,
                "severity": "warning"
            },
            "consistency": {
                "unique_columns": ["id"],
                "relationships": [
                    {
                        "name": "category_subcategory",
                        "parent_column": "category",
                        "child_column": "subcategory",
                        "valid_combinations": {
                            "A": ["A1", "A2", "A3"],
                            "B": ["B1", "B2"],
                            "C": ["C1", "C2", "C3", "C4"],
                            "D": ["D1", "D2"]
                        }
                    }
                ],
                "max_violation_ratio": 0.05,
                "severity": "error"
            },
            "format": {
                "format_rules": [
                    {
                        "name": "email_format",
                        "columns": ["email"],
                        "pattern": "email"
                    },
                    {
                        "name": "phone_format",
                        "columns": ["phone"],
                        "pattern": "phone"
                    },
                    {
                        "name": "id_format",
                        "columns": ["id"],
                        "custom_pattern": r"^ID-\d+$"
                    }
                ],
                "max_violation_ratio": 0.03,
                "severity": "error"
            },
            "freshness": {
                "freshness_rules": [
                    {
                        "name": "recent_data",
                        "column": "date",
                        "max_age": 30,
                        "max_age_unit": "days",
                        "threshold": 0.1,
                        "severity": "warning"
                    },
                    {
                        "name": "very_old_data",
                        "column": "date",
                        "max_age": 180,
                        "max_age_unit": "days",
                        "threshold": 0.02,
                        "severity": "error"
                    }
                ],
                "severity": "warning"
            }
        }
    }
    
    return DataQualityManager(config)


def visualize_results(results, title, output_file):
    """Visualize data quality results."""
    plt.figure(figsize=(12, 8))
    
    # Set up the plot
    plt.suptitle(title, fontsize=16)
    
    # Create subplots
    plt.subplot(2, 2, 1)
    
    # Completeness metrics
    if "completeness" in results["metrics"]:
        completeness_ratios = {
            col: metrics["completeness_ratio"] 
            for col, metrics in results["metrics"]["completeness"]["column_metrics"].items()
        }
        
        if completeness_ratios:
            sns.barplot(x=list(completeness_ratios.keys()), y=list(completeness_ratios.values()))
            plt.title("Completeness Ratio by Column")
            plt.xticks(rotation=45, ha="right")
            plt.ylim(0, 1.05)
            plt.ylabel("Completeness Ratio")
    
    # Outlier metrics
    plt.subplot(2, 2, 2)
    if "outlier" in results["metrics"]:
        outlier_ratios = {
            col: metrics["outlier_ratio"] 
            for col, metrics in results["metrics"]["outlier"]["column_metrics"].items()
        }
        
        if outlier_ratios:
            sns.barplot(x=list(outlier_ratios.keys()), y=list(outlier_ratios.values()))
            plt.title("Outlier Ratio by Column")
            plt.xticks(rotation=45, ha="right")
            plt.ylim(0, max(list(outlier_ratios.values()) + [0.05]) * 1.1)
            plt.ylabel("Outlier Ratio")
    
    # Format validation metrics
    plt.subplot(2, 2, 3)
    if "format" in results["metrics"]:
        violation_ratios = results["metrics"]["format"]["violation_ratios"]
        
        if violation_ratios:
            sns.barplot(x=list(violation_ratios.keys()), y=list(violation_ratios.values()))
            plt.title("Format Violation Ratio by Rule")
            plt.xticks(rotation=45, ha="right")
            plt.ylim(0, max(list(violation_ratios.values()) + [0.05]) * 1.1)
            plt.ylabel("Violation Ratio")
    
    # Freshness metrics
    plt.subplot(2, 2, 4)
    if "freshness" in results["metrics"]:
        stale_ratios = results["metrics"]["freshness"]["stale_ratios"]
        
        if stale_ratios:
            sns.barplot(x=list(stale_ratios.keys()), y=list(stale_ratios.values()))
            plt.title("Stale Data Ratio by Rule")
            plt.xticks(rotation=45, ha="right")
            plt.ylim(0, max(list(stale_ratios.values()) + [0.05]) * 1.1)
            plt.ylabel("Stale Ratio")
    
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
    
    logger.info(f"Visualization saved to {output_file}")


def main():
    """Main function to run the demo."""
    logger.info("Starting enhanced data quality monitoring demo")
    
    # Generate sample data
    logger.info("Generating sample data")
    data = generate_sample_data(size=10000)
    logger.info(f"Generated {len(data)} rows of sample data")
    
    # Configure and run data quality manager
    logger.info("Configuring data quality manager")
    dq_manager = configure_data_quality_manager()
    
    logger.info("Running data quality checks")
    results = dq_manager.run_monitors(data)
    
    # Save results
    results_file = dq_manager.save_results("enhanced_data_quality_results.json")
    logger.info(f"Saved results to {results_file}")
    
    # Visualize results
    logger.info("Visualizing results")
    visualize_results(
        results,
        "Enhanced Data Quality Monitoring Results",
        os.path.join(OUTPUT_DIR, "enhanced_data_quality_visualization.png")
    )
    
    # Print alerts summary
    alerts_by_severity = {}
    for alert in results["all_alerts"]:
        severity = alert["severity"]
        if severity not in alerts_by_severity:
            alerts_by_severity[severity] = []
        alerts_by_severity[severity].append(alert)
    
    logger.info("Data Quality Alerts Summary:")
    for severity, alerts in alerts_by_severity.items():
        logger.info(f"  {severity.upper()}: {len(alerts)} alerts")
    
    # Print sampling information if applied
    if results.get("sampling", {}).get("sampled", False):
        sampling = results["sampling"]
        logger.info(
            f"Sampling was applied: {sampling['sample_size']} rows sampled from "
            f"{sampling['original_size']} total rows ({sampling['sampling_ratio']:.2%}) "
            f"using {sampling['method']} method"
        )
    
    logger.info("Enhanced data quality monitoring demo completed")


if __name__ == "__main__":
    main()
