#!/usr/bin/env python3
"""
Script to check AWS CloudWatch logs for the ProHandel Lambda function
"""

import boto3
import os
import json
import datetime
from dotenv import load_dotenv
from tabulate import tabulate

# Load environment variables
load_dotenv()

# AWS credentials and region
aws_region = os.getenv('AWS_REGION', 'eu-central-1')
lambda_function_name = os.getenv('LAMBDA_FUNCTION_NAME', 'prohandel-fivetran-connector')

def get_cloudwatch_logs(minutes=30):
    """Get CloudWatch logs for the Lambda function for the last N hours"""
    try:
        # Create CloudWatch Logs client
        logs_client = boto3.client('logs', region_name=aws_region)
        
        # Get the log group name for the Lambda function
        log_group_name = f"/aws/lambda/{lambda_function_name}"
        
        # Calculate the start time (N minutes ago)
        start_time = int((datetime.datetime.now() - datetime.timedelta(minutes=minutes)).timestamp() * 1000)
        end_time = int(datetime.datetime.now().timestamp() * 1000)
        
        print(f"Fetching logs for {lambda_function_name} from the last {minutes} minute(s)...")
        
        # Get log streams
        response = logs_client.describe_log_streams(
            logGroupName=log_group_name,
            orderBy='LastEventTime',
            descending=True,
            limit=5  # Get the 5 most recent log streams
        )
        
        log_streams = response.get('logStreams', [])
        if not log_streams:
            print(f"No log streams found for {log_group_name}")
            return []
        
        all_events = []
        
        # Get log events from each stream
        for stream in log_streams:
            stream_name = stream['logStreamName']
            
            response = logs_client.get_log_events(
                logGroupName=log_group_name,
                logStreamName=stream_name,
                startTime=start_time,
                endTime=end_time,
                limit=100  # Limit to 100 log events per stream
            )
            
            events = response.get('events', [])
            for event in events:
                timestamp = datetime.datetime.fromtimestamp(event['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                message = event['message']
                all_events.append({
                    'timestamp': timestamp,
                    'stream': stream_name,
                    'message': message
                })
        
        # Sort events by timestamp
        all_events.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return all_events
    
    except Exception as e:
        print(f"Error getting CloudWatch logs: {str(e)}")
        return []

def analyze_logs(events):
    """Analyze log events for errors and important information"""
    if not events:
        print("No log events found")
        return
    
    print(f"\nFound {len(events)} log events")
    
    # Extract errors and warnings
    errors = []
    warnings = []
    sync_events = []
    
    for event in events:
        message = event['message'].lower()
        
        if 'error' in message or 'exception' in message or 'fail' in message:
            errors.append(event)
        elif 'warning' in message or 'warn' in message:
            warnings.append(event)
        
        if 'sync' in message:
            sync_events.append(event)
    
    # Print errors
    if errors:
        print(f"\n=== Found {len(errors)} errors ===")
        for i, error in enumerate(errors[:10], 1):  # Show first 10 errors
            print(f"\n{i}. Error at {error['timestamp']}:")
            print(f"   {error['message']}")  # Show full error message
        
        if len(errors) > 10:
            print(f"\n... and {len(errors) - 10} more errors")
    else:
        print("\n=== No errors found ===")
    
    # Print warnings
    if warnings:
        print(f"\n=== Found {len(warnings)} warnings ===")
        for i, warning in enumerate(warnings[:5], 1):  # Show first 5 warnings
            print(f"\n{i}. Warning at {warning['timestamp']}:")
            print(f"   {warning['message']}")  # Show full warning message
        
        if len(warnings) > 5:
            print(f"\n... and {len(warnings) - 5} more warnings")
    else:
        print("\n=== No warnings found ===")
    
    # Print sync events
    if sync_events:
        print(f"\n=== Found {len(sync_events)} sync-related events ===")
        for i, event in enumerate(sync_events[:10], 1):  # Show first 10 sync events
            print(f"\n{i}. Sync event at {event['timestamp']}:")
            print(f"   {event['message']}")  # Show full sync event message
        
        if len(sync_events) > 10:
            print(f"\n... and {len(sync_events) - 10} more sync events")
    else:
        print("\n=== No sync-related events found ===")

def main():
    """Main function"""
    print("=== Checking AWS CloudWatch Logs for ProHandel Lambda Function ===")
    
    # Get logs from the last 15 minutes by default
    minutes = 15
    
    # Check if minutes argument was provided
    import sys
    if len(sys.argv) > 1:
        try:
            minutes = int(sys.argv[1])
        except ValueError:
            print(f"Invalid minutes value: {sys.argv[1]}. Using default of {minutes} minutes.")
    
    print(f"Checking logs from the last {minutes} minutes...")
    events = get_cloudwatch_logs(minutes=minutes)
    
    # Analyze logs
    analyze_logs(events)

if __name__ == "__main__":
    main()
