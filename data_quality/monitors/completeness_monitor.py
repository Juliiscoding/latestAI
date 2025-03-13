"""
Completeness monitor for data quality monitoring.
"""
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

from data_quality.base_monitor import BaseDataQualityMonitor


class CompletenessMonitor(BaseDataQualityMonitor):
    """
    Monitor for checking data completeness.
    
    This monitor checks for missing values in the data and reports
    completeness metrics for each column.
    """
    
    def __init__(self, name: str = "Completeness Monitor", 
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize the completeness monitor.
        
        Args:
            name (str): Name of the monitor
            config (Dict[str, Any], optional): Configuration parameters for the monitor
                - threshold (float): Threshold for completeness ratio (default: 0.95)
                - columns (List[str]): List of columns to monitor (default: all columns)
                - severity (str): Alert severity (default: 'warning')
        """
        super().__init__(name, config)
        self.threshold = self.config.get('threshold', 0.95)
        self.columns = self.config.get('columns', None)
        self.severity = self.config.get('severity', 'warning')
    
    def run(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """
        Run the completeness monitor on the provided data.
        
        Args:
            data (pd.DataFrame): Data to monitor
            **kwargs: Additional parameters
            
        Returns:
            Dict[str, Any]: Monitoring results
        """
        # Get columns to monitor
        columns = self.columns or data.columns
        
        # Calculate completeness for each column
        completeness = {}
        overall_completeness = 0.0
        
        for column in columns:
            if column in data.columns:
                non_null_count = data[column].count()
                total_count = len(data)
                completeness_ratio = non_null_count / total_count if total_count > 0 else 1.0
                
                completeness[column] = {
                    'non_null_count': int(non_null_count),
                    'total_count': int(total_count),
                    'completeness_ratio': float(completeness_ratio)
                }
                
                # Check threshold
                self.check_threshold(
                    f"{column}_completeness", 
                    completeness_ratio, 
                    self.threshold, 
                    'lt',  # Alert if completeness is less than threshold
                    self.severity
                )
                
                overall_completeness += completeness_ratio
        
        # Calculate overall completeness
        if columns:
            overall_completeness /= len(columns)
        
        # Store metrics
        self.metrics = {
            'column_completeness': completeness,
            'overall_completeness': float(overall_completeness)
        }
        
        # Check overall threshold
        self.check_threshold(
            "overall_completeness", 
            overall_completeness, 
            self.threshold, 
            'lt',
            self.severity
        )
        
        self.last_run = pd.Timestamp.now()
        
        return self.metrics
