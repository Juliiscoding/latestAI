#!/usr/bin/env python
"""
Integration test for data quality monitoring with the full ETL pipeline.

This script tests the seamless operation of data quality monitoring
within the ETL pipeline, ensuring that data quality checks are performed
at appropriate stages and that issues are properly handled.
"""
import os
import sys
import logging
import json
from datetime import datetime
import pandas as pd
import numpy as np
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import ETL components
from etl.connectors.prohandel_connector import ProHandelConnector
from etl.loaders.database_loader import DatabaseLoader
from etl.orchestrator import ETLOrchestrator
from etl.utils.database import create_engine, create_session_factory
from etl.models.base import Base
from etl.models.article import Article
from etl.models.sales import Sale
from etl.models.inventory import Inventory

# Import data quality components
from data_quality.manager import DataQualityManager


class MockProHandelConnector:
    """
    Mock connector for testing ETL pipeline integration.
    """
    def __init__(self, test_data=None):
        self.test_data = test_data or {}
        self.extraction_count = 0
    
    def extract_articles(self, incremental=True, last_updated=None):
        """Mock article extraction"""
        logger.info(f"Extracting articles (mock)")
        self.extraction_count += 1
        
        if "articles" in self.test_data:
            # Convert DataFrame to dict records
            return self.test_data["articles"].to_dict(orient="records")
        
        return []
    
    def extract_sales(self, incremental=True, last_updated=None):
        """Mock sales extraction"""
        logger.info(f"Extracting sales (mock)")
        self.extraction_count += 1
        
        if "sales" in self.test_data:
            return self.test_data["sales"].to_dict(orient="records")
        
        return []
    
    def extract_inventory(self, incremental=True, last_updated=None):
        """Mock inventory extraction"""
        logger.info(f"Extracting inventory (mock)")
        self.extraction_count += 1
        
        if "inventory" in self.test_data:
            return self.test_data["inventory"].to_dict(orient="records")
        
        return []


class MockDatabaseLoader:
    """
    Mock database loader for testing ETL pipeline integration.
    """
    def __init__(self):
        self.loaded_data = {}
        self.load_count = 0
    
    def load_articles(self, articles):
        """Mock article loading"""
        logger.info(f"Loading {len(articles)} articles (mock)")
        self.loaded_data["articles"] = articles
        self.load_count += 1
        return len(articles)
    
    def load_sales(self, sales):
        """Mock sales loading"""
        logger.info(f"Loading {len(sales)} sales (mock)")
        self.loaded_data["sales"] = sales
        self.load_count += 1
        return len(sales)
    
    def load_inventory(self, inventory):
        """Mock inventory loading"""
        logger.info(f"Loading {len(inventory)} inventory items (mock)")
        self.loaded_data["inventory"] = inventory
        self.load_count += 1
        return len(inventory)


def generate_test_data(include_quality_issues=True):
    """
    Generate test data for ETL integration testing.
    
    Args:
        include_quality_issues (bool): Whether to include data quality issues
        
    Returns:
        dict: Dictionary of DataFrames for different entity types
    """
    logger.info("Generating test data for ETL integration testing")
    
    # Generate article data
    article_count = 100
    article_ids = list(range(1001, 1001 + article_count))
    categories = ["Electronics", "Clothing", "Food", "Home", "Garden"]
    
    articles = pd.DataFrame({
        "article_id": article_ids,
        "article_name": [f"Article {i}" for i in article_ids],
        "category": np.random.choice(categories, size=article_count),
        "unit_price": np.random.uniform(5, 500, size=article_count),
        "supplier_id": np.random.randint(101, 121, size=article_count),
        "created_at": pd.date_range(start="2024-01-01", periods=article_count),
        "updated_at": pd.date_range(start="2024-02-01", periods=article_count)
    })
    
    # Generate sales data
    sales_count = 500
    sales = pd.DataFrame({
        "sale_id": list(range(1, sales_count + 1)),
        "sale_date": pd.date_range(start="2024-01-01", periods=sales_count),
        "article_id": np.random.choice(article_ids, size=sales_count),
        "customer_id": np.random.randint(1, 51, size=sales_count),
        "quantity": np.random.randint(1, 10, size=sales_count),
        "unit_price": np.random.uniform(5, 500, size=sales_count),
    })
    
    # Calculate total price
    sales["total_price"] = sales["quantity"] * sales["unit_price"]
    
    # Generate inventory data
    inventory = pd.DataFrame({
        "article_id": article_ids,
        "current_stock": np.random.randint(0, 100, size=article_count),
        "min_stock": np.random.randint(5, 20, size=article_count),
        "max_stock": np.random.randint(50, 150, size=article_count),
        "last_restock_date": pd.date_range(start="2024-01-15", periods=article_count),
        "updated_at": pd.date_range(start="2024-02-15", periods=article_count)
    })
    
    # Add data quality issues if requested
    if include_quality_issues:
        logger.info("Adding data quality issues to test data")
        
        # Missing values in articles
        missing_mask = np.random.random(article_count) < 0.1
        articles.loc[missing_mask, "unit_price"] = np.nan
        
        # Outliers in sales
        outlier_mask = np.random.random(sales_count) < 0.05
        sales.loc[outlier_mask, "quantity"] = np.random.randint(50, 100, size=outlier_mask.sum())
        sales.loc[outlier_mask, "total_price"] = sales.loc[outlier_mask, "quantity"] * sales.loc[outlier_mask, "unit_price"]
        
        # Constraint violations in inventory
        inconsistent_mask = np.random.random(article_count) < 0.08
        inventory.loc[inconsistent_mask, "min_stock"] = inventory.loc[inconsistent_mask, "max_stock"] + 10
        
        # Duplicates in sales
        duplicate_count = int(sales_count * 0.03)
        duplicate_indices = np.random.choice(sales_count, duplicate_count, replace=False)
        duplicate_rows = sales.iloc[duplicate_indices].copy()
        sales = pd.concat([sales, duplicate_rows])
    
    return {
        "articles": articles,
        "sales": sales,
        "inventory": inventory
    }


def test_etl_with_data_quality():
    """
    Test the integration of data quality monitoring with the ETL pipeline.
    """
    logger.info("Testing ETL integration with data quality monitoring")
    
    # Create output directory for test results
    output_dir = Path("test_results/etl_integration")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Generate test data with quality issues
    test_data = generate_test_data(include_quality_issues=True)
    
    # Initialize mock ETL components
    connector = MockProHandelConnector(test_data)
    loader = MockDatabaseLoader()
    
    # Initialize data quality manager
    data_quality_config = {
        "output_dir": str(output_dir),
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
                "duplicate_columns": ["sale_id", "article_id", "customer_id", "sale_date"],
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
    
    quality_manager = DataQualityManager(config=data_quality_config)
    
    # Create a custom ETL orchestrator with data quality checks
    class ETLOrchestratorWithQuality:
        def __init__(self, connector, loader, quality_manager):
            self.connector = connector
            self.loader = loader
            self.quality_manager = quality_manager
            self.extraction_results = {}
            self.quality_results = {}
            self.load_results = {}
            self.skipped_entities = []
        
        def run_etl_with_quality(self, entity_types=None, incremental=True, force_load=False):
            """Run ETL with data quality checks"""
            if entity_types is None:
                entity_types = ["articles", "sales", "inventory"]
            
            for entity_type in entity_types:
                logger.info(f"Processing {entity_type}")
                
                # Extract data
                extract_method = getattr(self.connector, f"extract_{entity_type}")
                extracted_data = extract_method(incremental=incremental)
                self.extraction_results[entity_type] = extracted_data
                
                # Convert to DataFrame for data quality checks
                df = pd.DataFrame(extracted_data)
                
                if df.empty:
                    logger.warning(f"No {entity_type} data extracted")
                    continue
                
                # Run data quality checks
                quality_results = self.quality_manager.run_monitors(df)
                self.quality_results[entity_type] = quality_results
                
                # Save quality results
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"quality_{entity_type}_{timestamp}.json"
                self.quality_manager.save_results(filename)
                
                # Check for critical issues
                alerts = quality_results.get("all_alerts", [])
                critical_alerts = [a for a in alerts if a["severity"] == "critical"]
                
                if critical_alerts and not force_load:
                    logger.error(f"Critical data quality issues found in {entity_type}, skipping load")
                    self.skipped_entities.append(entity_type)
                    
                    # Log critical issues
                    for alert in critical_alerts:
                        logger.error(f"  {alert['message']}")
                    
                    continue
                
                # Load data
                load_method = getattr(self.loader, f"load_{entity_type}")
                loaded_count = load_method(extracted_data)
                self.load_results[entity_type] = loaded_count
                
                logger.info(f"Loaded {loaded_count} {entity_type} records")
            
            return {
                "extraction": self.extraction_results,
                "quality": self.quality_results,
                "load": self.load_results,
                "skipped": self.skipped_entities
            }
    
    # Run ETL with data quality checks
    logger.info("Running ETL with data quality checks")
    orchestrator = ETLOrchestratorWithQuality(connector, loader, quality_manager)
    results = orchestrator.run_etl_with_quality(force_load=False)
    
    # Log results
    logger.info("ETL with data quality completed")
    logger.info(f"Extracted: {', '.join([f'{len(data)} {entity}' for entity, data in results['extraction'].items()])}")
    logger.info(f"Loaded: {', '.join([f'{count} {entity}' for entity, count in results['load'].items()])}")
    
    if results['skipped']:
        logger.warning(f"Skipped loading: {', '.join(results['skipped'])}")
    
    # Save summary report
    summary = {
        "timestamp": datetime.now().isoformat(),
        "entities": {
            entity: {
                "extracted": len(data),
                "loaded": results["load"].get(entity, 0) if entity not in results["skipped"] else 0,
                "skipped": entity in results["skipped"],
                "quality_issues": len(results["quality"].get(entity, {}).get("all_alerts", []))
            }
            for entity, data in results["extraction"].items()
        },
        "total_extracted": sum(len(data) for data in results["extraction"].values()),
        "total_loaded": sum(results["load"].values()),
        "total_skipped": len(results["skipped"]),
        "total_quality_issues": sum(len(results["quality"].get(entity, {}).get("all_alerts", []))
                                   for entity in results["extraction"].keys())
    }
    
    with open(output_dir / "etl_integration_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    # Run ETL with force load
    logger.info("Running ETL with force load option")
    orchestrator = ETLOrchestratorWithQuality(connector, loader, quality_manager)
    force_results = orchestrator.run_etl_with_quality(force_load=True)
    
    # Log force load results
    logger.info("ETL with force load completed")
    logger.info(f"Extracted: {', '.join([f'{len(data)} {entity}' for entity, data in force_results['extraction'].items()])}")
    logger.info(f"Loaded: {', '.join([f'{count} {entity}' for entity, count in force_results['load'].items()])}")
    
    # Save force load summary
    force_summary = {
        "timestamp": datetime.now().isoformat(),
        "entities": {
            entity: {
                "extracted": len(data),
                "loaded": force_results["load"].get(entity, 0),
                "quality_issues": len(force_results["quality"].get(entity, {}).get("all_alerts", []))
            }
            for entity, data in force_results["extraction"].items()
        },
        "total_extracted": sum(len(data) for data in force_results["extraction"].values()),
        "total_loaded": sum(force_results["load"].values()),
        "total_quality_issues": sum(len(force_results["quality"].get(entity, {}).get("all_alerts", []))
                                   for entity in force_results["extraction"].keys())
    }
    
    with open(output_dir / "etl_integration_force_summary.json", "w") as f:
        json.dump(force_summary, f, indent=2)
    
    # Compare regular and force load results
    comparison = {
        "timestamp": datetime.now().isoformat(),
        "regular_load": {
            "total_extracted": summary["total_extracted"],
            "total_loaded": summary["total_loaded"],
            "total_skipped": summary["total_skipped"],
            "total_quality_issues": summary["total_quality_issues"]
        },
        "force_load": {
            "total_extracted": force_summary["total_extracted"],
            "total_loaded": force_summary["total_loaded"],
            "total_quality_issues": force_summary["total_quality_issues"]
        },
        "difference": {
            "loaded": force_summary["total_loaded"] - summary["total_loaded"]
        }
    }
    
    with open(output_dir / "etl_integration_comparison.json", "w") as f:
        json.dump(comparison, f, indent=2)
    
    logger.info("ETL integration testing completed")
    logger.info(f"Results saved to {output_dir}")


if __name__ == "__main__":
    logger.info("Starting ETL integration testing")
    test_etl_with_data_quality()
