#!/usr/bin/env python3
"""
Script to analyze Snowflake costs and identify what's causing the high spending.
"""

import os
import sys
import pandas as pd
import snowflake.connector
from dotenv import load_dotenv
from datetime import datetime, timedelta

def main():
    # Load environment variables
    load_dotenv()
    
    # Get Snowflake credentials
    account = os.getenv("SNOWFLAKE_ACCOUNT")
    user = os.getenv("SNOWFLAKE_USER")
    password = os.getenv("SNOWFLAKE_PASSWORD")
    
    # Connect to Snowflake
    try:
        print("Connecting to Snowflake to analyze cost drivers...")
        conn = snowflake.connector.connect(
            user=user,
            password=password,
            account=account,
            warehouse="MERCURIOS_DEV_WH",  # Using the smallest warehouse
            role="MERCURIOS_DEVELOPER"
        )
        print("Successfully connected to Snowflake")
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Get warehouse usage in the last 7 days
        print("\n=== WAREHOUSE USAGE (LAST 7 DAYS) ===")
        warehouse_query = """
        SELECT 
            WAREHOUSE_NAME,
            COUNT(*) as QUERY_COUNT,
            SUM(TOTAL_ELAPSED_TIME)/1000/60 as TOTAL_RUNTIME_MINUTES,
            SUM(BYTES_SCANNED)/1024/1024/1024 as TOTAL_GB_SCANNED
        FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        WHERE START_TIME >= DATEADD(day, -7, CURRENT_TIMESTAMP())
        GROUP BY WAREHOUSE_NAME
        ORDER BY TOTAL_RUNTIME_MINUTES DESC;
        """
        cursor.execute(warehouse_query)
        warehouse_usage = cursor.fetchall()
        
        # Print warehouse usage
        print(f"{'WAREHOUSE':<25} {'QUERIES':<10} {'RUNTIME (MIN)':<15} {'DATA SCANNED (GB)':<20}")
        print("-" * 70)
        for row in warehouse_usage:
            print(f"{row[0]:<25} {row[1]:<10} {row[2]:<15.2f} {row[3]:<20.2f}")
        
        # Get most expensive queries
        print("\n=== TOP 10 MOST EXPENSIVE QUERIES (LAST 7 DAYS) ===")
        query_query = """
        SELECT 
            QUERY_ID,
            USER_NAME,
            WAREHOUSE_NAME,
            DATABASE_NAME,
            SCHEMA_NAME,
            TOTAL_ELAPSED_TIME/1000 as EXECUTION_TIME_SECONDS,
            BYTES_SCANNED/1024/1024/1024 as GB_SCANNED,
            QUERY_TEXT
        FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        WHERE START_TIME >= DATEADD(day, -7, CURRENT_TIMESTAMP())
        AND EXECUTION_STATUS = 'SUCCESS'
        ORDER BY TOTAL_ELAPSED_TIME DESC
        LIMIT 10;
        """
        cursor.execute(query_query)
        expensive_queries = cursor.fetchall()
        
        # Print expensive queries
        print(f"{'USER':<20} {'WAREHOUSE':<25} {'TIME (SEC)':<12} {'DATA (GB)':<10} {'QUERY':<50}")
        print("-" * 120)
        for row in expensive_queries:
            query_text = row[7][:50] + "..." if len(row[7]) > 50 else row[7]
            print(f"{row[1]:<20} {row[2]:<25} {row[5]:<12.2f} {row[6]:<10.2f} {query_text}")
        
        # Get automated tasks and jobs
        print("\n=== AUTOMATED TASKS AND JOBS ===")
        tasks_query = """
        SHOW TASKS;
        """
        try:
            cursor.execute(tasks_query)
            tasks = cursor.fetchall()
            if tasks:
                print(f"{'NAME':<30} {'WAREHOUSE':<25} {'SCHEDULE':<20} {'STATE':<10}")
                print("-" * 85)
                for task in tasks:
                    print(f"{task[0]:<30} {task[8]:<25} {task[10]:<20} {task[5]:<10}")
            else:
                print("No scheduled tasks found.")
        except Exception as e:
            print(f"Could not retrieve tasks: {e}")
        
        # Check for large tables that might be causing high storage costs
        print("\n=== LARGEST TABLES BY ROW COUNT ===")
        tables_query = """
        SELECT 
            TABLE_CATALOG,
            TABLE_SCHEMA,
            TABLE_NAME,
            ROW_COUNT,
            BYTES/1024/1024/1024 as SIZE_GB
        FROM SNOWFLAKE.ACCOUNT_USAGE.TABLE_STORAGE_METRICS
        WHERE TABLE_CATALOG != 'SNOWFLAKE'
        ORDER BY ROW_COUNT DESC
        LIMIT 10;
        """
        try:
            cursor.execute(tables_query)
            tables = cursor.fetchall()
            if tables:
                print(f"{'DATABASE':<20} {'SCHEMA':<20} {'TABLE':<30} {'ROWS':<15} {'SIZE (GB)':<10}")
                print("-" * 95)
                for table in tables:
                    print(f"{table[0]:<20} {table[1]:<20} {table[2]:<30} {table[3]:<15,} {table[4]:<10.2f}")
            else:
                print("No table storage metrics available.")
        except Exception as e:
            print(f"Could not retrieve table metrics: {e}")
        
        # Check for Fivetran activity
        print("\n=== FIVETRAN USER ACTIVITY (LAST 7 DAYS) ===")
        fivetran_query = """
        SELECT 
            START_TIME,
            USER_NAME,
            WAREHOUSE_NAME,
            TOTAL_ELAPSED_TIME/1000 as EXECUTION_TIME_SECONDS,
            QUERY_TEXT
        FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        WHERE START_TIME >= DATEADD(day, -7, CURRENT_TIMESTAMP())
        AND USER_NAME LIKE '%FIVETRAN%'
        ORDER BY START_TIME DESC
        LIMIT 10;
        """
        try:
            cursor.execute(fivetran_query)
            fivetran_activity = cursor.fetchall()
            if fivetran_activity:
                print(f"{'TIMESTAMP':<25} {'USER':<20} {'WAREHOUSE':<25} {'TIME (SEC)':<12} {'QUERY':<50}")
                print("-" * 130)
                for row in fivetran_activity:
                    query_text = row[4][:50] + "..." if len(row[4]) > 50 else row[4]
                    print(f"{row[0]:<25} {row[1]:<20} {row[2]:<25} {row[3]:<12.2f} {query_text}")
            else:
                print("No Fivetran activity found.")
        except Exception as e:
            print(f"Could not retrieve Fivetran activity: {e}")
        
        # Close connection
        cursor.close()
        conn.close()
        print("\nConnection closed")
        
        # Provide cost reduction recommendations
        print("\n=== COST REDUCTION RECOMMENDATIONS ===")
        print("""
Based on the analysis above, here are targeted recommendations:

1. IMMEDIATE ACTIONS:
   - Run the SQL commands in cost_reduction_commands.sql to immediately reduce costs
   - Suspend the MERCURIOS_LOADING_WH warehouse which is consuming the most credits
   - Reduce the size of all warehouses to XSMALL
   - Set auto-suspend timeout to 60 seconds (1 minute)

2. FIVETRAN OPTIMIZATION:
   - Review the Fivetran sync schedule - consider reducing frequency
   - Use a smaller dedicated warehouse for Fivetran operations
   - Set stricter resource limits on the Fivetran warehouse

3. QUERY OPTIMIZATION:
   - Review and optimize the expensive queries identified above
   - Add appropriate filters and clustering keys
   - Consider materializing frequently used query results

4. STORAGE OPTIMIZATION:
   - Review the largest tables identified above
   - Implement data retention policies
   - Consider moving historical data to cheaper storage tiers

5. MONITORING:
   - Implement credit usage alerts
   - Set up daily cost monitoring
   - Review warehouse usage patterns regularly
        """)
        
    except Exception as e:
        print(f"Error connecting to Snowflake: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
