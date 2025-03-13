#!/usr/bin/env python3
"""
Check the status of Fivetran transformations in Snowflake
"""

import json
import snowflake.connector
import sys
from datetime import datetime

def main():
    """Check the status of Fivetran transformations"""
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
        
        # Check if the TRANSFORMATION_RUNS table exists
        print("Checking if TRANSFORMATION_RUNS table exists...")
        cursor.execute("SHOW TABLES LIKE 'TRANSFORMATION_RUNS' IN SCHEMA MERCURIOS_DATA.FIVETRAN_METADATA")
        tables = cursor.fetchall()
        
        if not tables:
            print("TRANSFORMATION_RUNS table does not exist. Transformations may not have started yet.")
            sys.exit(0)
        
        print("TRANSFORMATION_RUNS table exists!")
        
        # Check transformation runs
        print("\nChecking recent transformation runs...")
        try:
            cursor.execute("""
                SELECT * 
                FROM MERCURIOS_DATA.FIVETRAN_METADATA.TRANSFORMATION_RUNS
                ORDER BY _FIVETRAN_SYNCED DESC
                LIMIT 10
            """)
            runs = cursor.fetchall()
            
            if runs:
                # Get column names
                column_names = [desc[0] for desc in cursor.description]
                
                print(f"Found {len(runs)} transformation runs:")
                for run in runs:
                    print("\nTransformation Run:")
                    for i, value in enumerate(run):
                        print(f"- {column_names[i]}: {value}")
            else:
                print("No transformation runs found.")
        except Exception as e:
            print(f"Error querying transformation runs: {e}")
        
        # Check if any Fivetran Log tables/views exist
        print("\nChecking for Fivetran Log objects...")
        cursor.execute("SHOW SCHEMAS LIKE 'FIVETRAN_LOG' IN DATABASE MERCURIOS_DATA")
        schemas = cursor.fetchall()
        
        if schemas:
            print("FIVETRAN_LOG schema exists!")
            
            # Check for views
            cursor.execute("SHOW VIEWS IN SCHEMA MERCURIOS_DATA.FIVETRAN_LOG")
            views = cursor.fetchall()
            
            if views:
                print(f"Found {len(views)} views in FIVETRAN_LOG schema:")
                for view in views:
                    print(f"- {view[1]}")
            else:
                print("No views found in FIVETRAN_LOG schema yet.")
                
            # Check for tables
            cursor.execute("SHOW TABLES IN SCHEMA MERCURIOS_DATA.FIVETRAN_LOG")
            tables = cursor.fetchall()
            
            if tables:
                print(f"Found {len(tables)} tables in FIVETRAN_LOG schema:")
                for table in tables:
                    print(f"- {table[1]}")
            else:
                print("No tables found in FIVETRAN_LOG schema yet.")
        else:
            print("FIVETRAN_LOG schema does not exist yet.")
        
        # Close the connection
        cursor.close()
        conn.close()
        
        print(f"\nCheck completed at {datetime.now()}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
