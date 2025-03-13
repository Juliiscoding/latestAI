"""
Freshness monitor for data quality.

This monitor checks if data is up-to-date based on timestamp columns.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import logging

from data_quality.base_monitor import BaseDataQualityMonitor

logger = logging.getLogger(__name__)


class FreshnessMonitor(BaseDataQualityMonitor):
    """
    Monitor for checking data freshness/timeliness.
    
    This monitor checks if data is up-to-date based on timestamp columns.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, name: str = "Freshness Monitor"):
        """
        Initialize the FreshnessMonitor.
        
        Args:
            config: Configuration dictionary with the following options:
                - freshness_rules: List of freshness validation rules
                - reference_time: Reference time for freshness checks (default: current time)
                - severity: Severity level for alerts
            name: Name of the monitor
        """
        super().__init__(name, config)
        
        # Set default configuration
        self.freshness_rules = self.config.get("freshness_rules", [])
        self.reference_time = self.config.get("reference_time")
        self.severity = self.config.get("severity", "warning")
        
        # Set reference time to current time if not specified
        if self.reference_time is None:
            self.reference_time = datetime.now()
        elif isinstance(self.reference_time, str):
            try:
                self.reference_time = datetime.fromisoformat(self.reference_time)
            except ValueError:
                logger.error(f"Invalid reference time format: {self.reference_time}")
                self.reference_time = datetime.now()
    
    def run(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """
        Run freshness checks on the data.
        
        Args:
            data: DataFrame to check
            **kwargs: Additional arguments including:
                - reference_time: Override the reference time for this run
            
        Returns:
            Dict[str, Any]: Freshness check results
        """
        # Initialize results
        results = {
            "metrics": {
                "freshness_checks": {},
                "stale_counts": {},
                "stale_ratios": {},
                "overall": {
                    "total_stale": 0,
                    "total_records": 0,
                    "overall_stale_ratio": 0.0,
                    "reference_time": datetime.now().isoformat()
                }
            },
            "alerts": []
        }
        
        # Update reference time if provided in kwargs
        reference_time = kwargs.get("reference_time", self.reference_time)
        if isinstance(reference_time, str):
            try:
                reference_time = datetime.fromisoformat(reference_time)
            except ValueError:
                logger.error(f"Invalid reference time format: {reference_time}")
                reference_time = self.reference_time
        
        # Update reference time in results
        results["metrics"]["overall"]["reference_time"] = reference_time.isoformat()
        
        total_stale = 0
        total_records = 0
        
        # Check each freshness rule
        for rule in self.freshness_rules:
            rule_name = rule["name"]
            column = rule.get("column")
            max_age = rule.get("max_age")
            max_age_unit = rule.get("max_age_unit", "days")
            threshold = rule.get("threshold", 1.0)  # Default: all records must be fresh
            severity = rule.get("severity", self.severity)
            
            # Skip if column or max_age not specified
            if not column or max_age is None:
                logger.warning(f"Missing column or max_age for freshness rule {rule_name}")
                continue
            
            # Skip if column not in data
            if column not in data.columns:
                logger.warning(f"Column {column} not found in data")
                continue
            
            # Skip if column is all NaN
            if data[column].isna().all():
                logger.info(f"Column {column} is all NaN, skipping freshness check")
                continue
            
            # Convert max_age to timedelta
            if max_age_unit == "seconds":
                max_timedelta = timedelta(seconds=max_age)
            elif max_age_unit == "minutes":
                max_timedelta = timedelta(minutes=max_age)
            elif max_age_unit == "hours":
                max_timedelta = timedelta(hours=max_age)
            elif max_age_unit == "days":
                max_timedelta = timedelta(days=max_age)
            elif max_age_unit == "weeks":
                max_timedelta = timedelta(weeks=max_age)
            elif max_age_unit == "months":
                # Approximate months as 30 days
                max_timedelta = timedelta(days=30 * max_age)
            elif max_age_unit == "years":
                # Approximate years as 365 days
                max_timedelta = timedelta(days=365 * max_age)
            else:
                logger.warning(f"Invalid max_age_unit for freshness rule {rule_name}: {max_age_unit}")
                continue
            
            # Calculate cutoff time
            cutoff_time = reference_time - max_timedelta
            
            # Convert column to datetime if needed
            try:
                if data[column].dtype != 'datetime64[ns]':
                    datetime_column = pd.to_datetime(data[column])
                else:
                    datetime_column = data[column]
            except Exception as e:
                logger.error(f"Error converting column {column} to datetime: {str(e)}")
                continue
            
            # Check freshness
            stale_mask = datetime_column < cutoff_time
            stale_count = stale_mask.sum()
            total_count = datetime_column.notna().sum()
            stale_ratio = stale_count / total_count if total_count > 0 else 0
            
            # Update totals
            total_stale += stale_count
            total_records += total_count
            
            # Calculate age statistics
            age_timedeltas = reference_time - datetime_column
            age_days = age_timedeltas.dt.total_seconds() / (24 * 3600)
            
            # Store metrics
            results["metrics"]["freshness_checks"][rule_name] = {
                "column": column,
                "max_age": max_age,
                "max_age_unit": max_age_unit,
                "reference_time": reference_time.isoformat(),
                "cutoff_time": cutoff_time.isoformat(),
                "stale_count": int(stale_count),
                "total_count": int(total_count),
                "stale_ratio": float(stale_ratio),
                "min_age_days": float(age_days.min()) if not age_days.empty and not pd.isna(age_days.min()) else None,
                "max_age_days": float(age_days.max()) if not age_days.empty and not pd.isna(age_days.max()) else None,
                "mean_age_days": float(age_days.mean()) if not age_days.empty and not pd.isna(age_days.mean()) else None,
                "median_age_days": float(age_days.median()) if not age_days.empty and not pd.isna(age_days.median()) else None
            }
            
            # Store stale counts and ratios
            results["metrics"]["stale_counts"][rule_name] = int(stale_count)
            results["metrics"]["stale_ratios"][rule_name] = float(stale_ratio)
            
            # Generate alert if stale ratio exceeds threshold
            if stale_ratio > threshold:
                alert = {
                    "severity": severity,
                    "message": f"Data freshness check failed for rule '{rule_name}': {stale_count} out of {total_count} records ({stale_ratio:.2%}) are older than {max_age} {max_age_unit}",
                    "monitor": "freshness",
                    "rule": rule_name,
                    "column": column,
                    "max_age": max_age,
                    "max_age_unit": max_age_unit,
                    "stale_count": int(stale_count),
                    "stale_ratio": float(stale_ratio),
                    "threshold": float(threshold),
                    "reference_time": reference_time.isoformat(),
                    "timestamp": datetime.now().isoformat()
                }
                results["alerts"].append(alert)
                
                # Log alert
                logger.warning(f"Freshness alert: {alert['message']}")
        
        # Calculate overall metrics
        overall_stale_ratio = total_stale / total_records if total_records > 0 else 0
        
        results["metrics"]["overall"] = {
            "total_stale": int(total_stale),
            "total_records": int(total_records),
            "overall_stale_ratio": float(overall_stale_ratio),
            "reference_time": reference_time.isoformat()
        }
        
        # Generate overall alert if needed
        if total_records > 0 and overall_stale_ratio > 0.5:  # If more than half of the records are stale
            alert = {
                "severity": self.severity,
                "message": f"Overall data freshness check failed: {total_stale} out of {total_records} records ({overall_stale_ratio:.2%}) are stale",
                "monitor": "freshness",
                "stale_count": int(total_stale),
                "stale_ratio": float(overall_stale_ratio),
                "threshold": 0.5,
                "reference_time": reference_time.isoformat(),
                "timestamp": datetime.now().isoformat()
            }
            results["alerts"].append(alert)
            
            # Log alert
            logger.warning(f"Overall freshness alert: {alert['message']}")
        
        return results
