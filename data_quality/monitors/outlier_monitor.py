"""
Outlier monitor for data quality monitoring.
"""
from typing import Dict, Any, List, Optional, Union, Tuple
import pandas as pd
import numpy as np
from scipy import stats

from data_quality.base_monitor import BaseDataQualityMonitor


class OutlierMonitor(BaseDataQualityMonitor):
    """
    Monitor for detecting outliers in the data.
    
    This monitor uses statistical methods to detect outliers in numerical columns.
    """
    
    def __init__(self, name: str = "Outlier Monitor", 
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize the outlier monitor.
        
        Args:
            name (str): Name of the monitor
            config (Dict[str, Any], optional): Configuration parameters for the monitor
                - method (str): Method for outlier detection ('zscore', 'iqr', 'percentile')
                - threshold (float): Threshold for outlier detection
                    - For zscore: z-score threshold (default: 3.0)
                    - For iqr: IQR multiplier (default: 1.5)
                    - For percentile: percentile threshold (default: 0.01)
                - columns (List[str]): List of columns to monitor (default: all numerical columns)
                - max_outlier_ratio (float): Maximum allowed ratio of outliers (default: 0.05)
                - severity (str): Alert severity (default: 'warning')
        """
        super().__init__(name, config)
        self.method = self.config.get('method', 'zscore')
        self.threshold = self.config.get('threshold', 3.0 if self.method == 'zscore' else 
                                         1.5 if self.method == 'iqr' else 0.01)
        self.columns = self.config.get('columns', None)
        self.max_outlier_ratio = self.config.get('max_outlier_ratio', 0.05)
        self.severity = self.config.get('severity', 'warning')
    
    def detect_outliers_zscore(self, data: pd.Series) -> Tuple[pd.Series, float]:
        """
        Detect outliers using z-score method.
        
        Args:
            data (pd.Series): Data to analyze
            
        Returns:
            Tuple[pd.Series, float]: Boolean mask of outliers and outlier ratio
        """
        z_scores = np.abs(stats.zscore(data, nan_policy='omit'))
        outliers = pd.Series(z_scores > self.threshold, index=data.index)
        outlier_ratio = outliers.mean() if len(outliers) > 0 else 0.0
        return outliers, outlier_ratio
    
    def detect_outliers_iqr(self, data: pd.Series) -> Tuple[pd.Series, float]:
        """
        Detect outliers using IQR method.
        
        Args:
            data (pd.Series): Data to analyze
            
        Returns:
            Tuple[pd.Series, float]: Boolean mask of outliers and outlier ratio
        """
        q1 = data.quantile(0.25)
        q3 = data.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - (self.threshold * iqr)
        upper_bound = q3 + (self.threshold * iqr)
        
        outliers = (data < lower_bound) | (data > upper_bound)
        outlier_ratio = outliers.mean() if len(outliers) > 0 else 0.0
        return outliers, outlier_ratio
    
    def detect_outliers_percentile(self, data: pd.Series) -> Tuple[pd.Series, float]:
        """
        Detect outliers using percentile method.
        
        Args:
            data (pd.Series): Data to analyze
            
        Returns:
            Tuple[pd.Series, float]: Boolean mask of outliers and outlier ratio
        """
        lower_bound = data.quantile(self.threshold)
        upper_bound = data.quantile(1 - self.threshold)
        
        outliers = (data < lower_bound) | (data > upper_bound)
        outlier_ratio = outliers.mean() if len(outliers) > 0 else 0.0
        return outliers, outlier_ratio
    
    def run(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """
        Run the outlier monitor on the provided data.
        
        Args:
            data (pd.DataFrame): Data to monitor
            **kwargs: Additional parameters
            
        Returns:
            Dict[str, Any]: Monitoring results
        """
        # Get numerical columns
        numerical_columns = data.select_dtypes(include=['number']).columns.tolist()
        
        # Get columns to monitor
        columns = self.columns or numerical_columns
        columns = [col for col in columns if col in numerical_columns]
        
        # Detect outliers for each column
        outliers = {}
        overall_outlier_ratio = 0.0
        
        for column in columns:
            # Skip columns with all missing values
            if data[column].isna().all():
                continue
                
            # Skip columns with constant values
            if data[column].nunique() <= 1:
                continue
            
            # Detect outliers based on the selected method
            if self.method == 'zscore':
                column_outliers, outlier_ratio = self.detect_outliers_zscore(data[column].dropna())
            elif self.method == 'iqr':
                column_outliers, outlier_ratio = self.detect_outliers_iqr(data[column].dropna())
            elif self.method == 'percentile':
                column_outliers, outlier_ratio = self.detect_outliers_percentile(data[column].dropna())
            else:
                # Default to z-score
                column_outliers, outlier_ratio = self.detect_outliers_zscore(data[column].dropna())
            
            # Store outlier information
            outliers[column] = {
                'outlier_count': int(column_outliers.sum()),
                'total_count': int(len(column_outliers)),
                'outlier_ratio': float(outlier_ratio),
                'outlier_indices': column_outliers[column_outliers].index.tolist()
            }
            
            # Check threshold
            self.check_threshold(
                f"{column}_outlier_ratio", 
                outlier_ratio, 
                self.max_outlier_ratio, 
                'gt',  # Alert if outlier ratio is greater than threshold
                self.severity
            )
            
            overall_outlier_ratio += outlier_ratio
        
        # Calculate overall outlier ratio
        if columns:
            overall_outlier_ratio /= len(columns)
        
        # Store metrics
        self.metrics = {
            'column_outliers': outliers,
            'overall_outlier_ratio': float(overall_outlier_ratio),
            'method': self.method,
            'threshold': self.threshold
        }
        
        # Check overall threshold
        self.check_threshold(
            "overall_outlier_ratio", 
            overall_outlier_ratio, 
            self.max_outlier_ratio, 
            'gt',
            self.severity
        )
        
        self.last_run = pd.Timestamp.now()
        
        return self.metrics
