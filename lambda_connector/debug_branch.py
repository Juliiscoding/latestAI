#!/usr/bin/env python3
"""
Debug script to test the branch endpoint directly.
"""
import os
import sys
import json
from datetime import datetime

# Add the parent directory to sys.path to import from etl package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import connector
from etl.connectors.prohandel_connector import ProHandelConnector
from etl.utils.logger import logger

def main():
    """Test the branch endpoint directly."""
    logger.info("Testing branch endpoint directly...")
    
    # Initialize connector
    connector = ProHandelConnector()
    
    # Test branch endpoint
    logger.info("Fetching branch data...")
    branch_data = connector.get_entity_list('branch')
    
    if branch_data:
        logger.info(f"✅ Branch endpoint returned {len(branch_data)} records")
        logger.info(f"First branch record: {json.dumps(branch_data[0], indent=2)}")
    else:
        logger.warning("❌ Branch endpoint returned no data")
    
    # Test shop endpoint (which should not work)
    logger.info("Fetching shop data...")
    shop_data = connector.get_entity_list('shop')
    
    if shop_data:
        logger.info(f"✅ Shop endpoint returned {len(shop_data)} records")
        logger.info(f"First shop record: {json.dumps(shop_data[0], indent=2)}")
    else:
        logger.warning("❌ Shop endpoint returned no data")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
