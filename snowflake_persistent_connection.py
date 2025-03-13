#!/usr/bin/env python
"""
Snowflake Persistent Connection Script

This script establishes a persistent connection to Snowflake and provides
a command-line interface to run SQL queries without requiring repeated MFA.
"""

import os
import sys
import time
import argparse
import getpass
from datetime import datetime
import snowflake.connector
from snowflake.connector.errors import ProgrammingError
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_connection(account, user, password=None, warehouse=None, database=None, role=None):
    """Establish a connection to Snowflake."""
    conn_params = {
        'account': account,
        'user': user,
    }
    
    # Use password if provided, otherwise use browser authentication
    if password:
        conn_params['password'] = password
    else:
        conn_params['authenticator'] = 'externalbrowser'  # This will use your browser for authentication
    
    if warehouse:
        conn_params['warehouse'] = warehouse
    
    if database:
        conn_params['database'] = database
    
    if role:
        conn_params['role'] = role
    
    print(f"Connecting to Snowflake as {user}...")
    return snowflake.connector.connect(**conn_params)

def execute_query(conn, query, verbose=True):
    """Execute a SQL query and return the results."""
    try:
        cursor = conn.cursor()
        if verbose:
            print(f"Executing query: {query[:100]}..." if len(query) > 100 else f"Executing query: {query}")
        cursor.execute(query)
        
        # Check if there are results to fetch
        if cursor.description:
            results = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            df = pd.DataFrame(results, columns=columns)
            return df
        else:
            if verbose:
                print("Query executed successfully (no results to fetch)")
            return None
    except ProgrammingError as e:
        print(f"Error executing query: {e}")
        return None

def interactive_mode(conn):
    """Run an interactive SQL session."""
    print("\nEntering interactive mode. Type 'exit' or 'quit' to exit.")
    print("Type 'help' for available commands.")
    
    history = []
    
    while True:
        try:
            query = input("\nSQL> ")
            
            if query.lower() in ('exit', 'quit'):
                print("Exiting interactive mode.")
                break
            
            if query.lower() == 'help':
                print("\nAvailable commands:")
                print("  exit, quit - Exit interactive mode")
                print("  help - Show this help message")
                print("  history - Show command history")
                print("  clear - Clear the screen")
                print("  status - Show connection status")
                print("  use warehouse <name> - Switch to a different warehouse")
                print("  use database <name> - Switch to a different database")
                print("  use role <name> - Switch to a different role")
                continue
            
            if query.lower() == 'history':
                for i, cmd in enumerate(history):
                    print(f"{i+1}: {cmd}")
                continue
            
            if query.lower() == 'clear':
                os.system('cls' if os.name == 'nt' else 'clear')
                continue
            
            if query.lower() == 'status':
                status = execute_query(conn, "SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_SCHEMA()")
                print("\nConnection Status:")
                print(f"User: {status.iloc[0, 0]}")
                print(f"Role: {status.iloc[0, 1]}")
                print(f"Warehouse: {status.iloc[0, 2]}")
                print(f"Database: {status.iloc[0, 3]}")
                print(f"Schema: {status.iloc[0, 4]}")
                continue
            
            if query.lower().startswith('use warehouse '):
                warehouse = query[14:].strip()
                execute_query(conn, f"USE WAREHOUSE {warehouse}")
                print(f"Switched to warehouse: {warehouse}")
                history.append(query)
                continue
            
            if query.lower().startswith('use database '):
                database = query[13:].strip()
                execute_query(conn, f"USE DATABASE {database}")
                print(f"Switched to database: {database}")
                history.append(query)
                continue
            
            if query.lower().startswith('use role '):
                role = query[9:].strip()
                execute_query(conn, f"USE ROLE {role}")
                print(f"Switched to role: {role}")
                history.append(query)
                continue
            
            # Execute the SQL query
            if query.strip():
                start_time = time.time()
                result = execute_query(conn, query)
                end_time = time.time()
                
                if result is not None:
                    print(f"\nResults ({len(result)} rows, {end_time - start_time:.2f} seconds):")
                    print(result.to_string(index=False))
                else:
                    print(f"Query completed in {end_time - start_time:.2f} seconds")
                
                history.append(query)
        
        except KeyboardInterrupt:
            print("\nOperation cancelled by user. Type 'exit' to quit.")
        except Exception as e:
            print(f"Error: {e}")

def run_file(conn, file_path, verbose=True):
    """Execute SQL commands from a file."""
    try:
        with open(file_path, 'r') as f:
            sql_content = f.read()
        
        # Split the SQL file into individual statements
        statements = sql_content.split(';')
        
        results = []
        for stmt in statements:
            stmt = stmt.strip()
            if stmt:
                if verbose:
                    print(f"Executing: {stmt[:100]}..." if len(stmt) > 100 else f"Executing: {stmt}")
                result = execute_query(conn, stmt, verbose=False)
                if result is not None:
                    results.append(result)
        
        return results
    
    except Exception as e:
        print(f"Error executing SQL file: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Snowflake Persistent Connection Tool')
    parser.add_argument('--account', help='Snowflake account identifier')
    parser.add_argument('--user', help='Snowflake username')
    parser.add_argument('--warehouse', help='Snowflake warehouse')
    parser.add_argument('--database', help='Snowflake database')
    parser.add_argument('--role', help='Snowflake role')
    parser.add_argument('--file', help='SQL file to execute')
    parser.add_argument('--query', help='SQL query to execute')
    parser.add_argument('--output', help='Output file for query results (CSV format)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--password', help='Snowflake password')
    
    args = parser.parse_args()
    
    # Get connection parameters from arguments or environment variables
    account = args.account or os.getenv('SNOWFLAKE_ACCOUNT') or input("Snowflake Account: ")
    user = args.user or os.getenv('SNOWFLAKE_USER') or input("Snowflake Username: ")
    warehouse = args.warehouse or os.getenv('SNOWFLAKE_WAREHOUSE')
    database = args.database or os.getenv('SNOWFLAKE_DATABASE')
    role = args.role or os.getenv('SNOWFLAKE_ROLE')
    password = args.password or os.getenv('SNOWFLAKE_PASSWORD')
    
    if not password:
        password = getpass.getpass("Snowflake Password: ")
    
    # Establish connection
    conn = get_connection(account, user, password=password, warehouse=warehouse, database=database, role=role)
    
    try:
        if args.file:
            # Execute SQL from file
            results = run_file(conn, args.file, verbose=args.verbose)
            if results and args.output:
                # Combine all result DataFrames
                all_results = pd.concat(results, ignore_index=True)
                all_results.to_csv(args.output, index=False)
                print(f"Results saved to {args.output}")
        
        elif args.query:
            # Execute a single query
            result = execute_query(conn, args.query, verbose=args.verbose)
            if result is not None and args.output:
                result.to_csv(args.output, index=False)
                print(f"Results saved to {args.output}")
        
        else:
            # Enter interactive mode
            interactive_mode(conn)
    
    finally:
        # Close the connection
        conn.close()
        print("Connection closed.")

if __name__ == "__main__":
    main()
