#!/usr/bin/env python3
"""
Snowflake Data Quality Monitoring Script for ProHandel Data

This script connects to your Snowflake data warehouse and runs a series of data quality checks
on the ProHandel data synced via Fivetran. It generates a report of any issues found and can
send notifications when issues are detected.

Usage:
    python snowflake_data_quality_monitor.py --config snowflake_data_quality_config.json

Configuration file should contain:
    - Snowflake connection details
    - Tables to check
    - Checks to run
    - Notification settings
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine, text
import jinja2
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("snowflake_data_quality_monitor.log")
    ]
)
logger = logging.getLogger("snowflake_data_quality_monitor")

class SnowflakeDataQualityMonitor:
    """Class to monitor data quality for ProHandel data in Snowflake."""
    
    def __init__(self, config_path):
        """Initialize with configuration file."""
        self.config = self._load_config(config_path)
        self.conn = None
        self.engine = None
        self.issues = []
        self.report_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tables_checked": 0,
            "checks_performed": 0,
            "issues_found": 0,
            "issues": [],
            "summary": {}
        }
        
    def _load_config(self, config_path):
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            sys.exit(1)
            
    def _connect_to_snowflake(self):
        """Create Snowflake connection from config."""
        db_config = self.config.get("database", {})
        
        try:
            # Get password from environment or prompt if not available
            password = db_config.get("password")
            if not password:
                password = os.environ.get("SNOWFLAKE_PASSWORD")
                if not password:
                    import getpass
                    password = getpass.getpass("Enter your Snowflake password: ")
            
            # Create direct connection
            self.conn = snowflake.connector.connect(
                user=db_config.get("user"),
                password=password,
                account=db_config.get("account"),
                warehouse=db_config.get("warehouse"),
                database=db_config.get("database"),
                schema=db_config.get("schema")
            )
            
            # Create SQLAlchemy engine for pandas integration
            self.engine = create_engine(URL(
                user=db_config.get("user"),
                password=password,
                account=db_config.get("account"),
                warehouse=db_config.get("warehouse"),
                database=db_config.get("database"),
                schema=db_config.get("schema")
            ))
            
            logger.info(f"Successfully connected to Snowflake as {db_config.get('user')}")
            
            # Test connection
            cursor = self.conn.cursor()
            cursor.execute("SELECT current_version()")
            version = cursor.fetchone()[0]
            logger.info(f"Connected to Snowflake version: {version}")
            cursor.close()
            
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Snowflake: {e}")
            return False
    
    def run_checks(self):
        """Run all configured data quality checks."""
        if not self._connect_to_snowflake():
            return self.issues
            
        logger.info("Starting data quality checks...")
        start_time = time.time()
        
        for table in self.config.get("tables", []):
            table_name = table.get("name")
            logger.info(f"Checking table: {table_name}")
            self.report_data["tables_checked"] += 1
            
            # Run all configured checks for this table
            self._check_record_count(table)
            self._check_null_values(table)
            self._check_duplicates(table)
            self._check_referential_integrity(table)
            self._check_freshness(table)
            self._check_value_ranges(table)
            
        # Close connections
        if self.conn:
            self.conn.close()
        if self.engine:
            self.engine.dispose()
            
        # Finalize report
        end_time = time.time()
        self.report_data["duration_seconds"] = round(end_time - start_time, 2)
        self.report_data["issues_found"] = len(self.issues)
        self.report_data["issues"] = self.issues
        
        # Generate summary by table and severity
        summary = {
            "by_table": {},
            "by_severity": {"high": 0, "medium": 0, "low": 0}
        }
        
        for issue in self.issues:
            table = issue.get("table")
            severity = issue.get("severity")
            
            if table not in summary["by_table"]:
                summary["by_table"][table] = 0
            summary["by_table"][table] += 1
            summary["by_severity"][severity] += 1
            
        self.report_data["summary"] = summary
        
        # Save report
        self._save_report()
        
        # Send notifications if needed
        if self.issues:
            self._send_notifications()
            
        logger.info(f"Data quality check completed. Found {len(self.issues)} issues.")
        return self.issues
    
    def _check_record_count(self, table):
        """Check if record count is within expected range."""
        table_name = table.get("name")
        min_count = table.get("min_count", 0)
        
        try:
            query = f"SELECT COUNT(*) as count FROM {table_name}"
            cursor = self.conn.cursor()
            cursor.execute(query)
            count = cursor.fetchone()[0]
            cursor.close()
            
            self.report_data["checks_performed"] += 1
            
            if count < min_count:
                issue = {
                    "table": table_name,
                    "check": "record_count",
                    "severity": "high",
                    "message": f"Record count ({count}) is below minimum expected ({min_count})",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
                cursor = self.conn.cursor()
                cursor.execute(query)
                null_count = cursor.fetchone()[0]
                cursor.close()
                
                self.report_data["checks_performed"] += 1
                
                if null_count > 0:
                    issue = {
                        "table": table_name,
                        "column": column,
                        "check": "null_values",
                        "severity": "medium",
                        "message": f"Found {null_count} null values in required column {column}",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
            
            df = pd.read_sql(query, self.engine)
            
            self.report_data["checks_performed"] += 1
            
            if not df.empty:
                dup_count = len(df)
                issue = {
                    "table": table_name,
                    "columns": unique_columns,
                    "check": "duplicates",
                    "severity": "high",
                    "message": f"Found {dup_count} sets of duplicate values in columns {unique_columns}",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
                
                cursor = self.conn.cursor()
                cursor.execute(query)
                invalid_count = cursor.fetchone()[0]
                cursor.close()
                
                self.report_data["checks_performed"] += 1
                
                if invalid_count > 0:
                    issue = {
                        "table": table_name,
                        "column": column,
                        "ref_table": ref_table,
                        "ref_column": ref_column,
                        "check": "referential_integrity",
                        "severity": "high",
                        "message": f"Found {invalid_count} records with invalid references from {table_name}.{column} to {ref_table}.{ref_column}",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    self.issues.append(issue)
                    logger.warning(f"Issue found: {issue['message']}")
                else:
                    logger.info(f"Referential integrity check passed for {table_name}.{column} -> {ref_table}.{ref_column}")
                    
        except Exception as e:
            logger.error(f"Error checking referential integrity for {table_name}: {e}")
            
    def _check_freshness(self, table):
        """Check data freshness based on timestamp column."""
        table_name = table.get("name")
        freshness = table.get("freshness", {})
        
        if not freshness:
            return
            
        timestamp_column = freshness.get("timestamp_column")
        max_age_hours = freshness.get("max_age_hours", 24)
        
        try:
            query = f"""
                SELECT MAX({timestamp_column}) as last_updated
                FROM {table_name}
            """
            
            cursor = self.conn.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            
            self.report_data["checks_performed"] += 1
            
            if result and result[0]:
                last_updated = result[0]
                if isinstance(last_updated, str):
                    last_updated = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                
                age_hours = (datetime.now() - last_updated).total_seconds() / 3600
                
                if age_hours > max_age_hours:
                    issue = {
                        "table": table_name,
                        "check": "freshness",
                        "severity": "medium",
                        "message": f"Data is stale. Last updated {age_hours:.1f} hours ago, which exceeds the maximum age of {max_age_hours} hours",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    self.issues.append(issue)
                    logger.warning(f"Issue found: {issue['message']}")
                else:
                    logger.info(f"Freshness check passed for {table_name}. Last updated {age_hours:.1f} hours ago")
            else:
                issue = {
                    "table": table_name,
                    "check": "freshness",
                    "severity": "medium",
                    "message": f"Could not determine last update time. Timestamp column {timestamp_column} may be empty",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                self.issues.append(issue)
                logger.warning(f"Issue found: {issue['message']}")
                
        except Exception as e:
            logger.error(f"Error checking freshness for {table_name}: {e}")
            
    def _check_value_ranges(self, table):
        """Check if values are within expected ranges."""
        table_name = table.get("name")
        value_ranges = table.get("value_ranges", [])
        
        if not value_ranges:
            return
            
        try:
            for value_range in value_ranges:
                column = value_range.get("column")
                min_val = value_range.get("min")
                max_val = value_range.get("max")
                
                conditions = []
                if min_val is not None:
                    conditions.append(f"{column} < {min_val}")
                if max_val is not None:
                    conditions.append(f"{column} > {max_val}")
                    
                if not conditions:
                    continue
                    
                where_clause = " OR ".join(conditions)
                query = f"""
                    SELECT COUNT(*) as invalid_count
                    FROM {table_name}
                    WHERE {where_clause}
                """
                
                cursor = self.conn.cursor()
                cursor.execute(query)
                invalid_count = cursor.fetchone()[0]
                cursor.close()
                
                self.report_data["checks_performed"] += 1
                
                if invalid_count > 0:
                    range_desc = []
                    if min_val is not None:
                        range_desc.append(f">= {min_val}")
                    if max_val is not None:
                        range_desc.append(f"<= {max_val}")
                    range_str = " and ".join(range_desc)
                    
                    issue = {
                        "table": table_name,
                        "column": column,
                        "check": "value_range",
                        "severity": "medium",
                        "message": f"Found {invalid_count} records with values outside expected range ({range_str}) in column {column}",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    self.issues.append(issue)
                    logger.warning(f"Issue found: {issue['message']}")
                else:
                    range_desc = []
                    if min_val is not None:
                        range_desc.append(f">= {min_val}")
                    if max_val is not None:
                        range_desc.append(f"<= {max_val}")
                    range_str = " and ".join(range_desc)
                    logger.info(f"Value range check passed for {table_name}.{column} ({range_str})")
                    
        except Exception as e:
            logger.error(f"Error checking value ranges for {table_name}: {e}")
            
    def _save_report(self):
        """Save the data quality report to disk."""
        report_config = self.config.get("report", {})
        output_path = report_config.get("output_path", ".")
        formats = report_config.get("format", ["json"])
        
        # Create output directory if it doesn't exist
        Path(output_path).mkdir(parents=True, exist_ok=True)
        
        # Generate timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save in requested formats
        if "json" in formats:
            json_path = os.path.join(output_path, f"data_quality_report_{timestamp}.json")
            with open(json_path, 'w') as f:
                json.dump(self.report_data, f, indent=2)
            logger.info(f"Saved JSON report to {json_path}")
            
        if "html" in formats:
            # Create HTML report using Jinja2
            try:
                template_path = os.path.join(os.path.dirname(__file__), "templates", "report_template.html")
                if not os.path.exists(template_path):
                    # Create templates directory if it doesn't exist
                    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
                    Path(templates_dir).mkdir(parents=True, exist_ok=True)
                    
                    # Create a basic HTML template
                    with open(template_path, 'w') as f:
                        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Snowflake Data Quality Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #0066cc; }
        .summary { margin: 20px 0; padding: 10px; background-color: #f0f0f0; border-radius: 5px; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #0066cc; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .high { color: red; font-weight: bold; }
        .medium { color: orange; }
        .low { color: #0066cc; }
    </style>
</head>
<body>
    <h1>Snowflake Data Quality Report</h1>
    <p>Generated on: {{ report.timestamp }}</p>
    
    <div class="summary">
        <h2>Summary</h2>
        <p>Duration: {{ report.duration_seconds }} seconds</p>
        <p>Tables checked: {{ report.tables_checked }}</p>
        <p>Checks performed: {{ report.checks_performed }}</p>
        <p>Issues found: {{ report.issues_found }}</p>
        
        <h3>Issues by Severity</h3>
        <ul>
            <li class="high">High: {{ report.summary.by_severity.high }}</li>
            <li class="medium">Medium: {{ report.summary.by_severity.medium }}</li>
            <li class="low">Low: {{ report.summary.by_severity.low }}</li>
        </ul>
        
        {% if report.summary.by_table %}
        <h3>Issues by Table</h3>
        <ul>
            {% for table, count in report.summary.by_table.items() %}
            <li>{{ table }}: {{ count }}</li>
            {% endfor %}
        </ul>
        {% endif %}
    </div>
    
    {% if report.issues %}
    <h2>Issues</h2>
    <table>
        <tr>
            <th>Severity</th>
            <th>Table</th>
            <th>Check</th>
            <th>Message</th>
            <th>Timestamp</th>
        </tr>
        {% for issue in report.issues %}
        <tr>
            <td class="{{ issue.severity }}">{{ issue.severity }}</td>
            <td>{{ issue.table }}</td>
            <td>{{ issue.check }}</td>
            <td>{{ issue.message }}</td>
            <td>{{ issue.timestamp }}</td>
        </tr>
        {% endfor %}
    </table>
    {% endif %}
</body>
</html>""")
                
                # Load the template
                env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(template_path)))
                template = env.get_template(os.path.basename(template_path))
                
                # Render the template with our data
                html_content = template.render(report=self.report_data)
                
                # Save the HTML report
                html_path = os.path.join(output_path, f"data_quality_report_{timestamp}.html")
                with open(html_path, 'w') as f:
                    f.write(html_content)
                logger.info(f"Saved HTML report to {html_path}")
                
            except Exception as e:
                logger.error(f"Error generating HTML report: {e}")
                
        # Save to Snowflake if configured
        try:
            # Create a flattened version of the report data for Snowflake
            flattened_issues = []
            for issue in self.issues:
                flat_issue = {
                    "report_id": timestamp,
                    "table_name": issue.get("table"),
                    "check_type": issue.get("check"),
                    "severity": issue.get("severity"),
                    "message": issue.get("message"),
                    "timestamp": issue.get("timestamp")
                }
                
                # Add column if present
                if "column" in issue:
                    flat_issue["column_name"] = issue.get("column")
                    
                flattened_issues.append(flat_issue)
                
            if flattened_issues:
                # Create DataFrame
                issues_df = pd.DataFrame(flattened_issues)
                
                # Save to Snowflake
                write_pandas(
                    conn=self.conn,
                    df=issues_df,
                    table_name="DATA_QUALITY_ISSUES",
                    database="MERCURIOS_DATA",
                    schema="MONITORING"
                )
                logger.info("Saved issues to Snowflake table MERCURIOS_DATA.MONITORING.DATA_QUALITY_ISSUES")
        except Exception as e:
            logger.error(f"Error saving issues to Snowflake: {e}")
            
    def _send_notifications(self):
        """Send notifications about data quality issues."""
        notification_config = self.config.get("notification", {})
        min_severity = notification_config.get("min_severity", "high")
        
        # Filter issues by minimum severity
        severity_levels = {"high": 3, "medium": 2, "low": 1}
        min_severity_level = severity_levels.get(min_severity, 3)
        
        issues_to_notify = [
            issue for issue in self.issues
            if severity_levels.get(issue.get("severity"), 0) >= min_severity_level
        ]
        
        if not issues_to_notify:
            logger.info(f"No issues with severity >= {min_severity} to notify about")
            return
            
        # Send email notification if configured
        email = notification_config.get("email")
        if email:
            self._send_email_notification(email, issues_to_notify)
            
        # Send Slack notification if configured
        slack_webhook = notification_config.get("slack_webhook")
        if slack_webhook:
            self._send_slack_notification(slack_webhook, issues_to_notify)
            
    def _send_email_notification(self, email, issues):
        """Send email notification with data quality issues."""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['Subject'] = f"Snowflake Data Quality Alert - {len(issues)} Issues Found"
            msg['From'] = "data_quality_monitor@mercurios.ai"
            msg['To'] = email
            
            # Create HTML content
            html = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #0066cc; color: white; }}
                    .high {{ color: red; font-weight: bold; }}
                    .medium {{ color: orange; }}
                    .low {{ color: blue; }}
                </style>
            </head>
            <body>
                <h1>Snowflake Data Quality Alert</h1>
                <p>{len(issues)} issues were found during the latest data quality check.</p>
                
                <table>
                    <tr>
                        <th>Severity</th>
                        <th>Table</th>
                        <th>Check</th>
                        <th>Message</th>
                    </tr>
            """
            
            for issue in issues:
                severity = issue.get("severity", "")
                html += f"""
                    <tr>
                        <td class="{severity}">{severity}</td>
                        <td>{issue.get("table", "")}</td>
                        <td>{issue.get("check", "")}</td>
                        <td>{issue.get("message", "")}</td>
                    </tr>
                """
                
            html += """
                </table>
                
                <p>Please check the full report for more details.</p>
            </body>
            </html>
            """
            
            # Attach HTML content
            msg.attach(MIMEText(html, 'html'))
            
            # Send email
            # Note: This is a placeholder. In a real implementation, you would configure your SMTP server
            logger.info(f"Would send email notification to {email} with {len(issues)} issues")
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
            
    def _send_slack_notification(self, webhook_url, issues):
        """Send Slack notification with data quality issues."""
        try:
            # Create message
            message = {
                "text": f"Snowflake Data Quality Alert - {len(issues)} Issues Found",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "Snowflake Data Quality Alert"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{len(issues)} issues were found during the latest data quality check.*"
                        }
                    }
                ]
            }
            
            # Add issues to message
            for issue in issues:
                severity = issue.get("severity", "")
                severity_emoji = "🔴" if severity == "high" else "🟠" if severity == "medium" else "🔵"
                
                message["blocks"].append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{severity_emoji} *{severity.upper()}*: {issue.get('table', '')} - {issue.get('check', '')}\n{issue.get('message', '')}"
                    }
                })
                
            # Send to Slack
            # Note: This is a placeholder. In a real implementation, you would send the actual request
            logger.info(f"Would send Slack notification to webhook with {len(issues)} issues")
            
        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")

def main():
    """Main function to run the data quality monitor."""
    parser = argparse.ArgumentParser(description="Run data quality checks on Snowflake data")
    parser.add_argument("--config", default="snowflake_data_quality_config.json", help="Path to configuration file")
    args = parser.parse_args()
    
    monitor = SnowflakeDataQualityMonitor(args.config)
    issues = monitor.run_checks()
    
    if issues:
        logger.warning(f"Found {len(issues)} data quality issues")
        sys.exit(1)
    else:
        logger.info("No data quality issues found")
        sys.exit(0)
        
if __name__ == "__main__":
    main()
