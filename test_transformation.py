#!/usr/bin/env python
"""
Test script for the ETL transformation layer.
This script tests the transformation capabilities of the ETL pipeline.
"""
import os
import sys
import json
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from etl.transformers.base_transformer import BaseTransformer
from etl.transformers.article_transformer import ArticleTransformer
from etl.transformers.sales_transformer import SalesTransformer
from etl.transformers.inventory_transformer import InventoryTransformer
from etl.transformers.customer_transformer import CustomerTransformer
from etl.transformers.supplier_transformer import SupplierTransformer
from etl.orchestrator import ETLOrchestrator
from etl.utils.logger import logger

# Sample data for testing
SAMPLE_DATA = {
    "article": [
        {
            "article_id": "12345",
            "name": "Test Article",
            "description": "This is a test article",
            "price": 19.99,
            "category_id": "CAT001",
            "supplier_id": "SUP001",
            "created_at": "2023-01-01T12:00:00Z",
            "updated_at": "2023-01-02T12:00:00Z"
        }
    ],
    "sale": [
        {
            "sale_id": "S001",
            "article_id": "12345",
            "customer_id": "CUST001",
            "branch_id": "BR001",
            "quantity": 2,
            "price": 19.99,
            "total": 39.98,
            "sale_date": "2023-01-15T14:30:00Z",
            "currency": "EUR"
        }
    ],
    "inventory": [
        {
            "inventory_id": "INV001",
            "article_id": "12345",
            "branch_id": "BR001",
            "quantity": 10,
            "updated_at": "2023-01-10T10:00:00Z"
        }
    ],
    "customer": [
        {
            "customer_id": "CUST001",
            "name": "Test Customer",
            "email": "test@example.com",
            "created_at": "2022-12-01T09:00:00Z"
        }
    ],
    "supplier": [
        {
            "supplier_id": "SUP001",
            "name": "Test Supplier",
            "contact_name": "John Doe",
            "email": "john@supplier.com",
            "created_at": "2022-11-15T08:00:00Z"
        }
    ],
    "order": [
        {
            "order_id": "ORD001",
            "supplier_id": "SUP001",
            "branch_id": "BR001",
            "order_date": "2023-01-05T11:00:00Z",
            "expected_delivery_date": "2023-01-12T11:00:00Z",
            "delivery_date": "2023-01-13T14:00:00Z",
            "total_items": 5,
            "total_amount": 99.95,
            "order_items": [
                {
                    "article_id": "12345",
                    "quantity": 5,
                    "price": 19.99
                }
            ]
        }
    ]
}

def test_base_transformer():
    """Test the BaseTransformer class."""
    logger.info("Testing BaseTransformer...")
    
    # Create a simple transformer that inherits from BaseTransformer
    class TestTransformer(BaseTransformer):
        def transform(self, data):
            # Standardize timestamps
            for ts_field in ['created_at', 'updated_at']:
                if ts_field in data:
                    data[ts_field] = self.standardize_timestamp(data[ts_field])
            
            # Normalize product ID
            if 'article_id' in data:
                data['normalized_article_id'] = self.normalize_product_id(data['article_id'])
            
            # Convert currency
            if 'price' in data and 'currency' in data:
                data['price_eur'] = self.convert_currency(data['price'], data['currency'])
            
            return data
    
    # Create an instance of the test transformer
    transformer = TestTransformer()
    
    # Test timestamp standardization
    timestamp_str = "2023-01-15T14:30:00Z"
    standardized = transformer.standardize_timestamp(timestamp_str)
    logger.info(f"Original timestamp: {timestamp_str}")
    logger.info(f"Standardized timestamp: {standardized}")
    
    # Test product ID normalization
    product_id = "00012345"
    normalized = transformer.normalize_product_id(product_id)
    logger.info(f"Original product ID: {product_id}")
    logger.info(f"Normalized product ID: {normalized}")
    
    # Test currency conversion
    amount = 100.0
    from_currency = "USD"
    to_currency = "EUR"
    converted = transformer.convert_currency(amount, from_currency, to_currency)
    logger.info(f"Original amount: {amount} {from_currency}")
    logger.info(f"Converted amount: {converted} {to_currency}")
    
    # Test transform method
    sample_data = {
        "article_id": "00012345",
        "price": 100.0,
        "currency": "USD",
        "created_at": "2023-01-15T14:30:00Z"
    }
    transformed = transformer.transform(sample_data)
    logger.info(f"Original data: {sample_data}")
    logger.info(f"Transformed data: {transformed}")
    
    return True

def test_article_transformer():
    """Test the ArticleTransformer class."""
    logger.info("Testing ArticleTransformer...")
    
    # Create an instance of the ArticleTransformer
    transformer = ArticleTransformer(
        inventory_data=SAMPLE_DATA["inventory"],
        sales_data=SAMPLE_DATA["sale"]
    )
    
    # Test transform method
    sample_article = SAMPLE_DATA["article"][0]
    transformed = transformer.transform(sample_article)
    
    logger.info(f"Original article: {sample_article}")
    logger.info(f"Transformed article: {transformed}")
    
    return True

def test_sales_transformer():
    """Test the SalesTransformer class."""
    logger.info("Testing SalesTransformer...")
    
    # Create an instance of the SalesTransformer
    transformer = SalesTransformer()
    
    # Test transform method
    sample_sale = SAMPLE_DATA["sale"][0]
    transformed = transformer.transform(sample_sale)
    
    logger.info(f"Original sale: {sample_sale}")
    logger.info(f"Transformed sale: {transformed}")
    
    # Test aggregations
    transformer.transform_batch(SAMPLE_DATA["sale"])
    daily_aggs = transformer.get_daily_aggregations()
    weekly_aggs = transformer.get_weekly_aggregations()
    monthly_aggs = transformer.get_monthly_aggregations()
    
    logger.info(f"Daily aggregations: {daily_aggs}")
    logger.info(f"Weekly aggregations: {weekly_aggs}")
    logger.info(f"Monthly aggregations: {monthly_aggs}")
    
    return True

def test_inventory_transformer():
    """Test the InventoryTransformer class."""
    logger.info("Testing InventoryTransformer...")
    
    # Create an instance of the InventoryTransformer
    transformer = InventoryTransformer(
        sales_data=SAMPLE_DATA["sale"]
    )
    
    # Test transform method
    sample_inventory = SAMPLE_DATA["inventory"][0]
    transformed = transformer.transform(sample_inventory)
    
    logger.info(f"Original inventory: {sample_inventory}")
    logger.info(f"Transformed inventory: {transformed}")
    
    # Test inventory history
    transformer.transform_batch(SAMPLE_DATA["inventory"])
    inventory_history = transformer.get_inventory_history()
    
    logger.info(f"Inventory history: {inventory_history}")
    
    return True

def test_customer_transformer():
    """Test the CustomerTransformer class."""
    logger.info("Testing CustomerTransformer...")
    
    # Create an instance of the CustomerTransformer
    transformer = CustomerTransformer(
        sales_data=SAMPLE_DATA["sale"],
        orders_data=SAMPLE_DATA["order"]
    )
    
    # Test transform method
    sample_customer = SAMPLE_DATA["customer"][0]
    transformed = transformer.transform(sample_customer)
    
    logger.info(f"Original customer: {sample_customer}")
    logger.info(f"Transformed customer: {transformed}")
    
    # Test customer purchase patterns
    transformer.transform_batch(SAMPLE_DATA["customer"])
    purchase_patterns = transformer.get_customer_purchase_patterns()
    
    logger.info(f"Customer purchase patterns: {purchase_patterns}")
    
    return True

def test_supplier_transformer():
    """Test the SupplierTransformer class."""
    logger.info("Testing SupplierTransformer...")
    
    # Create an instance of the SupplierTransformer
    transformer = SupplierTransformer(
        orders_data=SAMPLE_DATA["order"]
    )
    
    # Test transform method
    sample_supplier = SAMPLE_DATA["supplier"][0]
    transformed = transformer.transform(sample_supplier)
    
    logger.info(f"Original supplier: {sample_supplier}")
    logger.info(f"Transformed supplier: {transformed}")
    
    # Test supplier metrics
    transformer.transform_batch(SAMPLE_DATA["supplier"])
    supplier_metrics = transformer.get_supplier_metrics()
    
    logger.info(f"Supplier metrics: {supplier_metrics}")
    
    return True

def test_orchestrator():
    """Test the ETLOrchestrator class."""
    logger.info("Testing ETLOrchestrator...")
    
    # Create a mock database session
    class MockSession:
        def __init__(self):
            self.committed = False
            self.rolled_back = False
        
        def query(self, *args, **kwargs):
            class MockQuery:
                def filter(self, *args, **kwargs):
                    return self
                
                def order_by(self, *args, **kwargs):
                    return self
                
                def first(self):
                    return None
            
            return MockQuery()
        
        def add(self, obj):
            pass
        
        def commit(self):
            self.committed = True
        
        def rollback(self):
            self.rolled_back = True
    
    # Create a mock database loader
    class MockDatabaseLoader:
        def __init__(self, session):
            self.session = session
            self.loaded_entities = {}
        
        def load_entity(self, entity_name, data):
            self.loaded_entities[entity_name] = data
            return len(data)
    
    # Create a mock connector
    class MockConnector:
        def __init__(self):
            self.extracted_entities = {}
        
        def get_entity_list(self, entity_name, filter_params=None, batch_size=None):
            return SAMPLE_DATA.get(entity_name, [])
    
    # Create a mock orchestrator
    class MockOrchestrator(ETLOrchestrator):
        def __init__(self, db_session):
            super().__init__(db_session)
            self.loader = MockDatabaseLoader(db_session)
            self.connector = MockConnector()
    
    # Create an instance of the mock orchestrator
    session = MockSession()
    orchestrator = MockOrchestrator(session)
    
    # Test run_etl method
    results = orchestrator.run_etl(entities=["article", "sale", "inventory", "customer", "supplier"])
    
    logger.info(f"ETL results: {results}")
    
    return True

def main():
    """Main function to run all tests."""
    logger.info("Starting transformation tests...")
    
    tests = [
        test_base_transformer,
        test_article_transformer,
        test_sales_transformer,
        test_inventory_transformer,
        test_customer_transformer,
        test_supplier_transformer,
        test_orchestrator
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
        except Exception as e:
            logger.error(f"Error in {test.__name__}: {e}")
            results.append((test.__name__, False))
    
    # Print summary
    logger.info("Test results:")
    for name, result in results:
        status = "PASSED" if result else "FAILED"
        logger.info(f"{name}: {status}")
    
    # Check if all tests passed
    if all(result for _, result in results):
        logger.info("All tests passed!")
        return 0
    else:
        logger.error("Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
