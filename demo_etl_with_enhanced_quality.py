"""
Demo script for integrating enhanced data quality monitoring with the ETL pipeline.

This script demonstrates the use of the enhanced data quality monitoring system
with the ETL pipeline, including format validation, freshness checks, and sampling
strategies for large datasets.
"""
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv

from etl.connectors.prohandel_connector import ProHandelConnector
from etl.loaders.database_loader import DatabaseLoader
from etl.orchestrator import ETLOrchestrator
from data_quality.manager import DataQualityManager
from data_quality.monitors.completeness_monitor import CompletenessMonitor
from data_quality.monitors.outlier_monitor import OutlierMonitor
from data_quality.monitors.consistency_monitor import ConsistencyMonitor
from data_quality.monitors.format_monitor import FormatMonitor
from data_quality.monitors.freshness_monitor import FreshnessMonitor

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create output directory
OUTPUT_DIR = "test_results/etl_enhanced_data_quality"
os.makedirs(OUTPUT_DIR, exist_ok=True)


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
                "columns": ["article_id", "name", "price", "category", "supplier_id"],
                "min_completeness_ratio": 0.98,
                "severity": "warning"
            },
            "outlier": {
                "columns": ["price", "stock_quantity"],
                "method": "zscore",
                "threshold": 3.0,
                "max_outlier_ratio": 0.05,
                "severity": "warning"
            },
            "consistency": {
                "unique_columns": ["article_id"],
                "max_violation_ratio": 0.05,
                "severity": "error"
            },
            "format": {
                "format_rules": [
                    {
                        "name": "article_id_format",
                        "columns": ["article_id"],
                        "custom_pattern": r"^[A-Z0-9-]+$"
                    },
                    {
                        "name": "supplier_id_format",
                        "columns": ["supplier_id"],
                        "custom_pattern": r"^S-\d+$"
                    }
                ],
                "max_violation_ratio": 0.03,
                "severity": "error"
            },
            "freshness": {
                "freshness_rules": [
                    {
                        "name": "recent_update",
                        "column": "last_updated",
                        "max_age": 30,
                        "max_age_unit": "days",
                        "threshold": 0.1,
                        "severity": "warning"
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


class EnhancedETLOrchestrator(ETLOrchestrator):
    """
    Enhanced ETL Orchestrator with integrated data quality monitoring.
    """
    
    def __init__(self, connector, loader, data_quality_manager=None):
        """
        Initialize the enhanced ETL orchestrator.
        
        Args:
            connector: Data connector for extraction
            loader: Data loader for loading
            data_quality_manager: Data quality manager for monitoring
        """
        super().__init__(connector, loader)
        self.data_quality_manager = data_quality_manager
        self.quality_results = {}
    
    def extract_transform_load(self, entity_type, force=False, incremental=True):
        """
        Extract, transform, and load data with data quality monitoring.
        
        Args:
            entity_type: Type of entity to process
            force: Whether to force operation despite quality issues
            incremental: Whether to use incremental loading
            
        Returns:
            Dict: Results of the ETL operation
        """
        logger.info(f"Starting ETL process for {entity_type} with data quality monitoring")
        
        # Extract data
        logger.info(f"Extracting {entity_type} data")
        data = self.connector.extract_data(entity_type, incremental=incremental)
        
        if data is None or len(data) == 0:
            logger.warning(f"No {entity_type} data extracted")
            return {"status": "warning", "message": f"No {entity_type} data extracted"}
        
        logger.info(f"Extracted {len(data)} {entity_type} records")
        
        # Add timestamp for freshness monitoring
        if 'last_updated' not in data.columns:
            # Generate random timestamps for demo purposes
            # In a real scenario, this would come from the data source
            current_time = datetime.now()
            data['last_updated'] = [
                current_time - timedelta(days=np.random.randint(0, 60))
                for _ in range(len(data))
            ]
        
        # Run data quality checks
        if self.data_quality_manager:
            logger.info(f"Running data quality checks on {entity_type} data")
            quality_results = self.data_quality_manager.run_monitors(
                data, 
                entity_name=entity_type
            )
            
            # Store quality results
            self.quality_results[entity_type] = quality_results
            
            # Save quality results
            results_file = self.data_quality_manager.save_results(
                f"{entity_type}_quality_results.json"
            )
            logger.info(f"Saved quality results to {results_file}")
            
            # Check for critical issues
            critical_alerts = [
                alert for alert in quality_results["all_alerts"]
                if alert["severity"] in ["error", "critical"]
            ]
            
            if critical_alerts and not force:
                logger.error(
                    f"Critical data quality issues detected for {entity_type}. "
                    f"Use force=True to load anyway."
                )
                return {
                    "status": "error",
                    "message": f"Critical data quality issues detected for {entity_type}",
                    "quality_results": quality_results
                }
            
            if critical_alerts and force:
                logger.warning(
                    f"Loading {entity_type} despite critical data quality issues "
                    f"because force=True"
                )
        
        # Load data
        logger.info(f"Loading {entity_type} data")
        load_result = self.loader.load_data(entity_type, data)
        
        result = {
            "status": "success",
            "message": f"Successfully processed {len(data)} {entity_type} records",
            "load_result": load_result
        }
        
        if self.data_quality_manager:
            result["quality_results"] = self.quality_results[entity_type]
        
        return result


def main():
    """Main function to run the demo."""
    logger.info("Starting enhanced ETL with data quality monitoring demo")
    
    # Initialize components
    logger.info("Initializing components")
    connector = ProHandelConnector()
    loader = DatabaseLoader()
    data_quality_manager = configure_data_quality_manager()
    
    # Initialize enhanced ETL orchestrator
    orchestrator = EnhancedETLOrchestrator(
        connector=connector,
        loader=loader,
        data_quality_manager=data_quality_manager
    )
    
    # Process articles
    logger.info("Processing articles")
    article_result = orchestrator.extract_transform_load("articles", force=True)
    
    # Check if quality results are available
    if "quality_results" in article_result:
        # Visualize quality results
        logger.info("Visualizing quality results")
        visualize_results(
            article_result["quality_results"],
            "Articles Data Quality Monitoring Results",
            os.path.join(OUTPUT_DIR, "articles_quality_visualization.png")
        )
        
        # Print alerts summary
        alerts_by_severity = {}
        for alert in article_result["quality_results"]["all_alerts"]:
            severity = alert["severity"]
            if severity not in alerts_by_severity:
                alerts_by_severity[severity] = []
            alerts_by_severity[severity].append(alert)
        
        logger.info("Data Quality Alerts Summary:")
        for severity, alerts in alerts_by_severity.items():
            logger.info(f"  {severity.upper()}: {len(alerts)} alerts")
    
    logger.info("Enhanced ETL with data quality monitoring demo completed")


if __name__ == "__main__":
    main()
