#!/usr/bin/env python
"""
Test script to demonstrate the data extraction capabilities of the ETL pipeline.
This script extracts data from the ProHandel API and prints it to the console,
without requiring a running PostgreSQL instance.
"""
import os
import sys
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the connector
from etl.connectors.prohandel_connector import prohandel_connector
from etl.utils.logger import logger

def test_extraction(entity_name, limit=5):
    """
    Test the extraction of data from the ProHandel API.
    
    Args:
        entity_name: Name of the entity to extract
        limit: Maximum number of records to extract
    """
    logger.info(f"Testing extraction for entity: {entity_name}")
    
    try:
        # Extract a single batch of data
        data_batch = prohandel_connector.get_entity_list(entity_name, page=1, pagesize=limit)
        
        if not data_batch:
            logger.warning(f"No data found for entity: {entity_name}")
            return
        
        # Print the data
        logger.info(f"Extracted {len(data_batch)} records for entity: {entity_name}")
        logger.info(f"Sample data: {json.dumps(data_batch[0], indent=2, default=str)}")
        
        return data_batch
    except Exception as e:
        logger.error(f"Error extracting data for entity: {entity_name}: {e}")
        return None

def main():
    """Main function."""
    # List of entities to test
    entities = ["article", "customer", "order", "sale", "inventory"]
    
    logger.info("Starting extraction test")
    
    results = {}
    
    # Test extraction for each entity
    for entity_name in entities:
        data = test_extraction(entity_name)
        results[entity_name] = len(data) if data else 0
    
    # Print summary
    logger.info("Extraction test complete")
    logger.info(f"Results: {json.dumps(results, indent=2)}")

if __name__ == "__main__":
    main()
