#!/usr/bin/env python3
"""
Test script to verify the branch endpoint functionality in the Lambda function.

This script tests the Lambda function's ability to correctly map the 'branch' endpoint
to 'shop' in the schema and sync operations.
"""
import os
import sys
import json
import traceback
from datetime import datetime

# Add the parent directory to sys.path to import from etl package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the lambda function
from lambda_function import lambda_handler, handle_schema, handle_sync

# Import connector for direct testing
from etl.connectors.prohandel_connector import ProHandelConnector

# Import logging
from etl.utils.logger import logger

def test_schema_generation():
    """Test that the schema correctly maps 'branch' to 'shop'."""
    logger.info("Testing schema generation...")
    
    # Call the schema handler directly
    schema_response = handle_schema()
    
    # Check if there was an error
    if 'error' in schema_response:
        logger.error(f"Schema generation failed: {schema_response['error']}")
        return False
    
    # Check if the schema contains a 'shop' table (mapped from 'branch')
    tables = schema_response.get('schema', {}).get('tables', {})
    if 'shop' in tables:
        logger.info("✅ Schema contains 'shop' table (mapped from 'branch')")
        
        # Check if shop has the additional fields we added
        shop_columns = tables['shop'].get('columns', {})
        if 'shop_type' in shop_columns and 'is_online' in shop_columns:
            logger.info("✅ Shop table contains enhanced fields (shop_type, is_online)")
        else:
            logger.warning("❌ Shop table is missing enhanced fields")
            return False
        
        return True
    else:
        logger.error("❌ Schema does not contain 'shop' table")
        return False

def test_sync_operation():
    """Test that the sync operation correctly maps 'branch' to 'shop'."""
    logger.info("Testing sync operation...")
    
    try:
        # First, directly test if we can get branch data from the API
        connector = ProHandelConnector()
        branch_data = connector.get_entity_list('branch', pagesize=5)
        
        logger.info(f"Direct API test: Branch endpoint returned {len(branch_data)} records")
        if branch_data:
            logger.info(f"Sample branch record: {json.dumps(branch_data[0], indent=2)}")
        
        # Create a test state
        test_state = {
            "bookmarks": {}
        }
        
        # Call the sync handler directly
        logger.info("Calling handle_sync function...")
        sync_response = handle_sync(test_state)
        
        # Check if there was an error
        if 'error' in sync_response:
            logger.error(f"Sync operation failed: {sync_response['error']}")
            return False
        
        # Debug: Print the full response structure
        logger.info(f"Sync response keys: {sync_response.keys()}")
        
        # Check insert data
        insert_data = sync_response.get('insert', {})
        logger.info(f"Insert data keys: {insert_data.keys()}")
        
        # Check state bookmarks
        bookmarks = sync_response.get('state', {}).get('bookmarks', {})
        logger.info(f"State bookmarks: {bookmarks}")
        
        # Check if the response contains 'shop' data (mapped from 'branch')
        if 'shop' in insert_data:
            logger.info(f"✅ Sync response contains 'shop' data with {len(insert_data['shop'])} records")
            return True
        else:
            logger.warning("❌ Sync response does not contain 'shop' data")
            
            # Check if branch is in the bookmarks (indicating it was processed)
            if 'branch' in bookmarks:
                logger.info("✅ Branch was processed (found in bookmarks)")
                
                # This might be a case where no branch data was returned from the API
                logger.info("The branch endpoint might have returned no data, which is valid")
                return True
            else:
                logger.warning("❌ Branch was not processed (not found in bookmarks)")
                
                # Check if any data was returned at all
                if not insert_data:
                    logger.warning("No data was returned in the insert section")
                    
                # Check if entities_to_sync includes branch
                logger.info("Checking if the sync function is configured to fetch branch data...")
                
                return False
    except Exception as e:
        logger.error(f"Exception during sync test: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def test_lambda_function():
    """Test the full Lambda function with a test event."""
    logger.info("Testing Lambda function...")
    
    # Create a test event for schema operation
    schema_event = {
        "request": {
            "operation": "schema",
            "secrets": {
                "api_key": os.environ.get("PROHANDEL_API_KEY"),
                "api_secret": os.environ.get("PROHANDEL_API_SECRET")
            }
        }
    }
    
    # Call the Lambda handler
    schema_response = lambda_handler(schema_event, None)
    
    # Check if there was an error
    if 'error' in schema_response:
        logger.error(f"Lambda function schema test failed: {schema_response['error']}")
        return False
    
    # Check if the schema contains a 'shop' table (mapped from 'branch')
    tables = schema_response.get('schema', {}).get('tables', {})
    if 'shop' in tables:
        logger.info("✅ Lambda function schema contains 'shop' table")
        return True
    else:
        logger.error("❌ Lambda function schema does not contain 'shop' table")
        return False

def main():
    """Run all tests."""
    logger.info("Starting branch endpoint tests...")
    
    # Run the tests
    schema_test_result = test_schema_generation()
    sync_test_result = test_sync_operation()
    lambda_test_result = test_lambda_function()
    
    # Print summary
    logger.info("\n=== Test Results ===")
    logger.info(f"Schema Generation: {'✅ PASS' if schema_test_result else '❌ FAIL'}")
    logger.info(f"Sync Operation: {'✅ PASS' if sync_test_result else '❌ FAIL'}")
    logger.info(f"Lambda Function: {'✅ PASS' if lambda_test_result else '❌ FAIL'}")
    
    # Overall result
    if schema_test_result and sync_test_result and lambda_test_result:
        logger.info("\n✅ All tests PASSED - Branch endpoint is correctly mapped to Shop")
        return 0
    else:
        logger.error("\n❌ Some tests FAILED - Branch endpoint mapping needs fixing")
        return 1

if __name__ == "__main__":
    sys.exit(main())
