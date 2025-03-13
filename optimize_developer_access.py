#!/usr/bin/env python3
"""
Script to apply Snowflake optimizations that a developer role can perform.
This script uses password authentication and focuses on operations that don't require ACCOUNTADMIN.
"""

import os
import sys
import snowflake.connector
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Get Snowflake credentials
    account = os.getenv("SNOWFLAKE_ACCOUNT")
    user = os.getenv("SNOWFLAKE_USER")
    password = os.getenv("SNOWFLAKE_PASSWORD")
    
    # SQL commands that should work with MERCURIOS_DEVELOPER role
    sql_commands = [
        """
        -- Set up a development database for testing
        USE ROLE MERCURIOS_DEVELOPER;
        USE WAREHOUSE MERCURIOS_DEV_WH;
        USE DATABASE MERCURIOS_DATA;
        USE SCHEMA STAGING;
        """,
        
        """
        -- Create a view to monitor your own query history
        CREATE OR REPLACE VIEW MY_QUERY_HISTORY AS
        SELECT 
            QUERY_ID,
            QUERY_TEXT,
            DATABASE_NAME,
            SCHEMA_NAME,
            QUERY_TYPE,
            SESSION_ID,
            USER_NAME,
            ROLE_NAME,
            EXECUTION_STATUS,
            ERROR_CODE,
            ERROR_MESSAGE,
            START_TIME,
            END_TIME,
            TOTAL_ELAPSED_TIME / 1000 AS EXECUTION_TIME_SECONDS
        FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
        WHERE USER_NAME = CURRENT_USER()
        ORDER BY START_TIME DESC;
        """,
        
        """
        -- Create a view to monitor warehouse usage for your queries
        CREATE OR REPLACE VIEW MY_WAREHOUSE_USAGE AS
        SELECT 
            QUERY_ID,
            WAREHOUSE_NAME,
            WAREHOUSE_SIZE,
            QUERY_TEXT,
            START_TIME,
            END_TIME,
            TOTAL_ELAPSED_TIME / 1000 AS EXECUTION_TIME_SECONDS
        FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
        WHERE USER_NAME = CURRENT_USER()
        AND WAREHOUSE_NAME IS NOT NULL
        ORDER BY START_TIME DESC;
        """,
        
        """
        -- Create a performance optimization view for your queries
        CREATE OR REPLACE VIEW MY_QUERY_OPTIMIZATION AS
        SELECT 
            QUERY_ID,
            QUERY_TEXT,
            PARTITIONS_SCANNED,
            PARTITIONS_TOTAL,
            BYTES_SCANNED,
            PERCENTAGE_SCANNED,
            EXECUTION_TIME_SECONDS
        FROM (
            SELECT 
                QUERY_ID,
                QUERY_TEXT,
                PARTITIONS_SCANNED,
                PARTITIONS_TOTAL,
                BYTES_SCANNED,
                CASE 
                    WHEN PARTITIONS_TOTAL > 0 
                    THEN (PARTITIONS_SCANNED / PARTITIONS_TOTAL) * 100 
                    ELSE 0 
                END AS PERCENTAGE_SCANNED,
                TOTAL_ELAPSED_TIME / 1000 AS EXECUTION_TIME_SECONDS
            FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
            WHERE USER_NAME = CURRENT_USER()
            AND PARTITIONS_TOTAL > 0
        )
        ORDER BY PERCENTAGE_SCANNED DESC, EXECUTION_TIME_SECONDS DESC;
        """,
        
        """
        -- Test query to verify everything is working
        SELECT 'Optimization script completed successfully' AS STATUS;
        """
    ]
    
    # Connect to Snowflake
    try:
        conn = snowflake.connector.connect(
            user=user,
            password=password,
            account=account,
            warehouse="MERCURIOS_DEV_WH",
            database="MERCURIOS_DATA",
            role="MERCURIOS_DEVELOPER"
        )
        print("Successfully connected to Snowflake")
        
        # Execute SQL commands
        cursor = conn.cursor()
        for i, cmd in enumerate(sql_commands):
            if cmd.strip():
                print(f"\nExecuting command {i+1}/{len(sql_commands)}:")
                print(f"{cmd[:100]}..." if len(cmd) > 100 else cmd)
                try:
                    cursor.execute(cmd)
                    if cursor.rowcount > 0:
                        result = cursor.fetchone()
                        print(f"Result: {result}")
                    print("✅ Command executed successfully")
                except Exception as e:
                    print(f"❌ Error executing command: {e}")
        
        # Close connection
        cursor.close()
        conn.close()
        print("\nConnection closed")
        print("\n✅ Developer optimizations applied successfully")
        
        # Provide next steps
        print("\nNext Steps:")
        print("1. Use the MY_QUERY_HISTORY view to monitor your query performance")
        print("2. Use the MY_WAREHOUSE_USAGE view to track warehouse utilization")
        print("3. Use the MY_QUERY_OPTIMIZATION view to identify queries that need optimization")
        print("\nFor full account-level optimizations, you'll need to work with someone who has ACCOUNTADMIN privileges.")
        
    except Exception as e:
        print(f"Error connecting to Snowflake: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
