#!/usr/bin/env python3
"""
Debug script to test the sync operation directly.
"""
import os
import sys
import json
import traceback
from datetime import datetime

# Add the parent directory to sys.path to import from etl package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the lambda function
from lambda_function import handle_sync

# Import logging
from etl.utils.logger import logger

def main():
    """Test the sync operation directly."""
    try:
        logger.info("Testing sync operation directly...")
        
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
            return 1
        
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
            
            # Print first shop record
            if insert_data['shop']:
                logger.info(f"First shop record: {json.dumps(insert_data['shop'][0], indent=2)}")
            
            return 0
        else:
            logger.warning("❌ Sync response does not contain 'shop' data")
            
            # Check if branch is in the bookmarks (indicating it was processed)
            if 'branch' in bookmarks:
                logger.info("✅ Branch was processed (found in bookmarks)")
                
                # This might be a case where no branch data was returned from the API
                logger.info("The branch endpoint might have returned no data, which is valid")
                return 0
            else:
                logger.warning("❌ Branch was not processed (not found in bookmarks)")
                
                # Check if any data was returned at all
                if not insert_data:
                    logger.warning("No data was returned in the insert section")
                
                return 1
    except Exception as e:
        logger.error(f"Exception during sync test: {str(e)}")
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())
