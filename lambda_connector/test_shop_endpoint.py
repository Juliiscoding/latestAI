#!/usr/bin/env python3
"""
Test script specifically for the ProHandel shop endpoint.
This script tests the shop endpoint with various parameters to determine
why it's not returning data.
"""

import os
import sys
import json
import logging
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl.connectors.prohandel_connector import ProHandelConnector
from etl.utils.logger import logger

# Configure logging for this script
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
script_logger = logging.getLogger("shop_endpoint_test")
script_logger.setLevel(logging.INFO)

def test_shop_endpoint():
    """Test the shop endpoint with various parameters."""
    # Load environment variables
    load_dotenv()
    
    # Initialize connector
    connector = ProHandelConnector()
    
    # Test 1: Basic request
    script_logger.info("Test 1: Basic shop endpoint request")
    try:
        shops = connector.get_entity_list('shop')
        script_logger.info(f"Number of shops: {len(shops)}")
        script_logger.info(f"Shop data: {json.dumps(shops, indent=2)}")
    except Exception as e:
        script_logger.error(f"Error in basic request: {str(e)}")
    
    # Test 2: With active parameter
    script_logger.info("Test 2: Shop endpoint with active=True parameter")
    try:
        shops_active = connector.get_entity_list('shop', params={'active': True})
        script_logger.info(f"Number of active shops: {len(shops_active)}")
        script_logger.info(f"Active shop data: {json.dumps(shops_active, indent=2)}")
    except Exception as e:
        script_logger.error(f"Error in active request: {str(e)}")
    
    # Test 3: With different page size
    script_logger.info("Test 3: Shop endpoint with larger page size")
    try:
        shops_paged = connector.get_entity_list('shop', pagesize=100)
        script_logger.info(f"Number of shops with larger page size: {len(shops_paged)}")
        script_logger.info(f"Paged shop data: {json.dumps(shops_paged, indent=2)}")
    except Exception as e:
        script_logger.error(f"Error in paged request: {str(e)}")
    
    # Test 4: Direct API request to see raw response
    script_logger.info("Test 4: Direct API request to shop endpoint")
    try:
        # Make direct request to see full response
        response = connector._make_request('/shop')
        script_logger.info(f"Raw API response: {json.dumps(response, indent=2)}")
    except Exception as e:
        script_logger.error(f"Error in direct request: {str(e)}")
    
    # Test 5: Check if endpoint name is different
    script_logger.info("Test 5: Testing alternative endpoint names")
    alternative_names = ['shops', 'store', 'stores', 'branch', 'branches']
    for name in alternative_names:
        try:
            script_logger.info(f"Testing endpoint name: {name}")
            alt_shops = connector.get_entity_list(name)
            script_logger.info(f"Number of results for '{name}': {len(alt_shops)}")
            if len(alt_shops) > 0:
                script_logger.info(f"Data for '{name}': {json.dumps(alt_shops, indent=2)}")
        except Exception as e:
            script_logger.error(f"Error with endpoint '{name}': {str(e)}")
    
    script_logger.info("Shop endpoint testing completed")

if __name__ == "__main__":
    test_shop_endpoint()
