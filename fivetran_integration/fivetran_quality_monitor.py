"""
Fivetran Data Quality Monitor for the Mercurios.ai ETL pipeline.

This module integrates Fivetran-loaded data with the Mercurios.ai data quality monitoring system.
It applies comprehensive data quality checks to data loaded by Fivetran and generates reports.
"""
import os
import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import sqlalchemy as sa
from sqlalchemy import create_engine, MetaData, Table, Column, select

from data_quality.manager import DataQualityManager
from etl.utils.logger import logger
from etl.config.config import ETL_CONFIG

class FivetranQualityMonitor:
    """
    Monitor for data quality of Fivetran-loaded data.
    
    This class connects to the destination database where Fivetran has loaded data,
    applies comprehensive data quality checks, and generates reports.
    """
    
    def __init__(self, db_connection_string: str, schema_name: str = "prohandel", 
                 data_quality_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Fivetran quality monitor.
        
        Args:
            db_connection_string: SQLAlchemy connection string for the destination database
            schema_name: Schema name where Fivetran has loaded the data
            data_quality_config: Configuration for data quality monitoring
        """
        self.db_connection_string = db_connection_string
        self.schema_name = schema_name
        self.engine = create_engine(db_connection_string)
        self.metadata = MetaData(schema=schema_name)
        self.metadata.reflect(bind=self.engine)
        
        # Initialize data quality manager
        self.data_quality_config = data_quality_config or {}
        self.data_quality_manager = self._initialize_data_quality_manager()
        
        # Create output directory for data quality reports
        self.quality_output_dir = self.data_quality_config.get(
            'output_dir', 'fivetran_data_quality_reports'
        )
        os.makedirs(self.quality_output_dir, exist_ok=True)
        
        logger.info(f"Initialized Fivetran quality monitor for schema {schema_name}")
    
    def _initialize_data_quality_manager(self) -> DataQualityManager:
        """
        Initialize the data quality manager with appropriate configuration.
        
        Returns:
            DataQualityManager: Configured data quality manager
        """
        # If no config is provided, use default configuration
        if not self.data_quality_config:
            self.data_quality_config = {
                "output_dir": "fivetran_data_quality_reports",
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
                        "min_completeness_ratio": 0.98,
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
                        "max_violation_ratio": 0.03,
                        "severity": "error"
                    },
                    "freshness": {
                        "severity": "warning"
                    }
                }
            }
        
        # Create and return data quality manager
        return DataQualityManager(self.data_quality_config)
    
    def _configure_entity_specific_monitors(self, entity_name: str) -> None:
        """
        Configure entity-specific monitors.
        
        Args:
            entity_name: Name of the entity to configure monitors for
        """
        # Configure format monitor with entity-specific rules
        if "format" in self.data_quality_manager.monitors:
            format_monitor = self.data_quality_manager.monitors["format"]
            
            # Entity-specific format rules
            if entity_name == "article":
                format_monitor.add_rule("number", r"^\d{1,10}$", "Article number must be 1-10 digits")
                format_monitor.add_rule("manufacturerNumber", r"^[A-Za-z0-9\-]{1,20}$", 
                                       "Manufacturer number must be alphanumeric with hyphens, 1-20 chars")
            elif entity_name == "customer":
                format_monitor.add_rule("number", r"^\d{1,10}$", "Customer number must be 1-10 digits")
                format_monitor.add_rule("name1", r"^.{1,100}$", "Name1 must be 1-100 characters")
            elif entity_name == "order":
                format_monitor.add_rule("number", r"^\d{1,10}$", "Order number must be 1-10 digits")
                format_monitor.add_rule("status", r"^(open|closed|canceled)$", 
                                       "Status must be one of: open, closed, canceled")
        
        # Configure freshness monitor with entity-specific rules
        if "freshness" in self.data_quality_manager.monitors:
            freshness_monitor = self.data_quality_manager.monitors["freshness"]
            
            # Entity-specific freshness rules
            if entity_name == "article":
                freshness_monitor.add_rule("lastChange", 30, "Article data should be less than 30 days old")
            elif entity_name == "customer":
                freshness_monitor.add_rule("lastChange", 60, "Customer data should be less than 60 days old")
            elif entity_name == "order":
                freshness_monitor.add_rule("lastChange", 7, "Order data should be less than 7 days old")
            elif entity_name == "sale":
                freshness_monitor.add_rule("saleDate", 7, "Sales data should be less than 7 days old")
            elif entity_name == "inventory":
                freshness_monitor.add_rule("lastChange", 1, "Inventory data should be less than 1 day old")
    
    def get_table_data(self, table_name: str, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Get data from a table in the destination database.
        
        Args:
            table_name: Name of the table to get data from
            limit: Maximum number of rows to retrieve (None for all)
            
        Returns:
            pd.DataFrame: Table data as DataFrame
        """
        if table_name not in self.metadata.tables:
            logger.warning(f"Table {table_name} not found in schema {self.schema_name}")
            return pd.DataFrame()
        
        table = self.metadata.tables[f"{self.schema_name}.{table_name}"]
        
        try:
            # Create query
            query = select([table])
            if limit:
                query = query.limit(limit)
            
            # Execute query and convert to DataFrame
            with self.engine.connect() as conn:
                result = conn.execute(query)
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
            
            logger.info(f"Retrieved {len(df)} rows from {table_name}")
            return df
        except Exception as e:
            logger.error(f"Error retrieving data from {table_name}: {str(e)}")
            return pd.DataFrame()
    
    def monitor_table(self, table_name: str, force: bool = False) -> Dict[str, Any]:
        """
        Monitor data quality for a table.
        
        Args:
            table_name: Name of the table to monitor
            force: Whether to force operation despite quality issues
            
        Returns:
            Dict[str, Any]: Monitoring results
        """
        # Get table data
        data = self.get_table_data(table_name)
        
        if data.empty:
            logger.warning(f"No data to monitor for {table_name}")
            return {
                "status": "warning",
                "message": f"No data to monitor for {table_name}",
                "rows": 0
            }
        
        # Configure entity-specific monitors
        self._configure_entity_specific_monitors(table_name)
        
        # Run data quality checks
        logger.info(f"Running data quality checks on {table_name} data")
        quality_results = self.data_quality_manager.run_monitors(
            data, 
            entity_name=table_name
        )
        
        # Save quality results
        results_file = os.path.join(
            self.quality_output_dir, 
            f"{table_name}_quality_results.json"
        )
        with open(results_file, 'w') as f:
            json.dump(quality_results, f, indent=2)
        logger.info(f"Saved quality results to {results_file}")
        
        # Check for critical issues
        critical_alerts = [
            alert for alert in quality_results.get("all_alerts", [])
            if alert.get("severity") in ["error", "critical"]
        ]
        
        if critical_alerts and not force:
            logger.error(
                f"Critical data quality issues detected for {table_name}. "
                f"Use force=True to process anyway."
            )
            return {
                "status": "error",
                "message": f"Critical data quality issues detected for {table_name}",
                "quality_results": quality_results,
                "rows": len(data),
                "errors": len(critical_alerts)
            }
        
        return {
            "status": "success",
            "message": f"Data quality checks completed for {table_name}",
            "quality_results": quality_results,
            "rows": len(data),
            "alerts": len(quality_results.get("all_alerts", []))
        }
    
    def monitor_all_tables(self, force: bool = False) -> Dict[str, Dict[str, Any]]:
        """
        Monitor data quality for all tables in the schema.
        
        Args:
            force: Whether to force operation despite quality issues
            
        Returns:
            Dict[str, Dict[str, Any]]: Monitoring results for each table
        """
        results = {}
        
        # Get all tables in the schema
        tables = [t.name for t in self.metadata.sorted_tables]
        logger.info(f"Found {len(tables)} tables in schema {self.schema_name}")
        
        # Monitor each table
        for table_name in tables:
            logger.info(f"Monitoring {table_name}")
            results[table_name] = self.monitor_table(table_name, force)
        
        # Save summary results
        summary = {
            "timestamp": datetime.now().isoformat(),
            "schema": self.schema_name,
            "tables_monitored": len(tables),
            "tables_with_errors": sum(1 for r in results.values() if r.get("status") == "error"),
            "tables_with_warnings": sum(1 for r in results.values() if r.get("status") == "warning"),
            "total_alerts": sum(r.get("alerts", 0) for r in results.values())
        }
        
        summary_file = os.path.join(
            self.quality_output_dir, 
            f"summary_quality_results.json"
        )
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Saved summary results to {summary_file}")
        
        return results

# Example usage
if __name__ == "__main__":
    # Replace with your actual connection string
    db_connection_string = "postgresql://username:password@localhost:5432/database"
    schema_name = "prohandel"
    
    monitor = FivetranQualityMonitor(db_connection_string, schema_name)
    results = monitor.monitor_all_tables()
    
    print(f"Monitored {len(results)} tables")
    print(f"Tables with errors: {sum(1 for r in results.values() if r.get('status') == 'error')}")
    print(f"Tables with warnings: {sum(1 for r in results.values() if r.get('status') == 'warning')}")
    print(f"Total alerts: {sum(r.get('alerts', 0) for r in results.values())}")
