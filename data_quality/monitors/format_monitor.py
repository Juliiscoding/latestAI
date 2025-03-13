"""
Format validation monitor for data quality.

This monitor checks if data values conform to expected formats,
such as dates, emails, phone numbers, etc.
"""
import pandas as pd
import numpy as np
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Pattern
import logging

from data_quality.base_monitor import BaseDataQualityMonitor

logger = logging.getLogger(__name__)


class FormatMonitor(BaseDataQualityMonitor):
    """
    Monitor for validating data formats.
    
    This monitor checks if data values conform to expected formats,
    such as dates, emails, phone numbers, etc.
    """
    
    # Common regex patterns
    COMMON_PATTERNS = {
        "email": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        "phone": r'^\+?[0-9]{8,15}$',
        "url": r'^(http|https)://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$',
        "date_iso": r'^\d{4}-\d{2}-\d{2}$',
        "datetime_iso": r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
        "zip_code": r'^\d{5}(-\d{4})?$',
        "ip_address": r'^(\d{1,3}\.){3}\d{1,3}$',
        "credit_card": r'^(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35\d{3})\d{11})$',
        "alpha_only": r'^[a-zA-Z]+$',
        "alphanumeric": r'^[a-zA-Z0-9]+$',
        "numeric_only": r'^[0-9]+$',
        "uuid": r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, name: str = "Format Monitor"):
        """
        Initialize the FormatMonitor.
        
        Args:
            config: Configuration dictionary with the following options:
                - format_rules: List of format validation rules
                - max_violation_ratio: Maximum acceptable ratio of format violations
                - severity: Severity level for alerts
            name: Name of the monitor
        """
        super().__init__(name, config)
        
        # Set default configuration
        self.format_rules = self.config.get("format_rules", [])
        self.max_violation_ratio = self.config.get("max_violation_ratio", 0.05)
        self.severity = self.config.get("severity", "error")
        
        # Compile regex patterns
        self.compiled_patterns = {}
        for rule in self.format_rules:
            pattern_type = rule.get("pattern_type")
            custom_pattern = rule.get("custom_pattern")
            
            if custom_pattern:
                # Use custom pattern
                try:
                    self.compiled_patterns[rule["name"]] = re.compile(custom_pattern)
                except re.error as e:
                    logger.error(f"Invalid regex pattern for rule {rule['name']}: {e}")
            elif pattern_type and pattern_type in self.COMMON_PATTERNS:
                # Use common pattern
                pattern = self.COMMON_PATTERNS[pattern_type]
                try:
                    self.compiled_patterns[rule["name"]] = re.compile(pattern)
                except re.error as e:
                    logger.error(f"Invalid regex pattern for rule {rule['name']}: {e}")
    
    def run(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """
        Run format validation on the data.
        
        Args:
            data: DataFrame to validate
            **kwargs: Additional arguments
            
        Returns:
            Dict[str, Any]: Format validation results
        """
        # Initialize results
        results = {
            "metrics": {
                "format_violations": {},
                "violation_counts": {},
                "violation_ratios": {},
                "overall": {
                    "total_violations": 0,
                    "total_values": 0,
                    "overall_violation_ratio": 0.0
                }
            },
            "alerts": []
        }
        
        total_violations = 0
        total_values = 0
        
        # Check each format rule
        for rule in self.format_rules:
            rule_name = rule["name"]
            columns = rule.get("columns", [])
            
            # Skip if no columns specified
            if not columns:
                continue
            
            # Get compiled pattern
            compiled_pattern = self.compiled_patterns.get(rule_name)
            if not compiled_pattern:
                logger.warning(f"No compiled pattern found for rule {rule_name}")
                continue
            
            # Check each column
            for column in columns:
                if column not in data.columns:
                    logger.warning(f"Column {column} not found in data")
                    continue
                
                # Skip if column is all NaN
                if data[column].isna().all():
                    logger.info(f"Column {column} is all NaN, skipping format validation")
                    continue
                
                # Convert column to string for regex validation
                str_column = data[column].astype(str)
                
                # Apply regex validation
                mask = str_column.apply(lambda x: bool(compiled_pattern.match(x)) if pd.notna(x) else True)
                
                # Count violations
                violation_count = (~mask).sum()
                total_count = data[column].notna().sum()
                violation_ratio = violation_count / total_count if total_count > 0 else 0
                
                # Store metrics
                key = f"{column}_{rule_name}"
                results["metrics"]["format_violations"][key] = {
                    "column": column,
                    "rule": rule_name,
                    "violation_count": int(violation_count),
                    "total_count": int(total_count),
                    "violation_ratio": float(violation_ratio)
                }
                
                # Store violation counts and ratios
                results["metrics"]["violation_counts"][key] = int(violation_count)
                results["metrics"]["violation_ratios"][key] = float(violation_ratio)
                
                # Update totals
                total_violations += violation_count
                total_values += total_count
                
                # Generate alert if violation ratio exceeds threshold
                if violation_ratio > self.max_violation_ratio:
                    alert = {
                        "severity": self.severity,
                        "message": f"Format validation failed for column '{column}' with rule '{rule_name}': {violation_count} violations out of {total_count} values ({violation_ratio:.2%})",
                        "monitor": "format",
                        "column": column,
                        "rule": rule_name,
                        "violation_count": int(violation_count),
                        "violation_ratio": float(violation_ratio),
                        "threshold": float(self.max_violation_ratio),
                        "timestamp": datetime.now().isoformat()
                    }
                    results["alerts"].append(alert)
                    
                    # Log alert
                    logger.warning(f"Format validation alert: {alert['message']}")
        
        # Calculate overall metrics
        overall_violation_ratio = total_violations / total_values if total_values > 0 else 0
        
        results["metrics"]["overall"] = {
            "total_violations": int(total_violations),
            "total_values": int(total_values),
            "overall_violation_ratio": float(overall_violation_ratio)
        }
        
        # Generate overall alert if needed
        if overall_violation_ratio > self.max_violation_ratio:
            alert = {
                "severity": self.severity,
                "message": f"Overall format validation failed: {total_violations} violations out of {total_values} values ({overall_violation_ratio:.2%})",
                "monitor": "format",
                "violation_count": int(total_violations),
                "violation_ratio": float(overall_violation_ratio),
                "threshold": float(self.max_violation_ratio),
                "timestamp": datetime.now().isoformat()
            }
            results["alerts"].append(alert)
            
            # Log alert
            logger.warning(f"Overall format validation alert: {alert['message']}")
        
        return results
