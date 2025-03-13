"""
Unit tests for enhanced data quality monitors.

This module contains unit tests for the FormatMonitor and FreshnessMonitor classes.
"""
import os
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

from data_quality.monitors.format_monitor import FormatMonitor
from data_quality.monitors.freshness_monitor import FreshnessMonitor


class TestFormatMonitor(unittest.TestCase):
    """Test cases for the FormatMonitor class."""
    
    def setUp(self):
        """Set up test data."""
        # Create test data
        self.test_data = pd.DataFrame({
            "id": ["ID001", "ID002", "ID003", "ID004", "ID005", "ID-006", "ID007", "ID008", "ID009", "ID010"],
            "email": ["user1@example.com", "user2@example.com", "user3@example", "user4@example.com", 
                      "user5@example.com", "user6@example.com", "invalid-email", "user8@example.com", 
                      "user9@example.com", "user10@example.com"],
            "phone": ["+491234567890", "+491234567891", "1234567892", "+491234567893", 
                      "+491234567894", "12345", "+491234567896", "+491234567897", 
                      "+491234567898", "+491234567899"],
            "url": ["https://example.com", "http://example.com", "example.com", "https://example.com/path", 
                    "https://example.com", "https://example.com", "https://example.com", "invalid-url", 
                    "https://example.com", "https://example.com"]
        })
        
        # Configure monitor
        self.config = {
            "format_rules": [
                {
                    "name": "id_format",
                    "columns": ["id"],
                    "custom_pattern": r"^ID\d{3}$",
                    "description": "ID must be in the format ID followed by 3 digits"
                },
                {
                    "name": "email_format",
                    "columns": ["email"],
                    "pattern_type": "email",
                    "description": "Email must be in valid format"
                },
                {
                    "name": "phone_format",
                    "columns": ["phone"],
                    "custom_pattern": r"^\+\d{12}$",
                    "description": "Phone must start with + followed by 12 digits"
                },
                {
                    "name": "url_format",
                    "columns": ["url"],
                    "pattern_type": "url",
                    "description": "URL must be in valid format"
                }
            ],
            "max_violation_ratio": 0.2,
            "severity": "warning"
        }
        
        # Initialize monitor
        self.monitor = FormatMonitor(self.config)
    
    def test_run(self):
        """Test run method."""
        # Run monitor
        results = self.monitor.run(self.test_data)
        
        # Print the results structure
        print("FORMAT MONITOR RESULTS:")
        print(json.dumps(results, indent=2, default=str))
        
        # Check results
        self.assertIn("metrics", results)
        self.assertIn("violation_ratios", results["metrics"])
        self.assertIn("violation_counts", results["metrics"])
        self.assertIn("alerts", results)
        
        # Check violation ratios
        violation_ratios = results["metrics"]["violation_ratios"]
        self.assertEqual(violation_ratios.get("id_id_format", 0), 0.1)  # 1 out of 10 violates the pattern
        self.assertEqual(violation_ratios.get("email_email_format", 0), 0.2)  # 2 out of 10 violate the pattern
        self.assertEqual(violation_ratios.get("phone_phone_format", 0), 0.3)  # 3 out of 10 violate the pattern
        self.assertEqual(violation_ratios.get("url_url_format", 0), 0.2)  # 2 out of 10 violate the pattern
        
        # Check violations
        violation_counts = results["metrics"]["violation_counts"]
        self.assertEqual(violation_counts.get("id_id_format", 0), 1)
        self.assertEqual(violation_counts.get("email_email_format", 0), 2)
        self.assertEqual(violation_counts.get("phone_phone_format", 0), 3)
        self.assertEqual(violation_counts.get("url_url_format", 0), 2)
        
        # Check alerts
        alerts = results["alerts"]
        # We should have alerts for phone_format and url_format (above max_violation_ratio)
        self.assertEqual(len(alerts), 2)
        
        # Check alert details
        alert_rule_names = [alert.get("rule") for alert in alerts]
        self.assertIn("phone_format", alert_rule_names)
        self.assertIn("url_format", alert_rule_names)
        
        for alert in alerts:
            self.assertEqual(alert["severity"], "warning")
    
    def test_custom_pattern(self):
        """Test custom pattern validation."""
        # Configure monitor with custom pattern
        config = {
            "format_rules": [
                {
                    "name": "custom_pattern",
                    "columns": ["id"],
                    "custom_pattern": r"^ID\d{3}$",
                    "description": "ID must be in the format ID followed by 3 digits"
                }
            ],
            "max_violation_ratio": 0.2,
            "severity": "warning"
        }
        
        # Initialize monitor
        monitor = FormatMonitor(config)
        
        # Run monitor
        results = monitor.run(self.test_data)
        
        # Print the results structure
        print("CUSTOM PATTERN RESULTS:")
        print(json.dumps(results, indent=2, default=str))
        
        # Check results
        self.assertEqual(results["metrics"]["violation_ratios"].get("id_custom_pattern", 0), 0.1)
        self.assertEqual(results["metrics"]["violation_counts"].get("id_custom_pattern", 0), 1)
    
    def test_built_in_patterns(self):
        """Test built-in pattern validation."""
        # Configure monitor with built-in patterns
        config = {
            "format_rules": [
                {
                    "name": "email_validation",
                    "columns": ["email"],
                    "pattern_type": "email",
                    "description": "Email must be in valid format"
                },
                {
                    "name": "url_validation",
                    "columns": ["url"],
                    "pattern_type": "url",
                    "description": "URL must be in valid format"
                }
            ],
            "max_violation_ratio": 0.2,
            "severity": "warning"
        }
        
        # Initialize monitor
        monitor = FormatMonitor(config)
        
        # Run monitor
        results = monitor.run(self.test_data)
        
        # Print the results structure
        print("BUILT-IN PATTERNS RESULTS:")
        print(json.dumps(results, indent=2, default=str))
        
        # Check results
        self.assertEqual(results["metrics"]["violation_ratios"].get("email_email_validation", 0), 0.2)
        self.assertEqual(results["metrics"]["violation_ratios"].get("url_url_validation", 0), 0.2)
        self.assertEqual(results["metrics"]["violation_counts"].get("email_email_validation", 0), 2)
        self.assertEqual(results["metrics"]["violation_counts"].get("url_url_validation", 0), 2)


class TestFreshnessMonitor(unittest.TestCase):
    """Test cases for the FreshnessMonitor class."""
    
    def setUp(self):
        """Set up test data."""
        # Create base timestamp
        now = datetime.now()
        
        # Create test data
        self.test_data = pd.DataFrame({
            "id": range(1, 11),
            "last_updated": [
                now - timedelta(days=5),
                now - timedelta(days=15),
                now - timedelta(days=25),
                now - timedelta(days=35),
                now - timedelta(days=45),
                now - timedelta(days=55),
                now - timedelta(days=65),
                now - timedelta(days=75),
                now - timedelta(days=85),
                now - timedelta(days=95)
            ],
            "created_at": [
                now - timedelta(days=100),
                now - timedelta(days=100),
                now - timedelta(days=100),
                now - timedelta(days=100),
                now - timedelta(days=100),
                now - timedelta(days=100),
                now - timedelta(days=100),
                now - timedelta(days=100),
                now - timedelta(days=100),
                now - timedelta(days=100)
            ]
        })
        
        # Configure monitor
        self.config = {
            "freshness_rules": [
                {
                    "name": "recent_update",
                    "column": "last_updated",
                    "max_age": 30,
                    "max_age_unit": "days",
                    "threshold": 0.5,
                    "severity": "warning",
                    "description": "Data should be updated within the last 30 days"
                },
                {
                    "name": "very_old_data",
                    "column": "last_updated",
                    "max_age": 60,
                    "max_age_unit": "days",
                    "threshold": 0.2,
                    "severity": "error",
                    "description": "Data should not be older than 60 days"
                }
            ],
            "severity": "warning"
        }
        
        # Initialize monitor
        self.monitor = FreshnessMonitor(self.config)
    
    def test_run(self):
        """Test run method."""
        # Run monitor
        results = self.monitor.run(self.test_data)
        
        # Print the results structure
        print("FRESHNESS MONITOR RESULTS:")
        print(json.dumps(results, indent=2, default=str))
        
        # Check results
        self.assertIn("metrics", results)
        self.assertIn("stale_ratios", results["metrics"])
        self.assertIn("stale_counts", results["metrics"])
        self.assertIn("alerts", results)
        
        # Check stale ratios
        stale_ratios = results["metrics"]["stale_ratios"]
        self.assertEqual(stale_ratios.get("recent_update", 0), 0.7)  # 7 out of 10 are older than 30 days
        self.assertEqual(stale_ratios.get("very_old_data", 0), 0.4)  # 4 out of 10 are older than 60 days
        
        # Check stale records
        stale_counts = results["metrics"]["stale_counts"]
        self.assertEqual(stale_counts.get("recent_update", 0), 7)
        self.assertEqual(stale_counts.get("very_old_data", 0), 4)
        
        # Check alerts
        alerts = results["alerts"]
        # We should have alerts for both rules (above threshold)
        self.assertEqual(len(alerts), 2)
        
        # Check alert details
        alert_rule_names = [alert.get("rule") for alert in alerts]
        self.assertIn("recent_update", alert_rule_names)
        self.assertIn("very_old_data", alert_rule_names)
        
        for alert in alerts:
            if alert["rule"] == "recent_update":
                self.assertEqual(alert["severity"], "warning")
            elif alert["rule"] == "very_old_data":
                self.assertEqual(alert["severity"], "error")
    
    def test_different_time_units(self):
        """Test different time units for freshness rules."""
        # Configure monitor with different time units
        config = {
            "freshness_rules": [
                {
                    "name": "hours_rule",
                    "column": "last_updated",
                    "max_age": 24 * 30,  # 30 days in hours
                    "max_age_unit": "hours",
                    "threshold": 0.5,
                    "severity": "warning"
                },
                {
                    "name": "minutes_rule",
                    "column": "last_updated",
                    "max_age": 24 * 60 * 30,  # 30 days in minutes
                    "max_age_unit": "minutes",
                    "threshold": 0.5,
                    "severity": "warning"
                },
                {
                    "name": "seconds_rule",
                    "column": "last_updated",
                    "max_age": 24 * 60 * 60 * 30,  # 30 days in seconds
                    "max_age_unit": "seconds",
                    "threshold": 0.5,
                    "severity": "warning"
                }
            ],
            "severity": "warning"
        }
        
        # Initialize monitor
        monitor = FreshnessMonitor(config)
        
        # Run monitor
        results = monitor.run(self.test_data)
        
        # Print the results structure
        print("DIFFERENT TIME UNITS RESULTS:")
        print(json.dumps(results, indent=2, default=str))
        
        # Check results - all should be the same since they represent the same time period
        stale_ratios = results["metrics"]["stale_ratios"]
        self.assertEqual(stale_ratios.get("hours_rule", 0), 0.7)
        self.assertEqual(stale_ratios.get("minutes_rule", 0), 0.7)
        self.assertEqual(stale_ratios.get("seconds_rule", 0), 0.7)
    
    def test_reference_date(self):
        """Test reference date for freshness calculation."""
        # Create a reference date in the past
        reference_date = datetime.now() - timedelta(days=50)
        
        # Configure monitor with reference date
        config = {
            "freshness_rules": [
                {
                    "name": "recent_update",
                    "column": "last_updated",
                    "max_age": 30,
                    "max_age_unit": "days",
                    "threshold": 0.5,
                    "severity": "warning"
                }
            ],
            "severity": "warning"
        }
        
        # Initialize monitor
        monitor = FreshnessMonitor(config)
        
        # Run monitor with reference date
        results = monitor.run(self.test_data, reference_time=reference_date)
        
        # Print the results structure
        print("REFERENCE DATE RESULTS:")
        print(json.dumps(results, indent=2, default=str))
        
        # Check results - using the reference date from 50 days ago
        # Only the first 3 records would be considered fresh (less than 30 days old from the reference date)
        stale_ratios = results["metrics"]["stale_ratios"]
        self.assertEqual(stale_ratios.get("recent_update", 0), 0.7)  # 7 out of 10 are older than 30 days from reference date


if __name__ == "__main__":
    unittest.main()
