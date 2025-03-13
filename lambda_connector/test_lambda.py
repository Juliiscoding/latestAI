#!/usr/bin/env python
"""
Test script for the ProHandel Lambda function.

This script allows for local testing of the Lambda function with different operations.
"""
import argparse
import json
import os
from datetime import datetime, timedelta

# Import the Lambda function
from lambda_function import lambda_handler

def load_test_event(operation, state=None):
    """
    Load a test event from a file or create one.
    
    Args:
        operation: Operation to test (test, schema, sync)
        state: Optional state to include in the event
        
    Returns:
        Test event
    """
    # Check if there's a test event file
    event_file = f"test_events/test_{operation}.json"
    
    if os.path.exists(event_file):
        with open(event_file, 'r') as f:
            event = json.load(f)
    else:
        # Create a basic event
        event = {
            "request": {
                "operation": operation
            }
        }
    
    # Add state if provided
    if state and 'request' in event:
        event['request']['state'] = state
    
    return event

def run_test(operation, state_days=None, enhancement=False):
    """
    Run a test of the Lambda function.
    
    Args:
        operation: Operation to test (test, schema, sync)
        state_days: Number of days ago for the state timestamp
        enhancement: Whether to test with data enhancement
    """
    # Create state if needed
    state = None
    if state_days is not None:
        state_date = datetime.now() - timedelta(days=state_days)
        state = {
            "last_sync": state_date.isoformat()
        }
    
    # Load test event
    if enhancement and operation == 'sync':
        event_file = "test_events/test_sync_with_enhancement.json"
        if os.path.exists(event_file):
            with open(event_file, 'r') as f:
                event = json.load(f)
        else:
            print(f"Warning: {event_file} not found, using default event")
            event = load_test_event(operation, state)
    else:
        event = load_test_event(operation, state)
    
    print(f"Running {operation} operation with event:")
    print(json.dumps(event, indent=2))
    
    # Run the Lambda function
    result = lambda_handler(event, None)
    
    # Print the result
    print("\nResult:")
    
    # For large results, limit the output
    if operation == 'sync' and 'insert' in result:
        # Count the number of records in each table
        record_counts = {}
        for table, records in result['insert'].items():
            record_counts[table] = len(records)
            
            # Show a sample record for each table
            if records:
                print(f"\nSample record from {table}:")
                print(json.dumps(records[0], indent=2))
        
        # Replace the full records with counts
        result['insert'] = record_counts
    
    # Print the final result
    print(json.dumps(result, indent=2))

def main():
    """
    Main function for the test script.
    """
    parser = argparse.ArgumentParser(description='Test the ProHandel Lambda function')
    parser.add_argument('--operation', choices=['test', 'schema', 'sync'], default='test',
                        help='Operation to test (default: test)')
    parser.add_argument('--state-days', type=int, default=None,
                        help='Number of days ago for the state timestamp (default: None)')
    parser.add_argument('--enhancement', action='store_true',
                        help='Test with data enhancement (only for sync operation)')
    
    args = parser.parse_args()
    
    run_test(args.operation, args.state_days, args.enhancement)

if __name__ == "__main__":
    main()
