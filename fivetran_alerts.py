#!/usr/bin/env python3
"""
Fivetran Monitoring Alerts
This script checks for issues with Fivetran connectors and sends alerts
"""

import json
import snowflake.connector
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from tabulate import tabulate

# Alert thresholds
SYNC_DELAY_THRESHOLD = 2  # Multiple of sync frequency
ERROR_COUNT_THRESHOLD = 3  # Number of errors in the last 24 hours

def check_alerts():
    """Check for issues with Fivetran connectors"""
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
        
        # Check if the FIVETRAN_LOG schema exists
        cursor.execute("SHOW SCHEMAS LIKE 'FIVETRAN_LOG' IN DATABASE MERCURIOS_DATA")
        schemas = cursor.fetchall()
        
        if not schemas:
            print("FIVETRAN_LOG schema does not exist. The Quickstart Data Model may not be deployed.")
            sys.exit(0)
        
        alerts = []
        
        # 1. Check for delayed syncs
        print("Checking for delayed syncs...")
        try:
            cursor.execute(f"""
                SELECT 
                    connector_name,
                    destination_name,
                    connector_type,
                    status,
                    last_successful_sync,
                    DATEDIFF('hour', last_successful_sync, CURRENT_TIMESTAMP()) as hours_since_last_sync,
                    sync_frequency,
                    'Delayed Sync' as alert_type
                FROM MERCURIOS_DATA.FIVETRAN_LOG.CONNECTOR_STATUS
                WHERE 
                    DATEDIFF('hour', last_successful_sync, CURRENT_TIMESTAMP()) > sync_frequency * {SYNC_DELAY_THRESHOLD}
                    AND is_paused = FALSE
                ORDER BY hours_since_last_sync DESC
            """)
            delayed_syncs = cursor.fetchall()
            
            if delayed_syncs:
                print(f"Found {len(delayed_syncs)} delayed syncs")
                alerts.extend(delayed_syncs)
            else:
                print("No delayed syncs found")
        except Exception as e:
            print(f"Error checking for delayed syncs: {e}")
        
        # 2. Check for connectors with errors
        print("Checking for connectors with errors...")
        try:
            cursor.execute(f"""
                WITH recent_errors AS (
                    SELECT 
                        connector_name,
                        COUNT(*) as error_count
                    FROM MERCURIOS_DATA.FIVETRAN_LOG.ERROR_REPORTING
                    WHERE created_at >= DATEADD('day', -1, CURRENT_TIMESTAMP())
                    GROUP BY 1
                    HAVING COUNT(*) >= {ERROR_COUNT_THRESHOLD}
                )
                SELECT 
                    cs.connector_name,
                    cs.destination_name,
                    cs.connector_type,
                    cs.status,
                    cs.last_successful_sync,
                    DATEDIFF('hour', cs.last_successful_sync, CURRENT_TIMESTAMP()) as hours_since_last_sync,
                    cs.sync_frequency,
                    'Frequent Errors' as alert_type
                FROM MERCURIOS_DATA.FIVETRAN_LOG.CONNECTOR_STATUS cs
                JOIN recent_errors re ON cs.connector_name = re.connector_name
                ORDER BY hours_since_last_sync DESC
            """)
            error_connectors = cursor.fetchall()
            
            if error_connectors:
                print(f"Found {len(error_connectors)} connectors with frequent errors")
                alerts.extend(error_connectors)
            else:
                print("No connectors with frequent errors found")
        except Exception as e:
            print(f"Error checking for connectors with errors: {e}")
        
        # 3. Check for connectors with failed status
        print("Checking for connectors with failed status...")
        try:
            cursor.execute("""
                SELECT 
                    connector_name,
                    destination_name,
                    connector_type,
                    status,
                    last_successful_sync,
                    DATEDIFF('hour', last_successful_sync, CURRENT_TIMESTAMP()) as hours_since_last_sync,
                    sync_frequency,
                    'Failed Status' as alert_type
                FROM MERCURIOS_DATA.FIVETRAN_LOG.CONNECTOR_STATUS
                WHERE 
                    status != 'connected'
                    AND is_paused = FALSE
                ORDER BY connector_name
            """)
            failed_connectors = cursor.fetchall()
            
            if failed_connectors:
                print(f"Found {len(failed_connectors)} connectors with failed status")
                alerts.extend(failed_connectors)
            else:
                print("No connectors with failed status found")
        except Exception as e:
            print(f"Error checking for connectors with failed status: {e}")
        
        # Close the connection
        cursor.close()
        conn.close()
        
        # Generate report
        if alerts:
            print(f"\nFound {len(alerts)} total alerts")
            headers = ["Connector", "Destination", "Type", "Status", "Last Sync", "Hours Since", "Frequency", "Alert Type"]
            print(tabulate(alerts, headers=headers, tablefmt="grid"))
            
            # In a real-world scenario, you would send these alerts via email, Slack, etc.
            # For now, we'll just print them
            print("\nIn a production environment, these alerts would be sent via email or Slack.")
            print("To implement email alerts, configure the send_email function in this script.")
        else:
            print("\nNo alerts found. All connectors are healthy!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def send_email(subject, body, recipients):
    """Send an email alert"""
    # This is a placeholder function. In a real-world scenario, you would configure
    # this with your SMTP server details and credentials.
    print(f"Would send email with subject '{subject}' to {recipients}")
    print(f"Body: {body}")
    
    # Example implementation (commented out):
    """
    sender = "alerts@yourdomain.com"
    password = "your_password"
    
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'html'))
    
    server = smtplib.SMTP('smtp.yourdomain.com', 587)
    server.starttls()
    server.login(sender, password)
    server.send_message(msg)
    server.quit()
    """

if __name__ == "__main__":
    print(f"Fivetran Monitoring Alerts - {datetime.now()}")
    print("-" * 80)
    check_alerts()
