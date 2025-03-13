#!/usr/bin/env python
"""
Test script to validate the Lambda function with Fivetran requests.
This script simulates Fivetran requests to the Lambda function and validates the responses.
"""

import os
import sys
import json
import logging
import argparse
import boto3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from tabulate import tabulate

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"lambda_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger(__name__)

# Entity configuration
ENTITY_CONFIG = {
    "article": {
        "endpoint": "/articles",
        "state_field": "updated_at"
    },
    "customer": {
        "endpoint": "/customers",
        "state_field": "updated_at"
    },
    "order": {
        "endpoint": "/orders",
        "state_field": "updated_at"
    },
    "orderposition": {
        "endpoint": "/order-positions",
        "state_field": "updated_at"
    },
    "inventory": {
        "endpoint": "/inventory",
        "state_field": "updated_at"
    },
    "customercard": {
        "endpoint": "/customer-cards",
        "state_field": "updated_at"
    },
    "supplier": {
        "endpoint": "/suppliers",
        "state_field": "updated_at"
    },
    "branch": {
        "endpoint": "/branches",
        "state_field": "updated_at"
    },
    "category": {
        "endpoint": "/categories",
        "state_field": "updated_at"
    },
    "voucher": {
        "endpoint": "/vouchers",
        "state_field": "updated_at"
    },
    "invoice": {
        "endpoint": "/invoices",
        "state_field": "updated_at"
    },
    "payment": {
        "endpoint": "/payments",
        "state_field": "updated_at"
    }
}

def create_test_request(operation: str, entity: Optional[str] = None, 
                       state: Optional[Dict[str, Any]] = None,
                       limit: int = 10) -> Dict[str, Any]:
    """
    Create a test request for the Lambda function.
    
    Args:
        operation: Fivetran operation (test, schema, sync)
        entity: Entity to sync (only for sync operation)
        state: State to use for incremental sync
        limit: Maximum number of records to fetch
        
    Returns:
        Dictionary with the request payload
    """
    request = {
        "agent": "fivetran",
        "version": 2,
        "secrets": {
            "api_key": os.environ.get("PROHANDEL_API_KEY", ""),
            "api_secret": os.environ.get("PROHANDEL_API_SECRET", ""),
            "api_url": os.environ.get("PROHANDEL_API_URL", "https://api.prohandel.cloud/api/v4"),
            "auth_url": os.environ.get("PROHANDEL_AUTH_URL", "https://auth.prohandel.cloud/api/v4")
        },
        "operation": operation
    }
    
    if operation == "sync" and entity:
        request["table"] = entity
        request["limit"] = limit
        
        if state:
            request["state"] = state
    
    return request

def invoke_lambda(function_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Invoke the Lambda function with the given payload.
    
    Args:
        function_name: Name of the Lambda function
        payload: Request payload
        
    Returns:
        Response from the Lambda function
    """
    lambda_client = boto3.client('lambda')
    
    try:
        logger.info(f"Invoking Lambda function: {function_name}")
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        payload = response['Payload'].read().decode('utf-8')
        return json.loads(payload)
    except Exception as e:
        logger.error(f"Error invoking Lambda function: {str(e)}", exc_info=True)
        return {"error": str(e)}

def validate_test_response(response: Dict[str, Any]) -> bool:
    """
    Validate the response from a test operation.
    
    Args:
        response: Response from the Lambda function
        
    Returns:
        True if the response is valid, False otherwise
    """
    if "error" in response:
        logger.error(f"Test operation failed: {response['error']}")
        return False
    
    if response.get("hasMore") is not True and response.get("hasMore") is not False:
        logger.error("Test operation response missing 'hasMore' field")
        return False
    
    return True

def validate_schema_response(response: Dict[str, Any]) -> bool:
    """
    Validate the response from a schema operation.
    
    Args:
        response: Response from the Lambda function
        
    Returns:
        True if the response is valid, False otherwise
    """
    if "error" in response:
        logger.error(f"Schema operation failed: {response['error']}")
        return False
    
    if "schema" not in response:
        logger.error("Schema operation response missing 'schema' field")
        return False
    
    schema = response.get("schema", {})
    
    if not schema or not isinstance(schema, dict):
        logger.error("Schema operation returned empty or invalid schema")
        return False
    
    # Check if all entities are in the schema
    for entity in ENTITY_CONFIG.keys():
        if entity not in schema:
            logger.warning(f"Entity '{entity}' missing from schema response")
    
    return True

def validate_sync_response(response: Dict[str, Any], entity: str) -> bool:
    """
    Validate the response from a sync operation.
    
    Args:
        response: Response from the Lambda function
        entity: Entity being synced
        
    Returns:
        True if the response is valid, False otherwise
    """
    if "error" in response:
        logger.error(f"Sync operation for {entity} failed: {response['error']}")
        return False
    
    if "hasMore" not in response:
        logger.error(f"Sync operation for {entity} missing 'hasMore' field")
        return False
    
    if "state" not in response:
        logger.warning(f"Sync operation for {entity} missing 'state' field")
    
    if "insert" not in response:
        logger.error(f"Sync operation for {entity} missing 'insert' field")
        return False
    
    inserts = response.get("insert", {}).get(entity, [])
    
    if not isinstance(inserts, list):
        logger.error(f"Sync operation for {entity} returned invalid 'insert' field")
        return False
    
    return True

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Test Lambda function with Fivetran requests')
    parser.add_argument('--function-name', type=str, default="prohandel-fivetran-connector",
                        help='Name of the Lambda function')
    parser.add_argument('--region', type=str, default="eu-central-1",
                        help='AWS region')
    parser.add_argument('--entity', type=str, help='Specific entity to test (default: all)')
    parser.add_argument('--limit', type=int, default=10,
                        help='Maximum number of records to fetch per entity')
    parser.add_argument('--output', type=str, default=f"lambda_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        help='Output file for test results')
    return parser.parse_args()

def main():
    """Main function to run Lambda tests."""
    args = parse_args()
    
    # Set AWS region
    os.environ['AWS_DEFAULT_REGION'] = args.region
    
    # Check if API credentials are provided
    if not os.environ.get("PROHANDEL_API_KEY") or not os.environ.get("PROHANDEL_API_SECRET"):
        logger.error("API key and secret are required. Set them as environment variables.")
        sys.exit(1)
    
    results = []
    summary_rows = []
    
    # Test the 'test' operation
    logger.info("Testing 'test' operation")
    test_request = create_test_request(operation="test")
    test_response = invoke_lambda(args.function_name, test_request)
    test_success = validate_test_response(test_response)
    
    results.append({
        "operation": "test",
        "request": test_request,
        "response": test_response,
        "success": test_success
    })
    
    summary_rows.append([
        "test",
        "N/A",
        "✅ PASS" if test_success else "❌ FAIL"
    ])
    
    # Test the 'schema' operation
    logger.info("Testing 'schema' operation")
    schema_request = create_test_request(operation="schema")
    schema_response = invoke_lambda(args.function_name, schema_request)
    schema_success = validate_schema_response(schema_response)
    
    results.append({
        "operation": "schema",
        "request": schema_request,
        "response": schema_response,
        "success": schema_success
    })
    
    summary_rows.append([
        "schema",
        "N/A",
        "✅ PASS" if schema_success else "❌ FAIL"
    ])
    
    # Determine which entities to test
    entities_to_test = [args.entity] if args.entity else ENTITY_CONFIG.keys()
    
    # Test the 'sync' operation for each entity
    for entity in entities_to_test:
        if entity not in ENTITY_CONFIG:
            logger.warning(f"Unknown entity: {entity}. Skipping.")
            continue
        
        logger.info(f"Testing 'sync' operation for entity: {entity}")
        
        # Create a state with a timestamp from yesterday
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        state = {
            ENTITY_CONFIG[entity]["state_field"]: yesterday
        }
        
        sync_request = create_test_request(
            operation="sync",
            entity=entity,
            state=state,
            limit=args.limit
        )
        
        sync_response = invoke_lambda(args.function_name, sync_request)
        sync_success = validate_sync_response(sync_response, entity)
        
        results.append({
            "operation": "sync",
            "entity": entity,
            "request": sync_request,
            "response": sync_response,
            "success": sync_success
        })
        
        # Add record count to summary
        record_count = 0
        if "insert" in sync_response and entity in sync_response["insert"]:
            record_count = len(sync_response["insert"][entity])
        
        summary_rows.append([
            "sync",
            entity,
            "✅ PASS" if sync_success else "❌ FAIL",
            record_count
        ])
    
    # Save detailed results to file
    with open(args.output, 'w') as f:
        # Remove secrets from the results before saving
        for result in results:
            if "request" in result and "secrets" in result["request"]:
                result["request"]["secrets"] = {"redacted": "for security"}
        
        json.dump(results, f, indent=2)
    
    logger.info(f"Detailed test results saved to {args.output}")
    
    # Print summary table
    print("\n" + "=" * 80)
    print("LAMBDA FUNCTION TEST SUMMARY")
    print("=" * 80)
    print(tabulate(
        summary_rows,
        headers=["Operation", "Entity", "Status", "Records"],
        tablefmt="grid"
    ))
    print("=" * 80)
    
    # Print overall status
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r.get("success", False))
    
    print(f"\nOverall Status: {successful_tests}/{total_tests} tests passed")
    
    if successful_tests < total_tests:
        print("\nFailed tests:")
        for result in results:
            if not result.get("success", False):
                entity = result.get("entity", "N/A")
                operation = result.get("operation", "unknown")
                print(f"  - {operation} operation for {entity} failed")
    
    print(f"\nFor detailed results, check: {args.output}")

if __name__ == "__main__":
    main()
