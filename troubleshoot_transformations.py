#!/usr/bin/env python3
"""
Troubleshoot Fivetran transformations in Snowflake
"""

import json
import snowflake.connector
import sys
from datetime import datetime
from tabulate import tabulate

def main():
    """Troubleshoot Fivetran transformations"""
    # Load Snowflake config
    with open('snowflake_config.json', 'r') as f:
        config = json.load(f)

    # Connect to Snowflake
    try:
        conn = snowflake.connector.connect(
            user=config['username'],
            password=config['password'],
            account=config['account'],
            warehouse=config['warehouse'],
            database=config['database'],
            schema=config['schema'],
            role=config['role']
        )
        
        cursor = conn.cursor()
        
        print("===== FIVETRAN TRANSFORMATION TROUBLESHOOTING =====")
        print(f"Started at: {datetime.now()}")
        print("=" * 50)
        
        # Check if the TRANSFORMATION_RUNS table exists
        print("\n1. Checking transformation runs...")
        cursor.execute("SHOW TABLES LIKE 'TRANSFORMATION_RUNS' IN SCHEMA MERCURIOS_DATA.FIVETRAN_METADATA")
        tables = cursor.fetchall()
        
        if not tables:
            print("TRANSFORMATION_RUNS table does not exist. Transformations may not have started yet.")
        else:
            print("TRANSFORMATION_RUNS table exists!")
            
            # Check transformation runs
            try:
                cursor.execute("""
                    SELECT 
                        DESTINATION_ID,
                        JOB_ID,
                        JOB_NAME,
                        PROJECT_TYPE,
                        MEASURED_DATE,
                        UPDATED_AT,
                        MODEL_RUNS
                    FROM MERCURIOS_DATA.FIVETRAN_METADATA.TRANSFORMATION_RUNS
                    ORDER BY UPDATED_AT DESC
                    LIMIT 5
                """)
                runs = cursor.fetchall()
                
                if runs:
                    headers = ["Destination ID", "Job ID", "Job Name", "Type", "Date", "Updated At", "Models Run"]
                    print("\nRecent transformation runs:")
                    print(tabulate(runs, headers=headers, tablefmt="grid"))
                else:
                    print("No transformation runs found.")
            except Exception as e:
                print(f"Error querying transformation runs: {e}")
        
        # Check Fivetran logs for errors
        print("\n2. Checking Fivetran logs for errors...")
        try:
            # First, get the column names from the LOG table
            cursor.execute("DESCRIBE TABLE MERCURIOS_DATA.FIVETRAN_METADATA.LOG")
            columns = cursor.fetchall()
            column_names = [col[0] for col in columns]
            
            # Check if the expected columns exist
            created_at_col = "CREATED_AT"
            message_type_col = "MESSAGE_TYPE"
            message_event_col = "MESSAGE_EVENT"
            message_text_col = "MESSAGE_TEXT"
            connector_id_col = "CONNECTOR_ID"
            
            # Map to actual column names if they exist with different names
            for col in column_names:
                if col.upper() == "CREATED_AT" or "CREATED" in col.upper() or "TIME" in col.upper():
                    created_at_col = col
                if "TYPE" in col.upper() and "MESSAGE" in col.upper():
                    message_type_col = col
                if "EVENT" in col.upper() and "MESSAGE" in col.upper():
                    message_event_col = col
                if "TEXT" in col.upper() and "MESSAGE" in col.upper():
                    message_text_col = col
                if "CONNECTOR" in col.upper() and "ID" in col.upper():
                    connector_id_col = col
            
            print(f"Using columns: {created_at_col}, {connector_id_col}, {message_type_col}, {message_event_col}, {message_text_col}")
            
            # Now build the query with the correct column names
            query = f"""
                SELECT 
                    {created_at_col},
                    {connector_id_col},
                    {message_type_col},
                    {message_event_col},
                    {message_text_col}
                FROM MERCURIOS_DATA.FIVETRAN_METADATA.LOG
                WHERE {message_type_col} LIKE '%ERROR%'
                ORDER BY {created_at_col} DESC
                LIMIT 10
            """
            
            cursor.execute(query)
            errors = cursor.fetchall()
            
            if errors:
                headers = ["Created At", "Connector ID", "Type", "Event", "Message"]
                print("\nRecent error logs:")
                print(tabulate(errors, headers=headers, tablefmt="grid"))
            else:
                print("No error logs found. This is good!")
        except Exception as e:
            print(f"Error querying logs: {e}")
        
        # Check Fivetran Log schema
        print("\n3. Checking FIVETRAN_LOG schema...")
        cursor.execute("SHOW SCHEMAS LIKE 'FIVETRAN_LOG' IN DATABASE MERCURIOS_DATA")
        schemas = cursor.fetchall()
        
        if schemas:
            print("FIVETRAN_LOG schema exists!")
            
            # Check for views
            cursor.execute("SHOW VIEWS IN SCHEMA MERCURIOS_DATA.FIVETRAN_LOG")
            views = cursor.fetchall()
            
            if views:
                view_names = [view[1] for view in views]
                print(f"\nFound {len(views)} views in FIVETRAN_LOG schema:")
                
                # Check for expected views
                expected_views = [
                    "CONNECTOR_STATUS",
                    "SYNC_PERFORMANCE",
                    "ERROR_REPORTING",
                    "SCHEMA_CHANGES",
                    "DAILY_API_CALLS",
                    "MONTHLY_ACTIVE_ROWS",
                    "CONNECTOR_ISSUES"
                ]
                
                print("\nStatus of key views:")
                for view in expected_views:
                    if view in view_names:
                        print(f"✅ {view} - Created")
                    else:
                        print(f"❌ {view} - Missing")
            else:
                print("No views found in FIVETRAN_LOG schema yet.")
                
            # Try to query a view if it exists
            if "CONNECTOR_STATUS" in view_names:
                print("\n4. Testing CONNECTOR_STATUS view...")
                try:
                    cursor.execute("""
                        SELECT * FROM MERCURIOS_DATA.FIVETRAN_LOG.CONNECTOR_STATUS
                        LIMIT 5
                    """)
                    status = cursor.fetchall()
                    
                    if status:
                        headers = [desc[0] for desc in cursor.description]
                        print("\nConnector status data:")
                        print(tabulate(status, headers=headers, tablefmt="grid"))
                    else:
                        print("No data found in CONNECTOR_STATUS view.")
                except Exception as e:
                    print(f"Error querying CONNECTOR_STATUS view: {e}")
        else:
            print("FIVETRAN_LOG schema does not exist yet.")
            
            # Check if there are any issues with the warehouse
            print("\n4. Checking warehouse status...")
            try:
                cursor.execute("SHOW WAREHOUSES")
                warehouses = cursor.fetchall()
                
                if warehouses:
                    warehouse_names = [w[0] for w in warehouses]
                    if config['warehouse'] in warehouse_names:
                        print(f"Warehouse '{config['warehouse']}' exists.")
                        
                        # Check warehouse status
                        cursor.execute(f"SHOW WAREHOUSES LIKE '{config['warehouse']}'")
                        warehouse_info = cursor.fetchone()
                        if warehouse_info:
                            print(f"Warehouse state: {warehouse_info[3]}")
                            print(f"Warehouse size: {warehouse_info[2]}")
                    else:
                        print(f"Warehouse '{config['warehouse']}' does not exist!")
                else:
                    print("No warehouses found.")
            except Exception as e:
                print(f"Error checking warehouse status: {e}")
        
        # Check if there are any issues with permissions
        print("\n5. Checking permissions...")
        try:
            cursor.execute(f"SHOW GRANTS TO ROLE {config['role']}")
            grants = cursor.fetchall()
            
            if grants:
                print(f"Role '{config['role']}' has {len(grants)} grants.")
                
                # Check for specific permissions
                has_usage = False
                has_select = False
                
                for grant in grants:
                    if "USAGE" in str(grant) and "MERCURIOS_DATA" in str(grant):
                        has_usage = True
                    if "SELECT" in str(grant) and "MERCURIOS_DATA" in str(grant):
                        has_select = True
                
                if has_usage:
                    print("✅ Has USAGE permission on MERCURIOS_DATA")
                else:
                    print("❌ Missing USAGE permission on MERCURIOS_DATA")
                    
                if has_select:
                    print("✅ Has SELECT permission on MERCURIOS_DATA")
                else:
                    print("❌ Missing SELECT permission on MERCURIOS_DATA")
            else:
                print(f"No grants found for role '{config['role']}'.")
        except Exception as e:
            print(f"Error checking permissions: {e}")
        
        # Close the connection
        cursor.close()
        conn.close()
        
        print("\n===== TROUBLESHOOTING COMPLETED =====")
        print(f"Finished at: {datetime.now()}")
        print("=" * 50)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
