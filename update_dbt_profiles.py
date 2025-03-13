#!/usr/bin/env python3
"""
Update dbt profiles.yml to use Snowflake as the target database.
"""

import os
import json
import yaml
import argparse

def load_snowflake_config(config_path):
    """Load Snowflake configuration from a JSON file."""
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config

def update_dbt_profiles(profiles_path, snowflake_config, password=None):
    """Update dbt profiles.yml to use Snowflake."""
    # Create profiles directory if it doesn't exist
    os.makedirs(os.path.dirname(profiles_path), exist_ok=True)
    
    # Create new profiles configuration
    profiles = {
        'prohandel': {
            'target': 'dev',
            'outputs': {
                'dev': {
                    'type': 'snowflake',
                    'account': snowflake_config['account'],
                    'user': snowflake_config['username'],
                    'password': password or snowflake_config['password'],
                    'role': 'MERCURIOS_DEVELOPER',
                    'database': 'MERCURIOS_DATA',
                    'warehouse': 'MERCURIOS_DEV_WH',
                    'schema': 'STANDARD',
                    'threads': 4,
                    'client_session_keep_alive': True
                },
                'prod': {
                    'type': 'snowflake',
                    'account': snowflake_config['account'],
                    'user': 'APP_SERVICE',
                    'password': '{{ env_var("DBT_PROD_PASSWORD") }}',
                    'role': 'MERCURIOS_APP_SERVICE',
                    'database': 'MERCURIOS_DATA',
                    'warehouse': 'MERCURIOS_ANALYTICS_WH',
                    'schema': 'ANALYTICS',
                    'threads': 8,
                    'client_session_keep_alive': True
                }
            }
        }
    }
    
    # Write to profiles.yml
    with open(profiles_path, 'w') as f:
        yaml.dump(profiles, f, default_flow_style=False)
    
    print(f"Updated dbt profiles at {profiles_path}")

def main():
    parser = argparse.ArgumentParser(description='Update dbt profiles.yml to use Snowflake')
    parser.add_argument('--config', default='snowflake_config.json', help='Path to Snowflake configuration file')
    parser.add_argument('--profiles', default='dbt_prohandel/profiles.yml', help='Path to dbt profiles.yml')
    parser.add_argument('--password', help='Snowflake password (if not in config file)')
    args = parser.parse_args()
    
    # Load Snowflake configuration
    snowflake_config = load_snowflake_config(args.config)
    
    # Update dbt profiles
    update_dbt_profiles(args.profiles, snowflake_config, args.password)

if __name__ == "__main__":
    main()
