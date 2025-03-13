"""
Data quality manager for the Mercurios.ai Predictive Inventory Management tool.
"""
from typing import Dict, List, Any, Optional, Union
import pandas as pd
import json
import os
from datetime import datetime

from etl.utils.logger import logger
from data_quality.base_monitor import BaseDataQualityMonitor
from data_quality.monitors.completeness_monitor import CompletenessMonitor
from data_quality.monitors.outlier_monitor import OutlierMonitor
from data_quality.monitors.consistency_monitor import ConsistencyMonitor
from data_quality.monitors.format_monitor import FormatMonitor
from data_quality.monitors.freshness_monitor import FreshnessMonitor
from data_quality.sampling import DataSampler


class DataQualityManager:
    """
    Manager for data quality monitoring.
    
    This class coordinates the execution of multiple data quality monitors
    and aggregates their results.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the data quality manager.
        
        Args:
            config (Dict[str, Any], optional): Configuration parameters for the manager
                - output_dir (str): Directory for storing monitoring results (default: 'data_quality_reports')
                - monitors (Dict[str, Dict]): Configuration for monitors
                - sampling (Dict[str, Any]): Configuration for sampling
        """
        self.config = config or {}
        self.output_dir = self.config.get('output_dir', 'data_quality_reports')
        self.monitor_configs = self.config.get('monitors', {})
        self.monitors = {}
        self.results = {}
        self.alerts = []
        
        # Initialize sampling configuration
        self.sampling_config = self.config.get("sampling", {})
        self.enable_sampling = self.sampling_config.get("enabled", True)
        self.sampler = DataSampler(self.sampling_config)
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize monitors from config
        self._initialize_monitors()
        
        logger.info(f"Initialized data quality manager with {len(self.monitors)} monitors")
    
    def _initialize_monitors(self) -> None:
        """
        Initialize monitors from configuration.
        """
        # Initialize completeness monitor if configured
        if 'completeness' in self.monitor_configs:
            self.monitors["completeness"] = CompletenessMonitor(
                name="Completeness Monitor",
                config=self.monitor_configs["completeness"]
            )
        
        # Initialize outlier monitor if configured
        if 'outlier' in self.monitor_configs:
            self.monitors["outlier"] = OutlierMonitor(
                name="Outlier Monitor",
                config=self.monitor_configs["outlier"]
            )
        
        # Initialize consistency monitor if configured
        if 'consistency' in self.monitor_configs:
            self.monitors["consistency"] = ConsistencyMonitor(
                name="Consistency Monitor",
                config=self.monitor_configs["consistency"]
            )
            
        # Initialize format monitor if configured
        if 'format' in self.monitor_configs:
            self.monitors["format"] = FormatMonitor(
                name="Format Monitor",
                config=self.monitor_configs["format"]
            )
            
        # Initialize freshness monitor if configured
        if 'freshness' in self.monitor_configs:
            self.monitors["freshness"] = FreshnessMonitor(
                name="Freshness Monitor",
                config=self.monitor_configs["freshness"]
            )
    
    def add_monitor(self, monitor: BaseDataQualityMonitor) -> None:
        """
        Add a monitor to the manager.
        
        Args:
            monitor (BaseDataQualityMonitor): Monitor to add
        """
        self.monitors[monitor.name] = monitor
        logger.info(f"Added {monitor.name} to data quality manager")
    
    def remove_monitor(self, monitor_name: str) -> None:
        """
        Remove a monitor from the manager.
        
        Args:
            monitor_name (str): Name of the monitor to remove
        """
        if monitor_name in self.monitors:
            del self.monitors[monitor_name]
            logger.info(f"Removed {monitor_name} from data quality manager")
    
    def run_monitors(self, data: pd.DataFrame, monitors: Optional[List[str]] = None, 
                    **kwargs) -> Dict[str, Any]:
        """
        Run monitors on the provided data.
        
        Args:
            data (pd.DataFrame): Data to monitor
            monitors (List[str], optional): List of monitor names to run (default: all monitors)
            **kwargs: Additional parameters to pass to monitors
            
        Returns:
            Dict[str, Any]: Monitoring results
        """
        # Get monitors to run
        monitors_to_run = monitors or list(self.monitors.keys())
        
        # Reset results and alerts
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "data_shape": {
                "rows": len(data),
                "columns": len(data.columns)
            },
            "column_types": {col: str(dtype) for col, dtype in data.dtypes.items()},
            "monitor_results": {},
            "metrics": {},
            "all_alerts": []
        }
        self.alerts = []
        
        # Apply sampling if enabled and data is large
        sampling_metadata = {"sampled": False}
        sampled_data = data
        
        if self.enable_sampling and self.sampler.should_sample(data):
            # Determine sampling strategy
            strategy = self.sampling_config.get("strategy", "random")
            
            # Apply sampling
            sampled_data, sampling_metadata = self.sampler.sample_data(
                data, 
                strategy=strategy,
                sample_size=self.sampling_config.get("sample_size"),
                random_state=self.sampling_config.get("random_state"),
                stratify_columns=self.sampling_config.get("stratify_columns"),
                outlier_fraction=self.sampling_config.get("outlier_fraction", 0.5),
                method=self.sampling_config.get("outlier_method", "zscore"),
                threshold=self.sampling_config.get("outlier_threshold", 3.0)
            )
            
            logger.info(
                f"Applied {strategy} sampling: {sampling_metadata['sample_size']} rows "
                f"from {sampling_metadata['original_size']} ({sampling_metadata['sampling_ratio']:.2%})"
            )
        
        # Add sampling metadata to results
        self.results["sampling"] = sampling_metadata
        
        # Run monitors
        for monitor_name in monitors_to_run:
            if monitor_name in self.monitors:
                logger.info(f"Running {monitor_name}")
                monitor = self.monitors[monitor_name]
                
                try:
                    # Run monitor
                    monitor_results = monitor.run(sampled_data, **kwargs)
                    
                    # Store results
                    self.results["monitor_results"][monitor_name] = monitor_results
                    
                    # Store metrics
                    if "metrics" in monitor_results:
                        self.results["metrics"][monitor_name] = monitor_results["metrics"]
                    
                    # Collect alerts
                    if "alerts" in monitor_results:
                        self.alerts.extend(monitor_results["alerts"])
                        logger.info(f"{monitor_name} completed with {len(monitor_results['alerts'])} alerts")
                    else:
                        logger.info(f"{monitor_name} completed with 0 alerts")
                    
                except Exception as e:
                    logger.error(f"Error running {monitor_name}: {str(e)}")
        
        # Add all alerts to results
        self.results["all_alerts"] = self.alerts
        
        # If sampling was applied, add a note about extrapolation
        if sampling_metadata.get("sampled", False):
            extrapolation_note = {
                "severity": "info",
                "message": (
                    f"Data quality results are based on a sample of {sampling_metadata['sample_size']} "
                    f"rows out of {sampling_metadata['original_size']} total rows "
                    f"({sampling_metadata['sampling_ratio']:.2%}). "
                    f"Sampling method: {sampling_metadata['method']}."
                ),
                "monitor": "sampling",
                "timestamp": datetime.now().isoformat()
            }
            self.results["all_alerts"].append(extrapolation_note)
        
        return self.results
    
    def get_alerts(self, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get alerts from all monitors, optionally filtered by severity.
        
        Args:
            severity (str, optional): Filter alerts by severity
            
        Returns:
            List[Dict[str, Any]]: List of alerts
        """
        if severity is None:
            return self.alerts
        
        return [alert for alert in self.alerts if alert["severity"] == severity]
    
    def clear_alerts(self) -> None:
        """
        Clear all alerts from all monitors.
        """
        for monitor_name, monitor in self.monitors.items():
            monitor.clear_alerts()
    
    def save_results(self, filename: Optional[str] = None) -> str:
        """
        Save monitoring results to a file.
        
        Args:
            filename (str, optional): Filename for the results (default: auto-generated)
            
        Returns:
            str: Path to the saved file
        """
        if not self.results:
            logger.warning("No results to save")
            return ""
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data_quality_report_{timestamp}.json"
        
        # Ensure filename has .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        # Create full path
        filepath = os.path.join(self.output_dir, filename)
        
        # Convert results to JSON-serializable format
        serializable_results = self._make_serializable(self.results)
        
        # Save results
        with open(filepath, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        logger.info(f"Saved data quality results to {filepath}")
        
        return filepath
    
    def _make_serializable(self, obj: Any) -> Any:
        """
        Convert an object to a JSON-serializable format.
        
        Args:
            obj (Any): Object to convert
            
        Returns:
            Any: JSON-serializable object
        """
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, (pd.DataFrame, pd.Series)):
            return obj.to_dict()
        elif isinstance(obj, (pd.Timestamp, datetime)):
            return obj.isoformat()
        elif isinstance(obj, (int, float, str, bool, type(None))):
            return obj
        else:
            return str(obj)
