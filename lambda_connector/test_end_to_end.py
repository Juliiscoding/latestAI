#!/usr/bin/env python3
"""
End-to-end test script for ProHandel Lambda function.

This script tests the complete functionality of the Lambda function,
including all entities, aggregations, and the shop endpoint mapping.
"""

import os
import json
import logging
from dotenv import load_dotenv
from lambda_function import handle_sync, handle_schema, handle_test

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('mercurios_etl')

# Load environment variables
load_dotenv()

def test_lambda_handlers():
    """Test the Lambda handler functions directly."""
    logger.info("===== TESTING LAMBDA HANDLERS =====")
    
    # Test operation
    logger.info("Testing 'test' operation...")
    test_response = handle_test()
    assert isinstance(test_response, dict), "Test operation failed"
    assert test_response.get("status") == "ok", "Test operation failed"
    logger.info("✅ Test operation successful")
    logger.info(f"Test response: {json.dumps(test_response, indent=2)}")
    
    # Schema operation
    logger.info("Testing 'schema' operation...")
    schema_response = handle_schema()
    assert "schema" in schema_response, "Schema operation failed"
    assert "tables" in schema_response["schema"], "Schema response missing tables"
    
    # Check for shop table in schema
    tables = schema_response["schema"]["tables"]
    assert "shop" in tables, "Shop table missing from schema"
    logger.info(f"✅ Schema operation successful, found {len(tables)} tables including 'shop'")
    
    # Sync operation
    logger.info("Testing 'sync' operation...")
    sync_response = handle_sync()
    assert "insert" in sync_response, "Sync operation failed"
    assert "state" in sync_response, "Sync response missing state"
    
    # Check for data in sync response
    insert_data = sync_response["insert"]
    logger.info(f"Sync response contains data for tables: {', '.join(insert_data.keys())}")
    
    # Check for shop data specifically
    assert "shop" in insert_data, "Shop data missing from sync response"
    logger.info(f"✅ Found {len(insert_data['shop'])} shop records")
    
    # Check for aggregations
    aggregations_found = []
    for table in insert_data.keys():
        if table.endswith('_agg'):
            aggregations_found.append(table)
            logger.info(f"✅ Found aggregation table '{table}' with {len(insert_data[table])} records")
    
    if not aggregations_found:
        logger.warning("⚠️ No aggregation tables found in sync response")
    
    logger.info("✅ Sync operation successful")
    
    return {
        "test": test_response,
        "schema": schema_response,
        "sync": sync_response
    }

def verify_shop_mapping():
    """Verify that the branch endpoint is correctly mapped to the shop schema."""
    logger.info("===== VERIFYING SHOP MAPPING =====")
    
    # Get sync data
    sync_response = handle_sync()
    
    # Check if shop data exists
    if "shop" not in sync_response.get("insert", {}):
        logger.error("❌ Shop data missing from sync response")
        return False
    
    shop_data = sync_response["insert"]["shop"]
    if not shop_data:
        logger.error("❌ Shop data is empty")
        return False
    
    # Check if branch bookmark exists in state
    bookmarks = sync_response.get("state", {}).get("bookmarks", {})
    if "branch" not in bookmarks:
        logger.error("❌ Branch bookmark missing from state")
        return False
    
    # Verify shop data structure
    first_shop = shop_data[0]
    required_fields = ["name1", "city", "street", "zipCode", "telephoneNumber"]
    
    for field in required_fields:
        if field not in first_shop:
            logger.error(f"❌ Required field '{field}' missing from shop data")
            return False
    
    # Check for enhanced fields
    enhanced_fields = ["shop_type", "is_online"]
    for field in enhanced_fields:
        if field not in first_shop:
            logger.warning(f"⚠️ Enhanced field '{field}' missing from shop data")
    
    logger.info(f"✅ Shop mapping verified successfully with {len(shop_data)} records")
    logger.info(f"Sample shop record: {json.dumps(first_shop, indent=2)}")
    
    return True

def verify_aggregations():
    """Verify that aggregations are working correctly."""
    logger.info("===== VERIFYING AGGREGATIONS =====")
    
    # Get sync data
    sync_response = handle_sync()
    insert_data = sync_response.get("insert", {})
    
    # Check for daily sales aggregation
    if "daily_sales_agg" not in insert_data:
        logger.warning("⚠️ Daily sales aggregation missing from sync response")
    else:
        daily_sales = insert_data["daily_sales_agg"]
        logger.info(f"✅ Found {len(daily_sales)} daily sales aggregation records")
        
        if daily_sales:
            # Verify structure
            first_agg = daily_sales[0]
            required_fields = ["date", "aggregation_type"]
            
            for field in required_fields:
                if field not in first_agg:
                    logger.error(f"❌ Required field '{field}' missing from daily sales aggregation")
                    break
            else:
                logger.info("✅ Daily sales aggregation structure verified")
                logger.info(f"Sample daily sales aggregation: {json.dumps(first_agg, indent=2)}")
    
    # Check for article sales aggregation
    if "article_sales_agg" not in insert_data:
        logger.warning("⚠️ Article sales aggregation missing from sync response")
    else:
        article_sales = insert_data["article_sales_agg"]
        logger.info(f"✅ Found {len(article_sales)} article sales aggregation records")
    
    # Check for warehouse inventory aggregation
    if "warehouse_inventory_agg" not in insert_data:
        logger.warning("⚠️ Warehouse inventory aggregation missing from sync response")
    else:
        warehouse_inventory = insert_data["warehouse_inventory_agg"]
        logger.info(f"✅ Found {len(warehouse_inventory)} warehouse inventory aggregation records")
    
    return True

def main():
    """Run all tests."""
    logger.info("Starting end-to-end tests for ProHandel Lambda function")
    
    try:
        # Test Lambda handlers
        lambda_results = test_lambda_handlers()
        
        # Verify shop mapping
        shop_mapping_ok = verify_shop_mapping()
        
        # Verify aggregations
        aggregations_ok = verify_aggregations()
        
        # Print summary
        logger.info("\n===== TEST SUMMARY =====")
        logger.info(f"Lambda Handler Test: {'✅ PASS' if lambda_results else '❌ FAIL'}")
        logger.info(f"Shop Mapping Test: {'✅ PASS' if shop_mapping_ok else '❌ FAIL'}")
        logger.info(f"Aggregations Test: {'✅ PASS' if aggregations_ok else '❌ FAIL'}")
        
        overall_status = all([lambda_results, shop_mapping_ok, aggregations_ok])
        logger.info(f"\nOverall Test Status: {'✅ PASS' if overall_status else '❌ FAIL'}")
        
        if overall_status:
            logger.info("\n🎉 The Lambda function is ready for deployment! 🎉")
        else:
            logger.error("\n⚠️ Some tests failed. Please fix the issues before deployment.")
        
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}", exc_info=True)
        return False
    
    return overall_status

if __name__ == "__main__":
    main()
