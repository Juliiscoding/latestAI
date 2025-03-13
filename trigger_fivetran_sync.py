#!/usr/bin/env python3
"""
Script to trigger a manual sync in Fivetran and check the integration pipeline
"""

import requests
import os
import json
import time
import boto3
import snowflake.connector
import pandas as pd
from tabulate import tabulate
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fivetran API credentials
API_KEY = os.getenv('FIVETRAN_API_KEY')
API_SECRET = os.getenv('FIVETRAN_API_SECRET')

# Connector ID for the ProHandel connector
# Try both known connector IDs if the primary one fails
CONNECTOR_ID = os.getenv('FIVETRAN_CONNECTOR_ID', 'armed_unleaded')
ALTERNATE_CONNECTOR_IDS = ['armed_unleaded', 'look_frescoes']

# AWS Lambda function name
LAMBDA_FUNCTION_NAME = os.getenv('LAMBDA_FUNCTION_NAME', 'prohandel-fivetran-connector')

# Snowflake connection parameters
SNOWFLAKE_USER = os.getenv('SNOWFLAKE_USER')
SNOWFLAKE_PASSWORD = os.getenv('SNOWFLAKE_PASSWORD')
SNOWFLAKE_ACCOUNT = os.getenv('SNOWFLAKE_ACCOUNT')
SNOWFLAKE_WAREHOUSE = os.getenv('SNOWFLAKE_WAREHOUSE')
SNOWFLAKE_DATABASE = os.getenv('SNOWFLAKE_DATABASE')
SNOWFLAKE_SCHEMA = os.getenv('SNOWFLAKE_SCHEMA')

def check_credentials():
    """Check if all required credentials are set"""
    missing_vars = []
    
    if not API_KEY:
        missing_vars.append('FIVETRAN_API_KEY')
    if not API_SECRET:
        missing_vars.append('FIVETRAN_API_SECRET')
    if not CONNECTOR_ID:
        missing_vars.append('FIVETRAN_CONNECTOR_ID')
    if not SNOWFLAKE_USER or not SNOWFLAKE_PASSWORD or not SNOWFLAKE_ACCOUNT:
        missing_vars.append('SNOWFLAKE_CREDENTIALS')
    
    if missing_vars:
        print("\n⚠️ Missing environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease add these to your .env file and try again.")
        return False
    return True

def trigger_sync():
    """Trigger a manual sync for the specified connector"""
    url = f"https://api.fivetran.com/v1/connectors/{CONNECTOR_ID}/force"
    
    # Use basic authentication with API key and secret
    auth = (API_KEY, API_SECRET)
    
    print(f"Triggering manual sync for connector {CONNECTOR_ID}...")
    try:
        response = requests.post(url, auth=auth)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Sync triggered successfully!")
            print(f"Status: {result.get('code')}")
            print(f"Message: {result.get('message')}")
            return True
        else:
            print(f"❌ Failed to trigger sync. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error triggering sync: {str(e)}")
        return False

def check_sync_status():
    """Check the status of the connector"""
    global CONNECTOR_ID
    
    # Try the primary connector ID first
    connector_ids_to_try = [CONNECTOR_ID]
    
    # Add alternate IDs if they're not already the primary
    for alt_id in ALTERNATE_CONNECTOR_IDS:
        if alt_id != CONNECTOR_ID and alt_id not in connector_ids_to_try:
            connector_ids_to_try.append(alt_id)
    
    # Try each connector ID until one works
    for connector_id in connector_ids_to_try:
        url = f"https://api.fivetran.com/v1/connectors/{connector_id}"
        
        # Use basic authentication with API key and secret
        auth = (API_KEY, API_SECRET)
        
        print(f"Checking status for connector {connector_id}...")
        try:
            response = requests.get(url, auth=auth)
            
            if response.status_code == 200:
                # Update the global connector ID if we found a working one
                if connector_id != CONNECTOR_ID:
                    print(f"✅ Found working connector ID: {connector_id}")
                    print(f"Updating CONNECTOR_ID from {CONNECTOR_ID} to {connector_id}")
                    CONNECTOR_ID = connector_id
                
                result = response.json()
                connector_data = result.get('data', {})
                
                status = connector_data.get('status', {})
                setup_state = connector_data.get('setup_state')
                sync_state = connector_data.get('sync_state')
                
                print(f"Connector name: {connector_data.get('schema')}")
                print(f"Setup state: {setup_state}")
                print(f"Sync state: {sync_state}")
                
                if 'succeeded_at' in status:
                    succeeded_at = datetime.fromisoformat(status['succeeded_at'].replace('Z', '+00:00'))
                    print(f"Last successful sync: {succeeded_at}")
                
                if 'failed_at' in status:
                    failed_at = datetime.fromisoformat(status['failed_at'].replace('Z', '+00:00'))
                    print(f"Last failed sync: {failed_at}")
                    print(f"Failure message: {status.get('failure_message', 'No message')}")
                
                return connector_data
            else:
                print(f"❌ Failed to check status. Status code: {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"❌ Error checking sync status: {str(e)}")
    
    # If we get here, none of the connector IDs worked
    print("\n⚠️ None of the known connector IDs worked. Please check the Fivetran dashboard for the correct connector ID.")
    print("You can find this in the Fivetran UI under 'Connectors' > your connector > 'Setup' tab.")
    return None

def check_lambda_function():
    """Check the AWS Lambda function status"""
    print(f"\n=== Checking AWS Lambda Function: {LAMBDA_FUNCTION_NAME} ===\n")
    
    try:
        # Create Lambda client
        lambda_client = boto3.client('lambda', region_name='eu-central-1')
        
        # Get function details
        response = lambda_client.get_function(FunctionName=LAMBDA_FUNCTION_NAME)
        
        if response:
            config = response.get('Configuration', {})
            print(f"✅ Lambda function exists")
            print(f"Runtime: {config.get('Runtime')}")
            print(f"Handler: {config.get('Handler')}")
            print(f"Memory: {config.get('MemorySize')} MB")
            print(f"Timeout: {config.get('Timeout')} seconds")
            print(f"Last modified: {config.get('LastModified')}")
            
            # Test invoke the Lambda function with a test event
            print("\nInvoking Lambda function with test event...")
            test_event = {
                "operation": "test",
                "agent": "Fivetran AWS Lambda Connector/test_script",
                "secrets": {
                    "PROHANDEL_API_KEY": os.getenv('PROHANDEL_API_KEY'),
                    "PROHANDEL_API_SECRET": os.getenv('PROHANDEL_API_SECRET'),
                    "PROHANDEL_AUTH_URL": os.getenv('PROHANDEL_AUTH_URL'),
                    "PROHANDEL_API_URL": os.getenv('PROHANDEL_API_URL')
                }
            }
            
            invoke_response = lambda_client.invoke(
                FunctionName=LAMBDA_FUNCTION_NAME,
                InvocationType='RequestResponse',
                Payload=json.dumps(test_event)
            )
            
            # Parse the response
            payload = invoke_response['Payload'].read().decode('utf-8')
            status_code = invoke_response.get('StatusCode')
            
            if status_code == 200:
                print(f"✅ Lambda function invoked successfully (Status: {status_code})")
                try:
                    payload_json = json.loads(payload)
                    print(f"Response: {json.dumps(payload_json, indent=2)}")
                    return True
                except:
                    print(f"Response: {payload}")
                    return True
            else:
                print(f"❌ Lambda function invocation failed (Status: {status_code})")
                print(f"Response: {payload}")
                return False
        else:
            print(f"❌ Lambda function not found: {LAMBDA_FUNCTION_NAME}")
            return False
    except Exception as e:
        print(f"❌ Error checking Lambda function: {str(e)}")
        return False

def check_snowflake_data():
    """Check if data exists in Snowflake"""
    print(f"\n=== Checking Snowflake Data ===\n")
    
    try:
        # Use the correct account identifier from verify_snowflake_access.py
        account_name = "VRXDFZX-ZZ95717"
        print(f"Using Snowflake account: {account_name} (overriding env variable: {SNOWFLAKE_ACCOUNT})")
        
        # Try connecting with different account formats
        try:
            print(f"Attempting connection with account: {account_name}")
            conn = snowflake.connector.connect(
                user=SNOWFLAKE_USER,
                password=SNOWFLAKE_PASSWORD,
                account=account_name,
                warehouse=SNOWFLAKE_WAREHOUSE,
                database=SNOWFLAKE_DATABASE,
                schema=SNOWFLAKE_SCHEMA
            )
        except Exception as e:
            print(f"First connection attempt failed: {str(e)}")
            # Try with region suffix
            try:
                account_with_region = f"{account_name}.eu-central-1"
                print(f"Attempting connection with account: {account_with_region}")
                conn = snowflake.connector.connect(
                    user=SNOWFLAKE_USER,
                    password=SNOWFLAKE_PASSWORD,
                    account=account_with_region,
                    warehouse=SNOWFLAKE_WAREHOUSE,
                    database=SNOWFLAKE_DATABASE,
                    schema=SNOWFLAKE_SCHEMA
                )
            except Exception as e2:
                print(f"Second connection attempt failed: {str(e2)}")
                # Try with full URL format
                account_with_url = f"{account_name}.snowflakecomputing.com"
                print(f"Attempting connection with account: {account_with_url}")
                conn = snowflake.connector.connect(
                    user=SNOWFLAKE_USER,
                    password=SNOWFLAKE_PASSWORD,
                    account=account_with_url,
                    warehouse=SNOWFLAKE_WAREHOUSE,
                    database=SNOWFLAKE_DATABASE,
                    schema=SNOWFLAKE_SCHEMA
                )
        
        print(f"✅ Connected to Snowflake: {SNOWFLAKE_DATABASE}")
        
        # List schemas to find Fivetran schemas
        cursor = conn.cursor()
        cursor.execute(f"SHOW SCHEMAS IN {SNOWFLAKE_DATABASE}")
        schemas = cursor.fetchall()
        
        # Extract schema names
        schema_names = [row[1] for row in schemas]
        print(f"Found {len(schema_names)} schemas in {SNOWFLAKE_DATABASE}")
        
        # Look for Fivetran schemas
        fivetran_schemas = [s for s in schema_names if 'FIVETRAN' in s.upper() or 'ARMED_UNLEADED' in s.upper()]
        
        if fivetran_schemas:
            print(f"\nFound {len(fivetran_schemas)} Fivetran-related schemas:")
            for schema in fivetran_schemas:
                print(f"  - {schema}")
                
                # Check for tables in this schema
                cursor.execute(f"SHOW TABLES IN {SNOWFLAKE_DATABASE}.{schema}")
                tables = cursor.fetchall()
                
                if tables:
                    table_names = [row[1] for row in tables]
                    print(f"    Found {len(table_names)} tables:")
                    
                    # Check for data in each table
                    for table in table_names:
                        try:
                            cursor.execute(f"SELECT COUNT(*) FROM {SNOWFLAKE_DATABASE}.{schema}.{table}")
                            count = cursor.fetchone()[0]
                            print(f"      - {table}: {count} rows")
                            
                            # If table has data, show sample
                            if count > 0:
                                cursor.execute(f"SELECT * FROM {SNOWFLAKE_DATABASE}.{schema}.{table} LIMIT 3")
                                sample_data = cursor.fetchall()
                                columns = [desc[0] for desc in cursor.description]
                                
                                df = pd.DataFrame(sample_data, columns=columns)
                                print("\nSample data:")
                                print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
                                print("\n")
                        except Exception as e:
                            print(f"      - {table}: Error getting count - {str(e)}")
                else:
                    print(f"    No tables found in schema {schema}")
            return True
        else:
            print("❌ No Fivetran-related schemas found in Snowflake")
            print("This suggests that the Fivetran connector may not have synced any data yet.")
            return False
    except Exception as e:
        print(f"❌ Error connecting to Snowflake: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== ProHandel Integration Pipeline Check ===\n")
    
    # Check if all required credentials are set
    if not check_credentials():
        print("\nPlease update your .env file with the missing credentials and try again.")
        exit(1)
    
    # Step 1: Check AWS Lambda function
    lambda_ok = check_lambda_function()
    
    # Step 2: Check Fivetran connector status
    print("\n=== Checking Fivetran Connector Status ===\n")
    connector_data = check_sync_status()
    
    # Step 3: Trigger a manual sync if requested
    if lambda_ok and connector_data:
        trigger_now = input("\nDo you want to trigger a manual sync in Fivetran? (y/n): ").lower()
        if trigger_now == 'y':
            if trigger_sync():
                print("\nWaiting 15 seconds for sync to start...")
                time.sleep(15)
                check_sync_status()
                
                print("\n✅ Sync has been triggered. Check Fivetran dashboard for progress.")
                print("You can also check CloudWatch logs for Lambda function activity.")
            else:
                print("❌ Failed to trigger sync. Please check your API credentials and connector ID.")
    
    # Step 4: Check Snowflake for data
    check_snowflake = input("\nDo you want to check Snowflake for ProHandel data? (y/n): ").lower()
    if check_snowflake == 'y':
        check_snowflake_data()
    
    print("\n=== Integration Pipeline Check Complete ===\n")
    print("Summary:")
    print(f"  - AWS Lambda Function: {'✅ OK' if lambda_ok else '❌ Issues detected'}")
    print(f"  - Fivetran Connector: {'✅ OK' if connector_data else '❌ Issues detected'}")
    
    if connector_data:
        sync_state = connector_data.get('sync_state', 'unknown')
        print(f"  - Fivetran Sync State: {sync_state}")
    
    print("\nNext steps:")
    print("  1. Monitor CloudWatch logs for Lambda function activity")
    print("  2. Check Fivetran dashboard for sync progress")
    print("  3. Verify data in Snowflake after sync completes")
