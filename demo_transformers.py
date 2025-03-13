#!/usr/bin/env python
"""
Demonstration script for the ETL transformers.
This script shows how to use the transformer components with sample data.
"""
import json
from datetime import datetime, timedelta
from pprint import pprint

from etl.transformers.base_transformer import BaseTransformer
from etl.transformers.supplier_transformer import SupplierTransformer
from etl.utils.logger import logger

# Create a concrete implementation of BaseTransformer for demonstration
class DemoTransformer(BaseTransformer):
    """Concrete implementation of BaseTransformer for demonstration purposes."""
    
    def transform(self, data):
        """Transform method required by the abstract base class."""
        return data
    
    def transform_batch(self, data_batch):
        """Transform batch method implementation."""
        return [self.transform(item) for item in data_batch]

def create_sample_data():
    """Create sample data for demonstration."""
    # Sample orders data
    orders = []
    
    # Create 10 orders for supplier SUP001 over the last 3 months
    supplier_id = "SUP001"
    base_date = datetime.now() - timedelta(days=90)
    
    for i in range(10):
        order_date = base_date + timedelta(days=i*9)  # Roughly every 9 days
        delivery_date = order_date + timedelta(days=3)  # 3-day lead time
        
        order = {
            "order_id": f"ORD{i+1:03d}",
            "supplier_id": supplier_id,
            "order_date": order_date.isoformat(),
            "expected_delivery_date": (order_date + timedelta(days=2)).isoformat(),
            "actual_delivery_date": delivery_date.isoformat(),
            "status": "completed",
            "items": [
                {
                    "product_id": f"PROD{j+1:03d}",
                    "quantity": 10 + (i % 5),
                    "unit_price": 19.99 + (j * 0.5),
                    "total_price": (19.99 + (j * 0.5)) * (10 + (i % 5))
                }
                for j in range(3)  # 3 items per order
            ],
            "total_amount": sum([(19.99 + (j * 0.5)) * (10 + (i % 5)) for j in range(3)])
        }
        orders.append(order)
    
    # Create 5 orders for supplier SUP002 over the last 3 months
    supplier_id = "SUP002"
    base_date = datetime.now() - timedelta(days=90)
    
    for i in range(5):
        order_date = base_date + timedelta(days=i*18)  # Roughly every 18 days
        delivery_date = order_date + timedelta(days=5)  # 5-day lead time
        
        # One late delivery
        if i == 2:
            delivery_date = order_date + timedelta(days=8)  # 8-day lead time (late)
        
        order = {
            "order_id": f"ORD{i+11:03d}",
            "supplier_id": supplier_id,
            "order_date": order_date.isoformat(),
            "expected_delivery_date": (order_date + timedelta(days=4)).isoformat(),
            "actual_delivery_date": delivery_date.isoformat(),
            "status": "completed",
            "items": [
                {
                    "product_id": f"PROD{j+1:03d}",
                    "quantity": 20 + (i % 3),
                    "unit_price": 29.99 + (j * 0.5),
                    "total_price": (29.99 + (j * 0.5)) * (20 + (i % 3))
                }
                for j in range(2)  # 2 items per order
            ],
            "total_amount": sum([(29.99 + (j * 0.5)) * (20 + (i % 3)) for j in range(2)])
        }
        orders.append(order)
    
    # Sample supplier data
    suppliers = [
        {
            "supplier_id": "SUP001",
            "name": "Reliable Supplies Inc.",
            "contact_name": "John Smith",
            "email": "john@reliablesupplies.com",
            "phone": "+1-555-123-4567",
            "address": "123 Supply St",
            "city": "Supplier City",
            "state": "SC",
            "postal_code": "12345",
            "country": "USA",
            "created_at": (datetime.now() - timedelta(days=365)).isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "supplier_id": "SUP002",
            "name": "Quality Products Ltd.",
            "contact_name": "Jane Doe",
            "email": "jane@qualityproducts.com",
            "phone": "+1-555-987-6543",
            "address": "456 Quality Ave",
            "city": "Quality Town",
            "state": "QT",
            "postal_code": "67890",
            "country": "USA",
            "created_at": (datetime.now() - timedelta(days=300)).isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ]
    
    return {
        "order": orders,
        "supplier": suppliers
    }

def demo_base_transformer():
    """Demonstrate the BaseTransformer functionality."""
    logger.info("Demonstrating BaseTransformer...")
    
    # Create an instance of the concrete implementation of BaseTransformer
    transformer = DemoTransformer()
    
    # Demonstrate timestamp standardization
    timestamps = [
        "2023-01-15T14:30:00Z",
        "2023-01-15 14:30:00",
        "15/01/2023 14:30:00",
        "01/15/2023 2:30 PM",
        1673795400  # Unix timestamp for 2023-01-15T14:30:00Z
    ]
    
    logger.info("Timestamp standardization:")
    for ts in timestamps:
        standardized = transformer.standardize_timestamp(ts)
        logger.info(f"  Original: {ts}, Standardized: {standardized}")
    
    # Demonstrate currency conversion
    amount = 100.0
    from_currency = "USD"
    to_currency = "EUR"
    
    logger.info("Currency conversion:")
    try:
        converted = transformer.convert_currency(amount, from_currency, to_currency)
        logger.info(f"  {amount} {from_currency} = {converted} {to_currency}")
    except Exception as e:
        logger.error(f"  Error in currency conversion: {e}")
    
    # Demonstrate product ID normalization
    product_ids = [
        "PROD-123",
        "prod123",
        "P-123",
        123
    ]
    
    logger.info("Product ID normalization:")
    for pid in product_ids:
        normalized = transformer.normalize_product_id(pid)
        logger.info(f"  Original: {pid}, Normalized: {normalized}")

def demo_supplier_transformer():
    """Demonstrate the SupplierTransformer functionality."""
    logger.info("\nDemonstrating SupplierTransformer...")
    
    # Create sample data
    sample_data = create_sample_data()
    
    # Create an instance of the SupplierTransformer
    transformer = SupplierTransformer(orders_data=sample_data["order"])
    
    # Transform supplier data
    for supplier in sample_data["supplier"]:
        transformed = transformer.transform(supplier)
        logger.info(f"Transformed supplier: {supplier['name']}")
        logger.info(f"  Supplier ID: {transformed['supplier_id']}")
        logger.info(f"  Contact: {transformed['contact_name']}")
        logger.info(f"  Location: {transformed['city']}, {transformed['state']}, {transformed['country']}")
    
    # Generate supplier metrics
    transformer.transform_batch(sample_data["supplier"])
    metrics = transformer.get_supplier_metrics()
    
    logger.info("\nSupplier Metrics:")
    for supplier_id, data in metrics.items():
        logger.info(f"\nMetrics for {supplier_id}:")
        
        if 'order_frequency' in data:
            logger.info(f"  Order Frequency:")
            for key, value in data['order_frequency'].items():
                logger.info(f"    {key}: {value:.2f}")
        
        if 'average_order_size' in data:
            logger.info(f"  Average Order Size:")
            for key, value in data['average_order_size'].items():
                if isinstance(value, (int, float)):
                    logger.info(f"    {key}: {value:.2f}")
                else:
                    logger.info(f"    {key}: {value}")
        
        if 'lead_time' in data:
            logger.info(f"  Lead Time: {data['lead_time']:.1f} days")
        
        if 'on_time_delivery_rate' in data:
            logger.info(f"  On-time Delivery Rate: {data['on_time_delivery_rate']*100:.1f}%")
        
        if 'reliability_score' in data:
            logger.info(f"  Reliability Score: {data['reliability_score']:.2f}/10")

def main():
    """Main function to run the demonstration."""
    logger.info("Starting ETL transformer demonstration...")
    
    demo_base_transformer()
    demo_supplier_transformer()
    
    logger.info("\nDemonstration completed successfully!")
    return 0

if __name__ == "__main__":
    main()
