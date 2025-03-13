#!/usr/bin/env python3
"""
Check the progress of Fivetran transformations in Snowflake
"""

import json
import snowflake.connector
import sys
import time
from datetime import datetime

def main():
    """Check the progress of Fivetran transformations"""
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
        cursor.execute("SHOW TABLES LIKE 'TRANSFORMATION_RUNS' IN SCHEMA MERCURIOS_DATA.FIVETRAN_METADATA")
        tables = cursor.fetchall()
        
        if not tables:
            print("TRANSFORMATION_RUNS table does not exist. Transformations may not have started yet.")
            sys.exit(0)
        
        # Start monitoring
        print("Monitoring Fivetran transformation progress...")
        print("Press Ctrl+C to stop monitoring")
        
        attempt = 0
        max_attempts = 30
        
        try:
            while attempt < max_attempts:
                attempt += 1
                
                # Check transformation runs
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
                    LIMIT 1
                """)
                run = cursor.fetchone()
                
                if run:
                    destination_id, job_id, job_name, project_type, measured_date, updated_at, model_runs = run
                    
                    # Check if the FIVETRAN_LOG schema exists
                    cursor.execute("SHOW SCHEMAS LIKE 'FIVETRAN_LOG' IN DATABASE MERCURIOS_DATA")
                    schemas = cursor.fetchall()
                    
                    if schemas:
                        # Check how many views exist
                        cursor.execute("SHOW VIEWS IN SCHEMA MERCURIOS_DATA.FIVETRAN_LOG")
                        views = cursor.fetchall()
                        
                        print(f"{datetime.now()} - FIVETRAN_LOG schema exists with {len(views)} views. Model runs: {model_runs}")
                        
                        if len(views) >= 19:  # Expected number of views
                            print(f"Quickstart Data Model deployment complete with {len(views)} views!")
                            break
                    else:
                        print(f"{datetime.now()} - FIVETRAN_LOG schema does not exist yet. Model runs: {model_runs}")
                else:
                    print(f"{datetime.now()} - No transformation runs found.")
                
                # Wait before checking again
                print(f"Checking again in 60 seconds... (attempt {attempt}/{max_attempts})")
                time.sleep(60)
                
            if attempt >= max_attempts:
                print("Maximum monitoring time reached. Exiting.")
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user.")
        
        # Close the connection
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
