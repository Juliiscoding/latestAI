#!/usr/bin/env python3
"""
Emergency script to immediately stop Snowflake spending
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
    
    # Connect to Snowflake
    try:
        print("Connecting to Snowflake to stop spending...")
        conn = snowflake.connector.connect(
            user=user,
            password=password,
            account=account,
            warehouse="MERCURIOS_DEV_WH",  # Use the smallest warehouse
            role="MERCURIOS_DEVELOPER"
        )
        print("Successfully connected to Snowflake")
        
        # Create a cursor
        cursor = conn.cursor()
        
        # First, check what warehouses exist
        print("\nChecking existing warehouses...")
        cursor.execute("SHOW WAREHOUSES")
        warehouses = cursor.fetchall()
        
        warehouse_names = []
        print("\nCurrent warehouse settings:")
        for wh in warehouses:
            wh_name = wh[0]
            wh_size = wh[3]
            wh_auto_suspend = wh[5]
            wh_status = "RUNNING" if wh[8] == "STARTED" else "SUSPENDED"
            warehouse_names.append(wh_name)
            print(f"- {wh_name}: Size={wh_size}, Auto-suspend={wh_auto_suspend}s, Status={wh_status}")
        
        # Now suspend and resize each warehouse
        for wh_name in warehouse_names:
            print(f"\nOptimizing warehouse: {wh_name}")
            
            # 1. Suspend the warehouse
            try:
                print(f"  Suspending {wh_name}...")
                cursor.execute(f"ALTER WAREHOUSE {wh_name} SUSPEND")
                print(f"  ✅ {wh_name} suspended")
            except Exception as e:
                print(f"  ❌ Could not suspend {wh_name}: {e}")
            
            # 2. Set auto-suspend to 60 seconds
            try:
                print(f"  Setting auto-suspend to 60 seconds for {wh_name}...")
                cursor.execute(f"ALTER WAREHOUSE {wh_name} SET AUTO_SUSPEND = 60")
                print(f"  ✅ Auto-suspend set to 60 seconds for {wh_name}")
            except Exception as e:
                print(f"  ❌ Could not set auto-suspend for {wh_name}: {e}")
            
            # 3. Resize to X-Small (if not already)
            try:
                print(f"  Resizing {wh_name} to X-Small...")
                cursor.execute(f"ALTER WAREHOUSE {wh_name} SET WAREHOUSE_SIZE = 'XSMALL'")
                print(f"  ✅ {wh_name} resized to X-Small")
            except Exception as e:
                print(f"  ❌ Could not resize {wh_name}: {e}")
            
            # 4. Disable multi-clustering
            try:
                print(f"  Disabling multi-clustering for {wh_name}...")
                cursor.execute(f"ALTER WAREHOUSE {wh_name} SET MAX_CLUSTER_COUNT = 1, MIN_CLUSTER_COUNT = 1")
                print(f"  ✅ Multi-clustering disabled for {wh_name}")
            except Exception as e:
                print(f"  ❌ Could not disable multi-clustering for {wh_name}: {e}")
        
        # Verify changes
        print("\nVerifying changes...")
        cursor.execute("SHOW WAREHOUSES")
        warehouses = cursor.fetchall()
        
        print("\nUpdated warehouse settings:")
        for wh in warehouses:
            wh_name = wh[0]
            wh_size = wh[3]
            wh_auto_suspend = wh[5]
            wh_status = "RUNNING" if wh[8] == "STARTED" else "SUSPENDED"
            print(f"- {wh_name}: Size={wh_size}, Auto-suspend={wh_auto_suspend}s, Status={wh_status}")
        
        # Close connection
        cursor.close()
        conn.close()
        print("\nConnection closed")
        print("\n✅ Emergency cost reduction measures applied")
        
        # Provide next steps
        print("\n=== NEXT STEPS TO FURTHER REDUCE COSTS ===")
        print("""
1. REVIEW FIVETRAN INTEGRATION
   - Check if Fivetran is running unnecessary syncs
   - Reduce sync frequency if possible
   - Consider pausing Fivetran connectors temporarily

2. CHECK FOR AUTOMATED JOBS
   - Look for any scheduled jobs or tasks that might be running
   - Pause or reduce frequency of non-critical jobs

3. IMPLEMENT PROPER MONITORING
   - Set up email alerts for credit usage
   - Check costs daily until they stabilize

4. LONG-TERM OPTIMIZATION
   - Optimize your most expensive queries
   - Implement proper data retention policies
   - Consider time-travel and fail-safe period adjustments
   - Review materialized views and other expensive features
        """)
        
    except Exception as e:
        print(f"Error connecting to Snowflake: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
