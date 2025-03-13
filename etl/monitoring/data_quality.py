"""
Data quality monitoring module for the ProHandel ETL pipeline.
This module provides functions to monitor the quality and completeness of the data.
"""

import json
import logging
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class DataQualityMonitor:
    """
    Monitor data quality and completeness for the ProHandel ETL pipeline.
    """
    
    def __init__(self, log_path: Optional[str] = None):
        """
        Initialize the DataQualityMonitor.
        
        Args:
            log_path: Path to store data quality logs. If None, logs will only be output to the logger.
        """
        self.log_path = log_path
        self.metrics = {}
        
    def check_completeness(self, entity_name: str, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check the completeness of the data by calculating the percentage of non-null values for each field.
        
        Args:
            entity_name: Name of the entity being checked
            data: List of dictionaries containing the data
            
        Returns:
            Dictionary containing completeness metrics
        """
        if not data:
            logger.warning(f"No data to check completeness for {entity_name}")
            return {"entity": entity_name, "record_count": 0, "fields": {}}
        
        df = pd.DataFrame(data)
        total_records = len(df)
        completeness = {}
        
        for column in df.columns:
            non_null_count = df[column].count()
            completeness[column] = {
                "non_null_count": int(non_null_count),
                "null_count": int(total_records - non_null_count),
                "completeness_pct": round(100 * non_null_count / total_records, 2)
            }
        
        metrics = {
            "entity": entity_name,
            "timestamp": datetime.now().isoformat(),
            "record_count": total_records,
            "fields": completeness
        }
        
        self.metrics[f"{entity_name}_completeness"] = metrics
        return metrics
    
    def check_value_distribution(self, entity_name: str, data: List[Dict[str, Any]], 
                                 fields: List[str]) -> Dict[str, Any]:
        """
        Check the distribution of values for specified fields.
        
        Args:
            entity_name: Name of the entity being checked
            data: List of dictionaries containing the data
            fields: List of fields to check value distribution for
            
        Returns:
            Dictionary containing value distribution metrics
        """
        if not data:
            logger.warning(f"No data to check value distribution for {entity_name}")
            return {"entity": entity_name, "record_count": 0, "fields": {}}
        
        df = pd.DataFrame(data)
        total_records = len(df)
        distributions = {}
        
        for field in fields:
            if field in df.columns:
                value_counts = df[field].value_counts(dropna=False).to_dict()
                distributions[field] = {
                    "unique_values": len(value_counts),
                    "top_values": dict(sorted(value_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
                    "null_count": int(df[field].isna().sum())
                }
        
        metrics = {
            "entity": entity_name,
            "timestamp": datetime.now().isoformat(),
            "record_count": total_records,
            "fields": distributions
        }
        
        self.metrics[f"{entity_name}_distribution"] = metrics
        return metrics
    
    def check_date_range(self, entity_name: str, data: List[Dict[str, Any]], 
                         date_fields: List[str]) -> Dict[str, Any]:
        """
        Check the date range for specified date fields.
        
        Args:
            entity_name: Name of the entity being checked
            data: List of dictionaries containing the data
            date_fields: List of date fields to check
            
        Returns:
            Dictionary containing date range metrics
        """
        if not data:
            logger.warning(f"No data to check date range for {entity_name}")
            return {"entity": entity_name, "record_count": 0, "fields": {}}
        
        df = pd.DataFrame(data)
        total_records = len(df)
        date_ranges = {}
        
        for field in date_fields:
            if field in df.columns:
                # Convert to datetime, coerce errors to NaT
                df[field] = pd.to_datetime(df[field], errors='coerce')
                
                if df[field].count() > 0:
                    min_date = df[field].min()
                    max_date = df[field].max()
                    
                    date_ranges[field] = {
                        "min_date": min_date.isoformat() if not pd.isna(min_date) else None,
                        "max_date": max_date.isoformat() if not pd.isna(max_date) else None,
                        "range_days": (max_date - min_date).days if not pd.isna(min_date) and not pd.isna(max_date) else None,
                        "null_count": int(df[field].isna().sum())
                    }
                else:
                    date_ranges[field] = {
                        "min_date": None,
                        "max_date": None,
                        "range_days": None,
                        "null_count": int(df[field].isna().sum())
                    }
        
        metrics = {
            "entity": entity_name,
            "timestamp": datetime.now().isoformat(),
            "record_count": total_records,
            "fields": date_ranges
        }
        
        self.metrics[f"{entity_name}_date_range"] = metrics
        return metrics
    
    def check_numeric_stats(self, entity_name: str, data: List[Dict[str, Any]], 
                           numeric_fields: List[str]) -> Dict[str, Any]:
        """
        Calculate statistics for numeric fields.
        
        Args:
            entity_name: Name of the entity being checked
            data: List of dictionaries containing the data
            numeric_fields: List of numeric fields to check
            
        Returns:
            Dictionary containing numeric statistics
        """
        if not data:
            logger.warning(f"No data to check numeric stats for {entity_name}")
            return {"entity": entity_name, "record_count": 0, "fields": {}}
        
        df = pd.DataFrame(data)
        total_records = len(df)
        numeric_stats = {}
        
        for field in numeric_fields:
            if field in df.columns:
                # Convert to numeric, coerce errors to NaN
                df[field] = pd.to_numeric(df[field], errors='coerce')
                
                if df[field].count() > 0:
                    numeric_stats[field] = {
                        "min": float(df[field].min()) if not pd.isna(df[field].min()) else None,
                        "max": float(df[field].max()) if not pd.isna(df[field].max()) else None,
                        "mean": float(df[field].mean()) if not pd.isna(df[field].mean()) else None,
                        "median": float(df[field].median()) if not pd.isna(df[field].median()) else None,
                        "std_dev": float(df[field].std()) if not pd.isna(df[field].std()) else None,
                        "null_count": int(df[field].isna().sum())
                    }
                else:
                    numeric_stats[field] = {
                        "min": None,
                        "max": None,
                        "mean": None,
                        "median": None,
                        "std_dev": None,
                        "null_count": int(df[field].isna().sum())
                    }
        
        metrics = {
            "entity": entity_name,
            "timestamp": datetime.now().isoformat(),
            "record_count": total_records,
            "fields": numeric_stats
        }
        
        self.metrics[f"{entity_name}_numeric_stats"] = metrics
        return metrics
    
    def detect_anomalies(self, entity_name: str, data: List[Dict[str, Any]], 
                         numeric_fields: List[str], z_threshold: float = 3.0) -> Dict[str, Any]:
        """
        Detect anomalies in numeric fields using z-score.
        
        Args:
            entity_name: Name of the entity being checked
            data: List of dictionaries containing the data
            numeric_fields: List of numeric fields to check for anomalies
            z_threshold: Z-score threshold for anomaly detection
            
        Returns:
            Dictionary containing anomaly detection results
        """
        if not data:
            logger.warning(f"No data to detect anomalies for {entity_name}")
            return {"entity": entity_name, "record_count": 0, "fields": {}}
        
        df = pd.DataFrame(data)
        total_records = len(df)
        anomalies = {}
        
        for field in numeric_fields:
            if field in df.columns:
                # Convert to numeric, coerce errors to NaN
                df[field] = pd.to_numeric(df[field], errors='coerce')
                
                if df[field].count() > 0:
                    mean = df[field].mean()
                    std = df[field].std()
                    
                    if std > 0:
                        df[f'{field}_zscore'] = (df[field] - mean) / std
                        anomaly_records = df[abs(df[f'{field}_zscore']) > z_threshold]
                        
                        anomalies[field] = {
                            "anomaly_count": len(anomaly_records),
                            "anomaly_pct": round(100 * len(anomaly_records) / total_records, 2),
                            "min_anomaly": float(anomaly_records[field].min()) if not anomaly_records.empty else None,
                            "max_anomaly": float(anomaly_records[field].max()) if not anomaly_records.empty else None
                        }
                    else:
                        anomalies[field] = {
                            "anomaly_count": 0,
                            "anomaly_pct": 0,
                            "min_anomaly": None,
                            "max_anomaly": None
                        }
        
        metrics = {
            "entity": entity_name,
            "timestamp": datetime.now().isoformat(),
            "record_count": total_records,
            "fields": anomalies
        }
        
        self.metrics[f"{entity_name}_anomalies"] = metrics
        return metrics
    
    def save_metrics(self, output_path: Optional[str] = None) -> None:
        """
        Save all collected metrics to a JSON file.
        
        Args:
            output_path: Path to save the metrics. If None, uses the log_path from initialization.
        """
        path = output_path or self.log_path
        if not path:
            logger.warning("No path specified for saving metrics")
            return
        
        with open(path, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        logger.info(f"Saved data quality metrics to {path}")
    
    def generate_report(self) -> str:
        """
        Generate a human-readable report of the data quality metrics.
        
        Returns:
            String containing the report
        """
        report = []
        report.append("# Data Quality Report")
        report.append(f"Generated at: {datetime.now().isoformat()}")
        report.append("\n")
        
        for metric_name, metric_data in self.metrics.items():
            entity = metric_data.get("entity", "Unknown")
            record_count = metric_data.get("record_count", 0)
            
            report.append(f"## {entity} - {metric_name.split('_')[-1].title()}")
            report.append(f"Total Records: {record_count}")
            report.append("\n")
            
            if "fields" in metric_data:
                for field_name, field_metrics in metric_data["fields"].items():
                    report.append(f"### {field_name}")
                    for metric_key, metric_value in field_metrics.items():
                        report.append(f"- {metric_key}: {metric_value}")
                    report.append("\n")
            
            report.append("\n")
        
        return "\n".join(report)


def monitor_entity_data(entity_name: str, data: List[Dict[str, Any]], 
                       numeric_fields: Optional[List[str]] = None,
                       date_fields: Optional[List[str]] = None,
                       categorical_fields: Optional[List[str]] = None,
                       output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Comprehensive monitoring of entity data quality.
    
    Args:
        entity_name: Name of the entity being monitored
        data: List of dictionaries containing the data
        numeric_fields: List of numeric fields to analyze
        date_fields: List of date fields to analyze
        categorical_fields: List of categorical fields to analyze
        output_path: Path to save the metrics
        
    Returns:
        Dictionary containing all metrics
    """
    monitor = DataQualityMonitor(output_path)
    
    # Check completeness for all fields
    completeness = monitor.check_completeness(entity_name, data)
    
    # Check specific field types if provided
    if numeric_fields:
        numeric_stats = monitor.check_numeric_stats(entity_name, data, numeric_fields)
        anomalies = monitor.detect_anomalies(entity_name, data, numeric_fields)
    
    if date_fields:
        date_range = monitor.check_date_range(entity_name, data, date_fields)
    
    if categorical_fields:
        distributions = monitor.check_value_distribution(entity_name, data, categorical_fields)
    
    # Save all metrics
    if output_path:
        monitor.save_metrics(output_path)
    
    # Generate report
    report = monitor.generate_report()
    logger.info(f"Data quality report for {entity_name}:\n{report}")
    
    return monitor.metrics
