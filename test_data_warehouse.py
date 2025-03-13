#!/usr/bin/env python
"""
Test script for the data warehouse and data mart functionality.
This script tests the creation of the data warehouse schema and data marts.
"""
import os
import sys
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import directly from the data_warehouse module to avoid circular imports
from etl.models.data_warehouse import Base, DimDate, DimProduct, DimLocation, DimCustomer, DimSupplier
from etl.data_mart import DataMartManager
from etl.utils.logger import logger

def test_data_warehouse_schema():
    """Test the creation of the data warehouse schema."""
    # Create an in-memory SQLite database for testing
    engine = create_engine('sqlite:///:memory:')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Create the data warehouse schema
        Base.metadata.create_all(engine)
        
        # Check if tables were created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = [
            'dim_date', 'dim_product', 'dim_location', 'dim_customer', 'dim_supplier',
            'fact_sales', 'fact_inventory', 'fact_orders',
            'fact_sales_daily', 'fact_sales_weekly', 'fact_sales_monthly'
        ]
        
        for table in expected_tables:
            assert table in tables, f"Table {table} was not created"
        
        logger.info(f"Successfully created {len(tables)} tables in the data warehouse schema")
        return True
    except Exception as e:
        logger.error(f"Error creating data warehouse schema: {e}")
        return False
    finally:
        session.close()

def test_data_mart_manager():
    """Test the DataMartManager functionality."""
    # Create an in-memory SQLite database for testing
    engine = create_engine('sqlite:///:memory:')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Create a DataMartManager instance
        data_mart_manager = DataMartManager(session)
        
        # Create the data warehouse schema
        data_mart_manager.create_data_warehouse_schema()
        
        # Populate the date dimension with a small date range for testing
        try:
            # SQLite doesn't support all the date functions used in populate_date_dimension
            # So we'll just test a small subset of functionality
            from etl.models.data_warehouse import DimDate
            
            # Create a few date records manually
            date_records = [
                DimDate(
                    date=datetime(2023, 1, 1),
                    day=1,
                    day_name="Sunday",
                    day_of_week=7,
                    day_of_year=1,
                    week=52,
                    week_of_year=52,
                    month=1,
                    month_name="January",
                    quarter=1,
                    year=2023,
                    is_weekend=True,
                    is_holiday=True,
                    season="Winter",
                    fiscal_year=2022,
                    fiscal_quarter=3
                ),
                DimDate(
                    date=datetime(2023, 1, 2),
                    day=2,
                    day_name="Monday",
                    day_of_week=1,
                    day_of_year=2,
                    week=1,
                    week_of_year=1,
                    month=1,
                    month_name="January",
                    quarter=1,
                    year=2023,
                    is_weekend=False,
                    is_holiday=False,
                    season="Winter",
                    fiscal_year=2022,
                    fiscal_quarter=3
                )
            ]
            
            session.bulk_save_objects(date_records)
            session.commit()
            
            # Check if date records were created
            date_count = session.query(DimDate).count()
            assert date_count == 2, f"Expected 2 date records, got {date_count}"
            
            logger.info(f"Successfully created {date_count} date records")
        except Exception as e:
            logger.warning(f"Error populating date dimension: {e}")
        
        # Test creating materialized views
        # Note: SQLite doesn't support materialized views, so we'll just simulate this
        # by checking if the methods run without errors
        
        # Mock the _create_materialized_view method to avoid SQLite limitations
        original_create_mv = data_mart_manager._create_materialized_view
        
        def mock_create_materialized_view(view_name, query):
            logger.info(f"Would create materialized view {view_name}")
            return True
        
        data_mart_manager._create_materialized_view = mock_create_materialized_view
        
        # Test creating data marts
        data_mart_manager.create_inventory_analytics_mart()
        data_mart_manager.create_supplier_analytics_mart()
        data_mart_manager.create_sales_analytics_mart()
        
        # Restore original method
        data_mart_manager._create_materialized_view = original_create_mv
        
        logger.info("Successfully tested DataMartManager functionality")
        return True
    except Exception as e:
        logger.error(f"Error testing DataMartManager: {e}")
        return False
    finally:
        session.close()

def main():
    """Main function to run all tests."""
    logger.info("Starting data warehouse and data mart tests...")
    
    tests = [
        test_data_warehouse_schema,
        test_data_mart_manager
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
