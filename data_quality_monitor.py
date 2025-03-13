#!/usr/bin/env python3
"""
Data Quality Monitoring Script for ProHandel Data

This script connects to your data warehouse and runs a series of data quality checks
on the ProHandel data synced via Fivetran. It generates a report of any issues found.

Usage:
    python data_quality_monitor.py --config config.json

Configuration file should contain:
    - Database connection details
    - Tables to check
    - Checks to run
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta

import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, text

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("data_quality_monitor.log")
    ]
)
logger = logging.getLogger("data_quality_monitor")

class DataQualityMonitor:
    """Class to monitor data quality for ProHandel data."""
    
    def __init__(self, config_path):
        """Initialize with configuration file."""
        self.config = self._load_config(config_path)
        self.engine = self._create_db_engine()
        self.issues = []
        
    def _load_config(self, config_path):
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            sys.exit(1)
            
    def _create_db_engine(self):
        """Create SQLAlchemy engine from config."""
        db_config = self.config.get("database", {})
        connection_string = f"postgresql://{db_config.get('user')}:{db_config.get('password')}@{db_config.get('host')}:{db_config.get('port')}/{db_config.get('dbname')}"
        
        try:
            return create_engine(connection_string)
        except Exception as e:
            logger.error(f"Failed to create database engine: {e}")
            sys.exit(1)
    
    def run_checks(self):
        """Run all configured data quality checks."""
        logger.info("Starting data quality checks...")
        
        for table in self.config.get("tables", []):
            table_name = table.get("name")
            logger.info(f"Checking table: {table_name}")
            
            # Run all configured checks for this table
            self._check_record_count(table)
            self._check_null_values(table)
            self._check_duplicates(table)
            self._check_referential_integrity(table)
            self._check_freshness(table)
            self._check_value_distribution(table)
            
        return self.issues
    
    def _check_record_count(self, table):
        """Check if record count is within expected range."""
        table_name = table.get("name")
        min_count = table.get("min_count", 0)
        
        try:
            query = f"SELECT COUNT(*) as count FROM {table_name}"
            result = pd.read_sql(query, self.engine)
            count = result['count'].iloc[0]
            
            if count < min_count:
                issue = {
                    "table": table_name,
                    "check": "record_count",
                    "severity": "high",
                    "message": f"Record count ({count}) is below minimum expected ({min_count})"
                }
                self.issues.append(issue)
                logger.warning(f"Issue found: {issue['message']}")
            else:
                logger.info(f"Record count check passed for {table_name}: {count} records")
                
        except Exception as e:
            logger.error(f"Error checking record count for {table_name}: {e}")
            
    def _check_null_values(self, table):
        """Check for null values in required columns."""
        table_name = table.get("name")
        required_columns = table.get("required_columns", [])
        
        if not required_columns:
            return
            
        try:
            for column in required_columns:
                query = f"SELECT COUNT(*) as null_count FROM {table_name} WHERE {column} IS NULL"
                result = pd.read_sql(query, self.engine)
                null_count = result['null_count'].iloc[0]
                
                if null_count > 0:
                    issue = {
                        "table": table_name,
                        "column": column,
                        "check": "null_values",
                        "severity": "medium",
                        "message": f"Found {null_count} null values in required column {column}"
                    }
                    self.issues.append(issue)
                    logger.warning(f"Issue found: {issue['message']}")
                else:
                    logger.info(f"Null check passed for {table_name}.{column}")
                    
        except Exception as e:
            logger.error(f"Error checking null values for {table_name}: {e}")
            
    def _check_duplicates(self, table):
        """Check for duplicate values in unique columns."""
        table_name = table.get("name")
        unique_columns = table.get("unique_columns", [])
        
        if not unique_columns:
            return
            
        try:
            columns_str = ", ".join(unique_columns)
            query = f"""
                SELECT {columns_str}, COUNT(*) as dup_count
                FROM {table_name}
                GROUP BY {columns_str}
                HAVING COUNT(*) > 1
            """
            result = pd.read_sql(query, self.engine)
            
            if not result.empty:
                dup_count = len(result)
                issue = {
                    "table": table_name,
                    "columns": unique_columns,
                    "check": "duplicates",
                    "severity": "high",
                    "message": f"Found {dup_count} sets of duplicate values in columns {unique_columns}"
                }
                self.issues.append(issue)
                logger.warning(f"Issue found: {issue['message']}")
            else:
                logger.info(f"Duplicate check passed for {table_name} columns {unique_columns}")
                
        except Exception as e:
            logger.error(f"Error checking duplicates for {table_name}: {e}")
            
    def _check_referential_integrity(self, table):
        """Check referential integrity for foreign keys."""
        table_name = table.get("name")
        foreign_keys = table.get("foreign_keys", [])
        
        if not foreign_keys:
            return
            
        try:
            for fk in foreign_keys:
                column = fk.get("column")
                ref_table = fk.get("ref_table")
                ref_column = fk.get("ref_column")
                
                query = f"""
                    SELECT COUNT(*) as invalid_count
                    FROM {table_name} t
                    LEFT JOIN {ref_table} r ON t.{column} = r.{ref_column}
                    WHERE t.{column} IS NOT NULL AND r.{ref_column} IS NULL
                """
                result = pd.read_sql(query, self.engine)
                invalid_count = result['invalid_count'].iloc[0]
                
                if invalid_count > 0:
                    issue = {
                        "table": table_name,
                        "column": column,
                        "check": "referential_integrity",
                        "severity": "high",
                        "message": f"Found {invalid_count} rows with invalid references in {column} to {ref_table}.{ref_column}"
                    }
                    self.issues.append(issue)
                    logger.warning(f"Issue found: {issue['message']}")
                else:
                    logger.info(f"Referential integrity check passed for {table_name}.{column}")
                    
        except Exception as e:
            logger.error(f"Error checking referential integrity for {table_name}: {e}")
            
    def _check_freshness(self, table):
        """Check data freshness based on timestamp column."""
        table_name = table.get("name")
        timestamp_column = table.get("timestamp_column")
        max_age_hours = table.get("max_age_hours", 24)
        
        if not timestamp_column:
            return
            
        try:
            query = f"""
                SELECT MAX({timestamp_column}) as latest_timestamp
                FROM {table_name}
            """
            result = pd.read_sql(query, self.engine)
            latest_timestamp = result['latest_timestamp'].iloc[0]
            
            if latest_timestamp is None:
                logger.info(f"No timestamp data found for {table_name}")
                return
                
            # Convert to datetime if string
            if isinstance(latest_timestamp, str):
                latest_timestamp = datetime.fromisoformat(latest_timestamp.replace('Z', '+00:00'))
                
            age_hours = (datetime.now() - latest_timestamp).total_seconds() / 3600
            
            if age_hours > max_age_hours:
                issue = {
                    "table": table_name,
                    "check": "freshness",
                    "severity": "medium",
                    "message": f"Data is {age_hours:.1f} hours old, exceeding maximum age of {max_age_hours} hours"
                }
                self.issues.append(issue)
                logger.warning(f"Issue found: {issue['message']}")
            else:
                logger.info(f"Freshness check passed for {table_name}: {age_hours:.1f} hours old")
                
        except Exception as e:
            logger.error(f"Error checking freshness for {table_name}: {e}")
            
    def _check_value_distribution(self, table):
        """Check value distribution for categorical columns."""
        table_name = table.get("name")
        categorical_columns = table.get("categorical_columns", [])
        
        if not categorical_columns:
            return
            
        try:
            for column in categorical_columns:
                expected_values = column.get("expected_values", [])
                column_name = column.get("name")
                
                if not expected_values:
                    continue
                    
                # Convert list to string for SQL IN clause
                values_str = ", ".join([f"'{v}'" for v in expected_values])
                query = f"""
                    SELECT COUNT(*) as invalid_count
                    FROM {table_name}
                    WHERE {column_name} IS NOT NULL AND {column_name} NOT IN ({values_str})
                """
                result = pd.read_sql(query, self.engine)
                invalid_count = result['invalid_count'].iloc[0]
                
                if invalid_count > 0:
                    issue = {
                        "table": table_name,
                        "column": column_name,
                        "check": "value_distribution",
                        "severity": "low",
                        "message": f"Found {invalid_count} rows with unexpected values in {column_name}"
                    }
                    self.issues.append(issue)
                    logger.warning(f"Issue found: {issue['message']}")
                else:
                    logger.info(f"Value distribution check passed for {table_name}.{column_name}")
                    
        except Exception as e:
            logger.error(f"Error checking value distribution for {table_name}: {e}")
    
    def generate_report(self):
        """Generate a report of all data quality issues."""
        if not self.issues:
            logger.info("No data quality issues found!")
            return "No data quality issues found!"
            
        # Group issues by table
        issues_by_table = {}
        for issue in self.issues:
            table = issue.get("table")
            if table not in issues_by_table:
                issues_by_table[table] = []
            issues_by_table[table].append(issue)
            
        # Generate report
        report = "# Data Quality Report\n\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report += f"Total issues found: {len(self.issues)}\n\n"
        
        for table, table_issues in issues_by_table.items():
            report += f"## Table: {table}\n\n"
            report += "| Check | Severity | Message |\n"
            report += "|-------|----------|--------|\n"
            
            for issue in table_issues:
                check = issue.get("check", "")
                severity = issue.get("severity", "")
                message = issue.get("message", "")
                report += f"| {check} | {severity} | {message} |\n"
                
            report += "\n"
            
        return report
        
def main():
    """Main function to run the data quality monitor."""
    parser = argparse.ArgumentParser(description="Monitor data quality for ProHandel data")
    parser.add_argument("--config", required=True, help="Path to configuration file")
    parser.add_argument("--output", help="Path to output report file")
    args = parser.parse_args()
    
    monitor = DataQualityMonitor(args.config)
    monitor.run_checks()
    report = monitor.generate_report()
    
    if args.output:
        with open(args.output, "w") as f:
            f.write(report)
        logger.info(f"Report written to {args.output}")
    else:
        print(report)
        
if __name__ == "__main__":
    main()
