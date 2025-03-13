"""
Enhanced ETL Orchestrator with integrated data quality monitoring.

This module extends the standard ETL Orchestrator to include enhanced data quality monitoring
capabilities, including format validation, freshness checks, and sampling strategies for
large datasets.
"""
from typing import Dict, List, Any, Optional, Tuple
import os
import pandas as pd
from datetime import datetime
import json

from sqlalchemy.orm import Session

from etl.orchestrator import ETLOrchestrator
from etl.utils.logger import logger
from etl.config.config import ETL_CONFIG, API_ENDPOINTS
from etl.models.models import ETLMetadata
from data_quality.manager import DataQualityManager
from data_quality.monitors.completeness_monitor import CompletenessMonitor
from data_quality.monitors.outlier_monitor import OutlierMonitor
from data_quality.monitors.consistency_monitor import ConsistencyMonitor
from data_quality.monitors.format_monitor import FormatMonitor
from data_quality.monitors.freshness_monitor import FreshnessMonitor


class EnhancedETLOrchestrator(ETLOrchestrator):
    """
    Enhanced ETL Orchestrator with integrated data quality monitoring.
    
    This class extends the standard ETL Orchestrator to include enhanced
    data quality monitoring capabilities, including format validation,
    freshness checks, and sampling strategies for large datasets.
    """
    
    def __init__(self, db_session: Session, incremental: bool = True, 
                 data_quality_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the enhanced ETL orchestrator.
        
        Args:
            db_session: SQLAlchemy database session
            incremental: Whether to use incremental loading
            data_quality_config: Configuration for data quality monitoring
        """
        super().__init__(db_session, incremental)
        
        # Initialize data quality manager
        self.data_quality_config = data_quality_config or {}
        self.data_quality_manager = self._initialize_data_quality_manager()
        self.quality_results = {}
        
        # Create output directory for data quality reports
        self.quality_output_dir = self.data_quality_config.get(
            'output_dir', 'data_quality_reports'
        )
        os.makedirs(self.quality_output_dir, exist_ok=True)
        
        logger.info(f"Initialized enhanced ETL orchestrator with data quality monitoring")
    
    def _initialize_data_quality_manager(self) -> DataQualityManager:
        """
        Initialize the data quality manager with appropriate configuration.
        
        Returns:
            DataQualityManager: Configured data quality manager
        """
        # If no config is provided, use default configuration
        if not self.data_quality_config:
            self.data_quality_config = {
                "output_dir": "data_quality_reports",
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
    
    def _extract_entity(self, entity_name: str, last_timestamp: Optional[datetime] = None) -> pd.DataFrame:
        """
        Extract data for an entity and convert to DataFrame.
        
        Args:
            entity_name: Name of the entity to extract
            last_timestamp: Timestamp of the last successful extraction
            
        Returns:
            pd.DataFrame: Extracted data as DataFrame
        """
        # Extract data using parent method (returns list of dicts)
        data_list = super()._extract_entity(entity_name, last_timestamp)
        
        # Convert to DataFrame
        if data_list:
            df = pd.DataFrame(data_list)
            logger.info(f"Converted {len(df)} {entity_name} records to DataFrame")
            return df
        else:
            logger.warning(f"No {entity_name} data extracted")
            return pd.DataFrame()
    
    def _process_entity_with_quality(self, entity_name: str, data: pd.DataFrame, 
                                     force: bool = False) -> Dict[str, Any]:
        """
        Process data for an entity with data quality monitoring.
        
        Args:
            entity_name: Name of the entity to process
            data: DataFrame containing the data
            force: Whether to force operation despite quality issues
            
        Returns:
            Dict[str, Any]: Processing results
        """
        if data.empty:
            logger.warning(f"No data to process for {entity_name}")
            return {
                "status": "warning",
                "message": f"No data to process for {entity_name}",
                "extracted": 0,
                "validated": 0,
                "transformed": 0,
                "loaded": 0
            }
        
        # Configure entity-specific monitors
        self._configure_entity_specific_monitors(entity_name)
        
        # Run data quality checks
        logger.info(f"Running data quality checks on {entity_name} data")
        quality_results = self.data_quality_manager.run_monitors(
            data, 
            entity_name=entity_name
        )
        
        # Store quality results
        self.quality_results[entity_name] = quality_results
        
        # Save quality results
        results_file = os.path.join(
            self.quality_output_dir, 
            f"{entity_name}_quality_results.json"
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
                f"Critical data quality issues detected for {entity_name}. "
                f"Use force=True to process anyway."
            )
            return {
                "status": "error",
                "message": f"Critical data quality issues detected for {entity_name}",
                "quality_results": quality_results,
                "extracted": len(data),
                "validated": 0,
                "transformed": 0,
                "loaded": 0,
                "errors": len(critical_alerts)
            }
        
        if critical_alerts and force:
            logger.warning(
                f"Processing {entity_name} despite critical data quality issues "
                f"because force=True"
            )
        
        # Continue with standard processing (validation, transformation, loading)
        try:
            # Process using parent class method
            process_result = super()._process_entity(entity_name)
            
            # Add quality results to the process result
            process_result["quality_results"] = quality_results
            
            return process_result
        except Exception as e:
            logger.error(f"Error processing {entity_name}: {e}")
            return {
                "status": "error",
                "message": f"Error processing {entity_name}: {e}",
                "quality_results": quality_results,
                "extracted": len(data),
                "validated": 0,
                "transformed": 0,
                "loaded": 0,
                "errors": 1
            }
    
    def _configure_entity_specific_monitors(self, entity_name: str) -> None:
        """
        Configure entity-specific monitors based on the entity type.
        
        Args:
            entity_name: Name of the entity to configure monitors for
        """
        # Get entity configuration
        entity_config = API_ENDPOINTS.get(entity_name, {})
        
        # Configure completeness monitor
        if "completeness" in self.data_quality_manager.monitors:
            completeness_monitor = self.data_quality_manager.monitors["completeness"]
            
            # Set entity-specific columns for completeness check
            if entity_name == "article":
                completeness_monitor.config["columns"] = [
                    "number", "name", "purchasePrice", "salePrice", "isActive"
                ]
            elif entity_name == "customer":
                completeness_monitor.config["columns"] = [
                    "number", "name1", "name2", "isActive"
                ]
            elif entity_name == "order":
                completeness_monitor.config["columns"] = [
                    "number", "created", "supplierNumber", "status"
                ]
            elif entity_name == "sale":
                completeness_monitor.config["columns"] = [
                    "articleNumber", "branchNumber", "customerNumber", "date", "quantity"
                ]
            elif entity_name == "inventory":
                completeness_monitor.config["columns"] = [
                    "articleNumber", "branchNumber", "active", "quantity"
                ]
        
        # Configure format monitor
        if "format" in self.data_quality_manager.monitors:
            format_monitor = self.data_quality_manager.monitors["format"]
            
            # Set entity-specific format rules
            format_rules = []
            
            if entity_name == "article":
                format_rules = [
                    {
                        "name": "article_number_format",
                        "columns": ["number"],
                        "custom_pattern": r"^\d+(\.\d+)?$"
                    }
                ]
            elif entity_name == "customer":
                format_rules = [
                    {
                        "name": "customer_number_format",
                        "columns": ["number"],
                        "custom_pattern": r"^\d+$"
                    },
                    {
                        "name": "email_format",
                        "columns": ["email"],
                        "pattern_type": "email"
                    }
                ]
            elif entity_name == "order":
                format_rules = [
                    {
                        "name": "order_number_format",
                        "columns": ["number"],
                        "custom_pattern": r"^\d+$"
                    }
                ]
            
            format_monitor.config["format_rules"] = format_rules
        
        # Configure freshness monitor
        if "freshness" in self.data_quality_manager.monitors:
            freshness_monitor = self.data_quality_manager.monitors["freshness"]
            
            # Set entity-specific freshness rules
            freshness_rules = []
            
            # Get timestamp field from entity config
            timestamp_field = entity_config.get("timestamp_field", "lastChange")
            
            if timestamp_field:
                freshness_rules = [
                    {
                        "name": "recent_data",
                        "column": timestamp_field,
                        "max_age": 30,
                        "max_age_unit": "days",
                        "threshold": 0.2,
                        "severity": "warning"
                    },
                    {
                        "name": "very_old_data",
                        "column": timestamp_field,
                        "max_age": 180,
                        "max_age_unit": "days",
                        "threshold": 0.5,
                        "severity": "error"
                    }
                ]
            
            freshness_monitor.config["freshness_rules"] = freshness_rules
    
    def run_etl(self, entities: Optional[List[str]] = None, 
                force: bool = False) -> Dict[str, Dict[str, Any]]:
        """
        Run the enhanced ETL pipeline with data quality monitoring.
        
        Args:
            entities: List of entity names to process (None for all)
            force: Whether to force operation despite quality issues
            
        Returns:
            Dict[str, Dict[str, Any]]: ETL results for each entity
        """
        # Determine which entities to process
        if entities is None:
            entities = list(API_ENDPOINTS.keys())
        
        logger.info(f"Starting enhanced ETL pipeline for entities: {entities}")
        
        # Get last ETL run timestamps
        last_run_timestamps = self._get_last_run_timestamps(entities)
        
        # Extract, process, and load data for each entity
        results = {}
        
        for entity_name in entities:
            try:
                # Extract data
                logger.info(f"Extracting data for {entity_name}")
                data = self._extract_entity(entity_name, last_run_timestamps.get(entity_name))
                
                # Process data with quality monitoring
                if not data.empty:
                    logger.info(f"Processing {len(data)} records for {entity_name}")
                    entity_result = self._process_entity_with_quality(entity_name, data, force)
                    results[entity_name] = entity_result
                else:
                    logger.warning(f"No data to process for {entity_name}")
                    results[entity_name] = {
                        "status": "warning",
                        "message": f"No data extracted for {entity_name}",
                        "extracted": 0,
                        "validated": 0,
                        "transformed": 0,
                        "loaded": 0
                    }
            except Exception as e:
                logger.error(f"Error processing {entity_name}: {e}")
                results[entity_name] = {
                    "status": "error",
                    "message": f"Error processing {entity_name}: {e}",
                    "extracted": 0,
                    "validated": 0,
                    "transformed": 0,
                    "loaded": 0,
                    "errors": 1
                }
        
        # Update ETL metadata
        self._update_etl_metadata(entities)
        
        logger.info(f"Enhanced ETL pipeline completed for entities: {entities}")
        
        return results
    
    def get_quality_summary(self) -> Dict[str, Any]:
        """
        Get a summary of data quality results.
        
        Returns:
            Dict[str, Any]: Summary of data quality results
        """
        if not self.quality_results:
            return {"status": "no_data", "message": "No data quality results available"}
        
        # Collect alerts by severity
        alerts_by_severity = {}
        all_alerts = []
        
        for entity, results in self.quality_results.items():
            entity_alerts = results.get("all_alerts", [])
            all_alerts.extend(entity_alerts)
            
            for alert in entity_alerts:
                severity = alert.get("severity", "info")
                if severity not in alerts_by_severity:
                    alerts_by_severity[severity] = []
                alerts_by_severity[severity].append(alert)
        
        # Create summary
        summary = {
            "timestamp": datetime.now().isoformat(),
            "entities_processed": list(self.quality_results.keys()),
            "total_alerts": len(all_alerts),
            "alerts_by_severity": {
                severity: len(alerts)
                for severity, alerts in alerts_by_severity.items()
            },
            "alerts_by_entity": {
                entity: len(results.get("all_alerts", []))
                for entity, results in self.quality_results.items()
            },
            "quality_status": "error" if alerts_by_severity.get("error", []) or 
                                        alerts_by_severity.get("critical", []) else "warning" if 
                                        alerts_by_severity.get("warning", []) else "success"
        }
        
        return summary
