#!/usr/bin/env python3
"""
Update Fivetran integration configuration to use Snowflake.
"""

import os
import json
import argparse

def load_snowflake_config(config_path):
    """Load Snowflake configuration from a JSON file."""
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config

def update_fivetran_config(fivetran_config_path, snowflake_config, fivetran_api_key=None, fivetran_api_secret=None):
    """Update Fivetran integration configuration to use Snowflake."""
    # Load existing Fivetran configuration
    with open(fivetran_config_path, 'r') as f:
        fivetran_config = json.load(f)
    
    # Update database connection to use Snowflake
    fivetran_config['database'] = {
        'type': 'snowflake',
        'account': snowflake_config['account'],
        'username': 'FIVETRAN_SERVICE',
        'password': '{{ env_var("FIVETRAN_SERVICE_PASSWORD") }}',
        'database': 'MERCURIOS_DATA',
        'schema': 'RAW',
        'warehouse': 'MERCURIOS_LOADING_WH',
        'role': 'MERCURIOS_FIVETRAN_SERVICE'
    }
    
    # Update Fivetran API credentials if provided
    if fivetran_api_key and fivetran_api_secret:
        fivetran_config['fivetran']['api_key'] = fivetran_api_key
        fivetran_config['fivetran']['api_secret'] = fivetran_api_secret
    
    # Write updated configuration
    with open(fivetran_config_path, 'w') as f:
        json.dump(fivetran_config, f, indent=2)
    
    print(f"Updated Fivetran configuration at {fivetran_config_path}")

def main():
    parser = argparse.ArgumentParser(description='Update Fivetran integration configuration to use Snowflake')
    parser.add_argument('--snowflake-config', default='snowflake_config.json', help='Path to Snowflake configuration file')
    parser.add_argument('--fivetran-config', default='fivetran_integration/config.json', help='Path to Fivetran integration configuration file')
    parser.add_argument('--fivetran-api-key', help='Fivetran API key')
    parser.add_argument('--fivetran-api-secret', help='Fivetran API secret')
    args = parser.parse_args()
    
    # Load Snowflake configuration
    snowflake_config = load_snowflake_config(args.snowflake_config)
    
    # Update Fivetran configuration
    update_fivetran_config(
        args.fivetran_config,
        snowflake_config,
        args.fivetran_api_key,
        args.fivetran_api_secret
    )

if __name__ == "__main__":
    main()
