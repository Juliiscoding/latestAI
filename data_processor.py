"""
Mock DataProcessor module for testing the Lambda function
"""
import logging
from datetime import datetime, timedelta

logger = logging.getLogger()

class DataProcessor:
    """Mock DataProcessor class for testing"""
    
    def __init__(self, api_client=None):
        self.api_client = api_client
    
    def process_data(self, data, entity_type):
        """Mock method to process data"""
        # Simply return the data unchanged for testing
        return data
    
    def enrich_data(self, data, entity_type):
        """Mock method to enrich data"""
        # Simply return the data unchanged for testing
        return data
        
    def process_articles(self, updated_since=None):
        """Mock method to process articles"""
        logger.info(f"Mock processing articles since {updated_since}")
        # Return sample article data
        return [
            {"id": "A001", "name": "Test Article 1", "price": 19.99, "updated_at": datetime.now().isoformat()},
            {"id": "A002", "name": "Test Article 2", "price": 29.99, "updated_at": datetime.now().isoformat()}
        ]
    
    def process_customers(self, updated_since=None):
        """Mock method to process customers"""
        logger.info(f"Mock processing customers since {updated_since}")
        # Return sample customer data
        return [
            {"id": "C001", "name": "Test Customer 1", "email": "customer1@example.com", "updated_at": datetime.now().isoformat()},
            {"id": "C002", "name": "Test Customer 2", "email": "customer2@example.com", "updated_at": datetime.now().isoformat()}
        ]
    
    def process_orders(self, updated_since=None):
        """Mock method to process orders"""
        logger.info(f"Mock processing orders since {updated_since}")
        # Return sample order data
        return [
            {"id": "O001", "customer_id": "C001", "total": 49.99, "status": "completed", "updated_at": datetime.now().isoformat()},
            {"id": "O002", "customer_id": "C002", "total": 99.99, "status": "pending", "updated_at": datetime.now().isoformat()}
        ]
    
    def process_sales(self, updated_since=None):
        """Mock method to process sales"""
        logger.info(f"Mock processing sales since {updated_since}")
        # Return sample sales data
        return [
            {"id": "S001", "article_id": "A001", "quantity": 2, "price": 19.99, "updated_at": datetime.now().isoformat()},
            {"id": "S002", "article_id": "A002", "quantity": 1, "price": 29.99, "updated_at": datetime.now().isoformat()}
        ]
    
    def process_inventory(self, updated_since=None):
        """Mock method to process inventory"""
        logger.info(f"Mock processing inventory since {updated_since}")
        # Return sample inventory data
        return [
            {"article_id": "A001", "warehouse_id": "W001", "quantity": 100, "updated_at": datetime.now().isoformat()},
            {"article_id": "A002", "warehouse_id": "W001", "quantity": 50, "updated_at": datetime.now().isoformat()}
        ]
