"""
Snowflake Connector for Earth Module

This module provides a secure connection to Snowflake analytics views
for the Mercurios.ai Earth module. It implements:
1. Secure connection with key-pair authentication
2. Query execution with proper error handling
3. Result transformation for GraphQL API consumption
4. Query monitoring and logging
5. Tenant isolation
"""

import os
import json
import logging
import time
from typing import Dict, List, Any, Optional, Union
import snowflake.connector
from snowflake.connector.errors import ProgrammingError, DatabaseError
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('snowflake_connector')

# Load environment variables
load_dotenv()

class SnowflakeConnector:
    """Connector class for Snowflake data warehouse."""
    
    def __init__(self, tenant_id: Optional[str] = None):
        """
        Initialize Snowflake connector with tenant isolation.
        
        Args:
            tenant_id: Optional tenant identifier for multi-tenant isolation
        """
        self.tenant_id = tenant_id
        self.connection = None
        self.account = os.getenv("SNOWFLAKE_ACCOUNT", "VRXDFZX-ZZ95717")
        self.user = os.getenv("SNOWFLAKE_USER", "MERCURIOS_ANALYST")
        self.password = os.getenv("SNOWFLAKE_PASSWORD")
        self.warehouse = os.getenv("SNOWFLAKE_WAREHOUSE", "MERCURIOS_ANALYTICS_WH")
        self.database = os.getenv("SNOWFLAKE_DATABASE", "MERCURIOS_DATA")
        self.schema = os.getenv("SNOWFLAKE_SCHEMA", "ANALYTICS")
        self.role = os.getenv("SNOWFLAKE_ROLE", "MERCURIOS_ANALYST")
        
        # For key-pair authentication (preferred)
        self.private_key_path = os.getenv("SNOWFLAKE_PRIVATE_KEY_PATH")
        self.private_key_passphrase = os.getenv("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE")
        
        # Query monitoring
        self.query_timeout = int(os.getenv("SNOWFLAKE_QUERY_TIMEOUT", "300"))  # 5 minutes default
        
    def connect(self) -> None:
        """Establish connection to Snowflake."""
        try:
            conn_params = {
                "account": self.account,
                "user": self.user,
                "warehouse": self.warehouse,
                "database": self.database,
                "schema": self.schema,
                "role": self.role,
                "client_session_keep_alive": True,
                "application": "Mercurios_Earth_Module"
            }
            
            # Use key-pair authentication if available
            if self.private_key_path:
                with open(self.private_key_path, "rb") as key_file:
                    private_key = key_file.read()
                    
                conn_params["private_key"] = private_key
                if self.private_key_passphrase:
                    conn_params["private_key_passphrase"] = self.private_key_passphrase
            else:
                # Fall back to password authentication
                conn_params["password"] = self.password
            
            self.connection = snowflake.connector.connect(**conn_params)
            logger.info(f"Connected to Snowflake account: {self.account}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Snowflake: {str(e)}")
            raise
    
    def disconnect(self) -> None:
        """Close Snowflake connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Disconnected from Snowflake")
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a query against Snowflake with tenant isolation if applicable.
        
        Args:
            query: SQL query to execute
            params: Query parameters for parameterized queries
            
        Returns:
            List of dictionaries containing query results
        """
        if not self.connection:
            self.connect()
            
        cursor = self.connection.cursor(snowflake.connector.DictCursor)
        
        try:
            # Apply tenant isolation if tenant_id is provided
            if self.tenant_id and "/* TENANT_FILTER */" in query:
                query = query.replace(
                    "/* TENANT_FILTER */", 
                    f"AND tenant_id = '{self.tenant_id}'"
                )
            
            start_time = time.time()
            cursor.execute(query, params, timeout=self.query_timeout)
            execution_time = time.time() - start_time
            
            # Log query performance
            logger.info(f"Query executed in {execution_time:.2f} seconds")
            if execution_time > 5:  # Log slow queries
                logger.warning(f"Slow query detected ({execution_time:.2f}s): {query[:100]}...")
            
            # Fetch results
            results = cursor.fetchall()
            return results
            
        except ProgrammingError as e:
            error_msg = f"Snowflake query error: {str(e)}"
            logger.error(error_msg)
            raise
        except DatabaseError as e:
            error_msg = f"Snowflake database error: {str(e)}"
            logger.error(error_msg)
            raise
        finally:
            cursor.close()
    
    def get_daily_sales_summary(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Get daily sales summary data from Snowflake.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of daily sales summary records
        """
        query = """
        SELECT 
            DATE,
            TOTAL_SALES,
            TOTAL_ORDERS,
            AVERAGE_ORDER_VALUE,
            TOTAL_UNITS_SOLD,
            TOTAL_UNIQUE_CUSTOMERS
        FROM 
            DAILY_SALES_SUMMARY
        WHERE 
            DATE BETWEEN %s AND %s
            /* TENANT_FILTER */
        ORDER BY 
            DATE
        """
        params = {"start_date": start_date, "end_date": end_date}
        return self.execute_query(query, params)
    
    def get_customer_insights(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get customer insights data from Snowflake.
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of customer insight records
        """
        query = """
        SELECT 
            CUSTOMER_ID,
            CUSTOMER_NAME,
            LIFETIME_VALUE,
            LAST_PURCHASE_DATE,
            PURCHASE_FREQUENCY,
            TOTAL_ORDERS,
            AVERAGE_ORDER_VALUE,
            FAVORITE_PRODUCT_CATEGORY
        FROM 
            CUSTOMER_INSIGHTS
        WHERE 
            1=1
            /* TENANT_FILTER */
        ORDER BY 
            LIFETIME_VALUE DESC
        LIMIT %s OFFSET %s
        """
        params = {"limit": limit, "offset": offset}
        return self.execute_query(query, params)
    
    def get_product_performance(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get product performance data from Snowflake.
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of product performance records
        """
        query = """
        SELECT 
            PRODUCT_ID,
            PRODUCT_NAME,
            TOTAL_SALES,
            QUANTITY_SOLD,
            PROFIT_MARGIN,
            STOCK_LEVEL,
            REORDER_POINT,
            DAYS_OF_SUPPLY
        FROM 
            PRODUCT_PERFORMANCE
        WHERE 
            1=1
            /* TENANT_FILTER */
        ORDER BY 
            TOTAL_SALES DESC
        LIMIT %s OFFSET %s
        """
        params = {"limit": limit, "offset": offset}
        return self.execute_query(query, params)
    
    def get_inventory_status(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get inventory status data from Snowflake.
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of inventory status records
        """
        query = """
        SELECT 
            PRODUCT_ID,
            PRODUCT_NAME,
            CURRENT_STOCK,
            REORDER_POINT,
            DAYS_OF_SUPPLY,
            STOCK_STATUS,
            LAST_RESTOCK_DATE,
            NEXT_RESTOCK_DATE
        FROM 
            INVENTORY_STATUS
        WHERE 
            1=1
            /* TENANT_FILTER */
        ORDER BY 
            DAYS_OF_SUPPLY ASC
        LIMIT %s OFFSET %s
        """
        params = {"limit": limit, "offset": offset}
        return self.execute_query(query, params)
    
    def get_shop_performance(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get shop performance data from Snowflake.
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of shop performance records
        """
        query = """
        SELECT 
            SHOP_ID,
            SHOP_NAME,
            TOTAL_SALES,
            TOTAL_ORDERS,
            AVERAGE_ORDER_VALUE,
            TOTAL_CUSTOMERS,
            TOP_SELLING_CATEGORY,
            SALES_GROWTH_RATE
        FROM 
            SHOP_PERFORMANCE
        WHERE 
            1=1
            /* TENANT_FILTER */
        ORDER BY 
            TOTAL_SALES DESC
        LIMIT %s OFFSET %s
        """
        params = {"limit": limit, "offset": offset}
        return self.execute_query(query, params)
    
    def get_business_dashboard_metrics(self) -> Dict[str, Any]:
        """
        Get business dashboard metrics from Snowflake.
        
        Returns:
            Dictionary containing business dashboard metrics
        """
        query = """
        SELECT 
            METRIC_NAME,
            METRIC_VALUE,
            COMPARISON_VALUE,
            PERCENT_CHANGE,
            TREND_DIRECTION,
            TIME_PERIOD
        FROM 
            BUSINESS_DASHBOARD
        WHERE 
            1=1
            /* TENANT_FILTER */
        """
        results = self.execute_query(query)
        
        # Transform results into a more usable format for the dashboard
        metrics = {}
        for row in results:
            metric_name = row["METRIC_NAME"]
            metrics[metric_name] = {
                "value": row["METRIC_VALUE"],
                "comparison_value": row["COMPARISON_VALUE"],
                "percent_change": row["PERCENT_CHANGE"],
                "trend_direction": row["TREND_DIRECTION"],
                "time_period": row["TIME_PERIOD"]
            }
        
        return metrics
    
    def get_inventory_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get inventory optimization recommendations.
        
        Returns:
            List of inventory recommendations
        """
        query = """
        WITH LowStock AS (
            SELECT 
                PRODUCT_ID,
                PRODUCT_NAME,
                CURRENT_STOCK,
                REORDER_POINT,
                DAYS_OF_SUPPLY
            FROM 
                INVENTORY_STATUS
            WHERE 
                CURRENT_STOCK < REORDER_POINT
                /* TENANT_FILTER */
        ),
        OverStock AS (
            SELECT 
                PRODUCT_ID,
                PRODUCT_NAME,
                CURRENT_STOCK,
                REORDER_POINT,
                DAYS_OF_SUPPLY
            FROM 
                INVENTORY_STATUS
            WHERE 
                DAYS_OF_SUPPLY > 90
                /* TENANT_FILTER */
        )
        
        SELECT 
            PRODUCT_ID,
            PRODUCT_NAME,
            CURRENT_STOCK,
            REORDER_POINT,
            DAYS_OF_SUPPLY,
            'RESTOCK' as RECOMMENDATION_TYPE,
            'Product needs to be restocked soon' as RECOMMENDATION_TEXT,
            (REORDER_POINT - CURRENT_STOCK) as RECOMMENDED_ACTION_VALUE
        FROM 
            LowStock
        
        UNION ALL
        
        SELECT 
            PRODUCT_ID,
            PRODUCT_NAME,
            CURRENT_STOCK,
            REORDER_POINT,
            DAYS_OF_SUPPLY,
            'REDUCE_INVENTORY' as RECOMMENDATION_TYPE,
            'Product has excess inventory' as RECOMMENDATION_TEXT,
            (CURRENT_STOCK - (REORDER_POINT * 2)) as RECOMMENDED_ACTION_VALUE
        FROM 
            OverStock
        
        ORDER BY 
            DAYS_OF_SUPPLY ASC
        """
        return self.execute_query(query)


# Example usage
if __name__ == "__main__":
    # For testing the connector
    connector = SnowflakeConnector()
    try:
        # Test connection
        connector.connect()
        
        # Test query
        start_date = "2025-01-01"
        end_date = "2025-03-13"
        results = connector.get_daily_sales_summary(start_date, end_date)
        
        # Print results
        print(f"Retrieved {len(results)} records from DAILY_SALES_SUMMARY")
        for i, row in enumerate(results[:5]):
            print(f"Row {i+1}: {json.dumps(row)}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        connector.disconnect()
