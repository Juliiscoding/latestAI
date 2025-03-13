"""
Base monitor for data quality monitoring.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Tuple
import pandas as pd
from datetime import datetime

from etl.utils.logger import logger


class BaseDataQualityMonitor(ABC):
    """
    Base class for all data quality monitors.
    
    This abstract class defines the interface for all data quality monitors
    in the Mercurios.ai Predictive Inventory Management tool.
    """
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base data quality monitor.
        
        Args:
            name (str): Name of the monitor
            config (Dict[str, Any], optional): Configuration parameters for the monitor
        """
        self.name = name
        self.config = config or {}
        self.metrics = {}
        self.alerts = []
        self.last_run = None
        logger.info(f"Initialized {self.name} data quality monitor")
    
    @abstractmethod
    def run(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """
        Run the data quality monitor on the provided data.
        
        Args:
            data (pd.DataFrame): Data to monitor
            **kwargs: Additional parameters
            
        Returns:
            Dict[str, Any]: Monitoring results
        """
        pass
    
    def check_threshold(self, metric_name: str, metric_value: float, 
                       threshold: float, comparison: str = 'lt',
                       severity: str = 'warning') -> bool:
        """
        Check if a metric value exceeds a threshold.
        
        Args:
            metric_name (str): Name of the metric
            metric_value (float): Value of the metric
            threshold (float): Threshold value
            comparison (str): Comparison operator ('lt', 'gt', 'eq', 'ne', 'le', 'ge')
            severity (str): Alert severity ('info', 'warning', 'error', 'critical')
            
        Returns:
            bool: True if threshold is exceeded, False otherwise
        """
        exceeded = False
        
        if comparison == 'lt':
            exceeded = metric_value < threshold
        elif comparison == 'gt':
            exceeded = metric_value > threshold
        elif comparison == 'eq':
            exceeded = metric_value == threshold
        elif comparison == 'ne':
            exceeded = metric_value != threshold
        elif comparison == 'le':
            exceeded = metric_value <= threshold
        elif comparison == 'ge':
            exceeded = metric_value >= threshold
        
        if exceeded:
            self.add_alert(metric_name, metric_value, threshold, comparison, severity)
        
        return exceeded
    
    def add_alert(self, metric_name: str, metric_value: float, threshold: float, 
                 comparison: str, severity: str) -> None:
        """
        Add an alert to the monitor.
        
        Args:
            metric_name (str): Name of the metric
            metric_value (float): Value of the metric
            threshold (float): Threshold value
            comparison (str): Comparison operator
            severity (str): Alert severity
        """
        comparison_symbols = {
            'lt': '<',
            'gt': '>',
            'eq': '==',
            'ne': '!=',
            'le': '<=',
            'ge': '>='
        }
        
        symbol = comparison_symbols.get(comparison, comparison)
        
        alert = {
            'timestamp': datetime.now(),
            'monitor': self.name,
            'metric': metric_name,
            'value': metric_value,
            'threshold': threshold,
            'comparison': comparison,
            'message': f"{metric_name} = {metric_value} {symbol} {threshold}",
            'severity': severity
        }
        
        self.alerts.append(alert)
        
        if severity == 'critical':
            logger.critical(f"Data quality alert: {alert['message']}")
        elif severity == 'error':
            logger.error(f"Data quality alert: {alert['message']}")
        elif severity == 'warning':
            logger.warning(f"Data quality alert: {alert['message']}")
        else:
            logger.info(f"Data quality alert: {alert['message']}")
    
    def get_alerts(self, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get alerts from the monitor.
        
        Args:
            severity (str, optional): Filter alerts by severity
            
        Returns:
            List[Dict[str, Any]]: List of alerts
        """
        if severity is None:
            return self.alerts
        
        return [alert for alert in self.alerts if alert['severity'] == severity]
    
    def clear_alerts(self) -> None:
        """
        Clear all alerts from the monitor.
        """
        self.alerts = []
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get metrics from the monitor.
        
        Returns:
            Dict[str, Any]: Monitoring metrics
        """
        return self.metrics
