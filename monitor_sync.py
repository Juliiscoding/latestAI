#!/usr/bin/env python3
"""
Monitor Fivetran Sync and Data Quality

This script helps monitor the Fivetran sync process and run data quality checks
on the synced data.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, text

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Monitor Fivetran sync and data quality')
    parser.add_argument('--config', type=str, default='data_quality_config.json',
                        help='Path to data quality config file')
    parser.add_argument('--output', type=str, default='sync_monitor_report.md',
                        help='Path to output report file')
    parser.add_argument('--check-interval', type=int, default=300,
                        help='Interval in seconds between checks')
    parser.add_argument('--max-duration', type=int, default=3600,
                        help='Maximum duration in seconds to monitor')
    parser.add_argument('--lambda-name', type=str, default='prohandel-connector',
                        help='Name of the Lambda function')
    parser.add_argument('--region', type=str, default='eu-central-1',
                        help='AWS region')
    return parser.parse_args()

def check_lambda_logs(lambda_name, region, start_time):
    """Check Lambda logs for errors."""
    try:
        cmd = [
            'aws', 'logs', 'filter-log-events',
            '--log-group-name', f'/aws/lambda/{lambda_name}',
            '--start-time', str(int(start_time.timestamp() * 1000)),
            '--filter-pattern', 'ERROR'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error checking Lambda logs: {e}")
        return None

def check_table_counts(engine, config):
    """Check record counts for all tables."""
    results = {}
    for table in config.get('tables', []):
        table_name = table.get('name')
        try:
            query = text(f"SELECT COUNT(*) as count FROM {table_name}")
            result = engine.execute(query).fetchone()
            count = result[0] if result else 0
            results[table_name] = {
                'count': count,
                'min_count': table.get('min_count', 0),
                'status': 'OK' if count >= table.get('min_count', 0) else 'ERROR'
            }
        except Exception as e:
            results[table_name] = {
                'count': 0,
                'min_count': table.get('min_count', 0),
                'status': f'ERROR: {str(e)}'
            }
    return results

def check_data_freshness(engine, config):
    """Check data freshness for tables with timestamp columns."""
    results = {}
    for table in config.get('tables', []):
        table_name = table.get('name')
        timestamp_column = table.get('timestamp_column')
        if not timestamp_column:
            continue
        
        try:
            query = text(f"SELECT MAX({timestamp_column}) as latest FROM {table_name}")
            result = engine.execute(query).fetchone()
            latest = result[0] if result else None
            
            if latest:
                now = datetime.now()
                age_hours = (now - latest.replace(tzinfo=None)).total_seconds() / 3600
                max_age = table.get('max_age_hours', 24)
                
                results[table_name] = {
                    'latest': latest,
                    'age_hours': age_hours,
                    'max_age_hours': max_age,
                    'status': 'OK' if age_hours <= max_age else 'ERROR'
                }
            else:
                results[table_name] = {
                    'latest': None,
                    'status': 'ERROR: No timestamp data'
                }
        except Exception as e:
            results[table_name] = {
                'latest': None,
                'status': f'ERROR: {str(e)}'
            }
    return results

def create_database_engine(config):
    """Create SQLAlchemy engine from config."""
    db_config = config.get('database', {})
    connection_string = (
        f"postgresql://{db_config.get('user')}:{db_config.get('password')}@"
        f"{db_config.get('host')}:{db_config.get('port')}/{db_config.get('dbname')}"
    )
    return create_engine(connection_string)

def generate_report(table_counts, freshness_results, lambda_logs, output_file):
    """Generate a Markdown report with the results."""
    with open(output_file, 'w') as f:
        f.write(f"# Fivetran Sync Monitoring Report\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Table Record Counts\n\n")
        f.write("| Table | Count | Min Required | Status |\n")
        f.write("|-------|-------|-------------|--------|\n")
        for table, data in table_counts.items():
            f.write(f"| {table} | {data['count']} | {data['min_count']} | {data['status']} |\n")
        
        f.write("\n## Data Freshness\n\n")
        f.write("| Table | Latest Timestamp | Age (hours) | Max Age | Status |\n")
        f.write("|-------|-----------------|-------------|---------|--------|\n")
        for table, data in freshness_results.items():
            latest = data.get('latest', 'N/A')
            if isinstance(latest, datetime):
                latest = latest.strftime('%Y-%m-%d %H:%M:%S')
            age = data.get('age_hours', 'N/A')
            if isinstance(age, (int, float)):
                age = f"{age:.2f}"
            f.write(f"| {table} | {latest} | {age} | {data.get('max_age_hours', 'N/A')} | {data['status']} |\n")
        
        if lambda_logs:
            f.write("\n## Lambda Function Errors\n\n")
            f.write("```\n")
            f.write(lambda_logs)
            f.write("\n```\n")
        else:
            f.write("\n## Lambda Function Errors\n\n")
            f.write("No errors found in Lambda logs.\n")
        
        f.write("\n## Next Steps\n\n")
        f.write("1. Address any errors or warnings in the report\n")
        f.write("2. Run full data quality checks with `python data_quality_monitor.py`\n")
        f.write("3. Run dbt models to transform the data\n")
        f.write("4. Create dashboards based on the transformed data\n")

def main():
    """Main function."""
    args = parse_args()
    
    try:
        with open(args.config, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading config file: {e}")
        sys.exit(1)
    
    print(f"Starting sync monitoring for {args.max_duration} seconds...")
    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=args.max_duration)
    
    while datetime.now() < end_time:
        current_time = datetime.now()
        print(f"\nCheck at {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            engine = create_database_engine(config)
            table_counts = check_table_counts(engine, config)
            freshness_results = check_data_freshness(engine, config)
            lambda_logs = check_lambda_logs(args.lambda_name, args.region, start_time)
            
            # Print summary
            print("\nTable Counts:")
            for table, data in table_counts.items():
                print(f"  {table}: {data['count']} records ({data['status']})")
            
            print("\nData Freshness:")
            for table, data in freshness_results.items():
                if 'age_hours' in data:
                    print(f"  {table}: {data.get('age_hours', 'N/A'):.2f} hours old ({data['status']})")
            
            # Generate report
            generate_report(table_counts, freshness_results, lambda_logs, args.output)
            print(f"\nReport generated: {args.output}")
            
            # Check if all tables have data
            all_tables_have_data = all(data['status'] == 'OK' for data in table_counts.values())
            all_data_fresh = all(data['status'] == 'OK' for data in freshness_results.values() if 'age_hours' in data)
            
            if all_tables_have_data and all_data_fresh:
                print("\nAll tables have data and are up to date!")
                print("You can now proceed with running data quality checks and dbt models.")
                break
            
        except Exception as e:
            print(f"Error during monitoring: {e}")
        
        # Wait for next check
        print(f"\nWaiting {args.check_interval} seconds until next check...")
        time.sleep(args.check_interval)
    
    print("\nMonitoring complete.")

if __name__ == "__main__":
    main()
