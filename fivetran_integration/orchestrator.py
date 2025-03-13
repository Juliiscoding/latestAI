"""
Fivetran Integration Orchestrator for the Mercurios.ai ETL pipeline.

This module orchestrates the Fivetran sync and data quality monitoring process.
It triggers Fivetran syncs, monitors their status, and applies data quality checks
to the loaded data.
"""
import os
import json
import time
import requests
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from fivetran_quality_monitor import FivetranQualityMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fivetran_orchestrator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FivetranOrchestrator:
    """
    Orchestrator for Fivetran integration.
    
    This class orchestrates the Fivetran sync and data quality monitoring process.
    It triggers Fivetran syncs, monitors their status, and applies data quality checks
    to the loaded data.
    """
    
    def __init__(self, config_path: str = 'config.json'):
        """
        Initialize the Fivetran orchestrator.
        
        Args:
            config_path: Path to the configuration file
        """
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Initialize Fivetran API client
        self.fivetran_api_key = self._get_config_value('fivetran.api_key')
        self.fivetran_api_secret = self._get_config_value('fivetran.api_secret')
        self.connector_id = self._get_config_value('fivetran.connector_id')
        self.fivetran_api_url = 'https://api.fivetran.com/v1'
        
        # Initialize data quality monitor
        db_connection_string = self._get_config_value('database.connection_string')
        schema = self._get_config_value('database.schema')
        data_quality_config = self.config.get('data_quality', {})
        
        self.quality_monitor = FivetranQualityMonitor(
            db_connection_string=db_connection_string,
            schema_name=schema,
            data_quality_config=data_quality_config
        )
        
        logger.info("Initialized Fivetran orchestrator")
    
    def _get_config_value(self, path: str, default: Any = None) -> Any:
        """
        Get a configuration value by path.
        
        Args:
            path: Path to the configuration value (e.g., 'database.connection_string')
            default: Default value if not found
            
        Returns:
            Configuration value
        """
        parts = path.split('.')
        value = self.config
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        
        # Replace environment variables
        if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
            env_var = value[2:-1]
            return os.environ.get(env_var, default)
        
        return value
    
    def _make_fivetran_request(self, endpoint: str, method: str = 'GET', 
                              data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a request to the Fivetran API.
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            data: Request data
            
        Returns:
            API response
        """
        url = f"{self.fivetran_api_url}/{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {self.fivetran_api_key}:{self.fivetran_api_secret}'
        }
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method == 'PATCH':
                response = requests.patch(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Fivetran API request failed: {str(e)}")
            raise
    
    def get_connector_status(self) -> Dict[str, Any]:
        """
        Get the status of the Fivetran connector.
        
        Returns:
            Connector status
        """
        try:
            response = self._make_fivetran_request(f"connectors/{self.connector_id}")
            return response.get('data', {})
        except Exception as e:
            logger.error(f"Failed to get connector status: {str(e)}")
            return {}
    
    def start_sync(self) -> bool:
        """
        Start a Fivetran sync.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            response = self._make_fivetran_request(
                f"connectors/{self.connector_id}/force",
                method='POST'
            )
            logger.info(f"Started Fivetran sync for connector {self.connector_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to start Fivetran sync: {str(e)}")
            return False
    
    def wait_for_sync_completion(self, timeout_minutes: int = 60, 
                                check_interval_seconds: int = 30) -> bool:
        """
        Wait for the Fivetran sync to complete.
        
        Args:
            timeout_minutes: Maximum time to wait in minutes
            check_interval_seconds: Interval between status checks in seconds
            
        Returns:
            True if sync completed successfully, False otherwise
        """
        start_time = time.time()
        timeout_seconds = timeout_minutes * 60
        
        logger.info(f"Waiting for Fivetran sync to complete (timeout: {timeout_minutes} minutes)")
        
        while time.time() - start_time < timeout_seconds:
            status = self.get_connector_status()
            
            if not status:
                logger.warning("Failed to get connector status")
                time.sleep(check_interval_seconds)
                continue
            
            sync_state = status.get('sync_state', '')
            succeeded_at = status.get('succeeded_at', '')
            failed_at = status.get('failed_at', '')
            
            if sync_state == 'scheduled':
                logger.info("Sync is scheduled but not yet running")
            elif sync_state == 'syncing':
                logger.info("Sync is in progress")
            elif sync_state == 'paused':
                logger.warning("Sync is paused")
            elif sync_state == 'completed':
                logger.info(f"Sync completed successfully at {succeeded_at}")
                return True
            elif sync_state == 'failed':
                logger.error(f"Sync failed at {failed_at}")
                return False
            else:
                logger.warning(f"Unknown sync state: {sync_state}")
            
            time.sleep(check_interval_seconds)
        
        logger.error(f"Sync timed out after {timeout_minutes} minutes")
        return False
    
    def run_data_quality_checks(self, force: bool = False) -> Dict[str, Dict[str, Any]]:
        """
        Run data quality checks on the loaded data.
        
        Args:
            force: Whether to force operation despite quality issues
            
        Returns:
            Data quality results
        """
        logger.info("Running data quality checks")
        return self.quality_monitor.monitor_all_tables(force=force)
    
    def send_notifications(self, results: Dict[str, Dict[str, Any]]) -> None:
        """
        Send notifications about data quality issues.
        
        Args:
            results: Data quality results
        """
        if not self._get_config_value('notification.enabled', False):
            logger.info("Notifications are disabled")
            return
        
        # Count issues
        tables_with_errors = sum(1 for r in results.values() if r.get("status") == "error")
        tables_with_warnings = sum(1 for r in results.values() if r.get("status") == "warning")
        total_alerts = sum(r.get("alerts", 0) for r in results.values())
        
        # Skip if no issues
        if tables_with_errors == 0 and tables_with_warnings == 0:
            logger.info("No issues to notify about")
            return
        
        # Send email notification
        if self._get_config_value('notification.email.enabled', False):
            recipients = self._get_config_value('notification.email.recipients', [])
            subject_prefix = self._get_config_value('notification.email.subject_prefix', '')
            
            subject = f"{subject_prefix} Data Quality Report - {tables_with_errors} errors, {tables_with_warnings} warnings"
            
            # This is a placeholder for actual email sending logic
            logger.info(f"Would send email to {recipients} with subject: {subject}")
            logger.info(f"Email would contain {total_alerts} alerts")
        
        # Send Slack notification
        if self._get_config_value('notification.slack.enabled', False):
            webhook_url = self._get_config_value('notification.slack.webhook_url', '')
            channel = self._get_config_value('notification.slack.channel', '')
            
            # This is a placeholder for actual Slack notification logic
            logger.info(f"Would send Slack notification to {channel}")
            logger.info(f"Slack notification would contain {total_alerts} alerts")
    
    def run_full_pipeline(self, force_quality: bool = False) -> Dict[str, Any]:
        """
        Run the full pipeline: sync data and check quality.
        
        Args:
            force_quality: Whether to force quality checks despite issues
            
        Returns:
            Pipeline results
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "sync_started": False,
            "sync_completed": False,
            "quality_checks_run": False,
            "tables_with_errors": 0,
            "tables_with_warnings": 0,
            "total_alerts": 0
        }
        
        # Start sync
        sync_started = self.start_sync()
        results["sync_started"] = sync_started
        
        if not sync_started:
            logger.error("Failed to start sync, aborting pipeline")
            return results
        
        # Wait for sync to complete
        sync_completed = self.wait_for_sync_completion()
        results["sync_completed"] = sync_completed
        
        if not sync_completed:
            logger.error("Sync failed or timed out, aborting pipeline")
            return results
        
        # Run data quality checks
        quality_results = self.run_data_quality_checks(force=force_quality)
        results["quality_checks_run"] = True
        
        # Count issues
        tables_with_errors = sum(1 for r in quality_results.values() if r.get("status") == "error")
        tables_with_warnings = sum(1 for r in quality_results.values() if r.get("status") == "warning")
        total_alerts = sum(r.get("alerts", 0) for r in quality_results.values())
        
        results["tables_with_errors"] = tables_with_errors
        results["tables_with_warnings"] = tables_with_warnings
        results["total_alerts"] = total_alerts
        
        # Send notifications
        self.send_notifications(quality_results)
        
        logger.info(f"Pipeline completed: {tables_with_errors} errors, {tables_with_warnings} warnings, {total_alerts} alerts")
        
        return results

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Fivetran Integration Orchestrator')
    parser.add_argument('--config', default='config.json', help='Path to configuration file')
    parser.add_argument('--force-quality', action='store_true', help='Force quality checks despite issues')
    parser.add_argument('--sync-only', action='store_true', help='Only run the sync, skip quality checks')
    parser.add_argument('--quality-only', action='store_true', help='Only run quality checks, skip sync')
    
    args = parser.parse_args()
    
    orchestrator = FivetranOrchestrator(config_path=args.config)
    
    if args.sync_only:
        # Only run sync
        sync_started = orchestrator.start_sync()
        if sync_started:
            orchestrator.wait_for_sync_completion()
    elif args.quality_only:
        # Only run quality checks
        quality_results = orchestrator.run_data_quality_checks(force=args.force_quality)
        orchestrator.send_notifications(quality_results)
    else:
        # Run full pipeline
        orchestrator.run_full_pipeline(force_quality=args.force_quality)

if __name__ == "__main__":
    main()
