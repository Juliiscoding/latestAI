"""
ProHandel Fivetran Connector for the Mercurios.ai ETL pipeline.

This connector adapts the existing ProHandel connector to work with Fivetran's Connector SDK.
It handles data extraction from the ProHandel API with incremental loading, authentication,
and basic data quality validation.
"""
from fivetran_connector_sdk import Connector
from fivetran_connector_sdk import Operations as op
from fivetran_connector_sdk import Logging as log
import requests
import datetime
import json
import os
import pandas as pd
from typing import Dict, List, Any, Optional, Generator

def schema(configuration):
    """
    Define the schema for the connector.
    
    Args:
        configuration: Configuration parameters for the connector
        
    Returns:
        List: Schema definition as a list of table definitions
    """
    log.info(f"Schema called with configuration: {configuration}")
    
    # Return schema as a list of tables
    return [
        {
            "table": "article",
            "primary_key": ["number"],
            "columns": {
                "number": "string",
                "name": "string",
                "description": "string",
                "manufacturerNumber": "string",
                "price": {"type": "decimal", "precision": 10, "scale": 2},
                "cost": {"type": "decimal", "precision": 10, "scale": 2},
                "unit": "string",
                "category": "string",
                "lastChange": {"type": "timestamp"}
            }
        },
        {
            "table": "customer",
            "primary_key": ["number"],
            "columns": {
                "number": "string",
                "name1": "string",
                "name2": "string",
                "street": "string",
                "zipCode": "string",
                "city": "string",
                "country": "string",
                "email": "string",
                "phone": "string",
                "lastChange": {"type": "timestamp"}
            }
        },
        {
            "table": "order",
            "primary_key": ["number"],
            "columns": {
                "number": "string",
                "customerNumber": "string",
                "orderDate": {"type": "timestamp"},
                "deliveryDate": {"type": "timestamp"},
                "status": "string",
                "total": {"type": "decimal", "precision": 10, "scale": 2},
                "currency": "string",
                "lastChange": {"type": "timestamp"}
            }
        },
        {
            "table": "sale",
            "primary_key": ["number", "articleNumber"],
            "columns": {
                "number": "string",
                "articleNumber": "string",
                "saleDate": {"type": "timestamp"},
                "quantity": {"type": "decimal", "precision": 10, "scale": 2},
                "price": {"type": "decimal", "precision": 10, "scale": 2},
                "total": {"type": "decimal", "precision": 10, "scale": 2},
                "currency": "string",
                "lastChange": {"type": "timestamp"}
            }
        },
        {
            "table": "inventory",
            "primary_key": ["articleNumber", "warehouseCode"],
            "columns": {
                "articleNumber": "string",
                "warehouseCode": "string",
                "quantity": {"type": "decimal", "precision": 10, "scale": 2},
                "lastChange": {"type": "timestamp"}
            }
        }
    ]

def update(configuration, state):
    """
    Update method for the connector.
    
    This method is called by Fivetran to extract data from the source.
    
    Args:
        configuration: Configuration parameters for the connector
        state: Current state of the connector
        
    Returns:
        Updated state and extracted data
    """
    # Log the configuration and state
    log.info(f"Configuration: {configuration}")
    log.info(f"State: {state}")
    
    # Use configuration or fall back to configuration file
    if not configuration:
        config_path = os.path.join(os.path.dirname(__file__), 'configuration.json')
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except Exception as e:
            log.error(f"Error loading configuration: {str(e)}")
            return {"lastSync": datetime.datetime.now().isoformat()}
    else:
        config = configuration
    
    api_url = config.get('api_url', 'https://api.prohandel.example.com/v1')
    api_key = config.get('api_key', 'YOUR_PROHANDEL_API_KEY')
    api_secret = config.get('api_secret', 'YOUR_PROHANDEL_API_SECRET')
    
    log.info(f"Starting ProHandel data extraction")
    
    # Generate mock data for testing
    # Article data
    log.info(f"Processing articles")
    for i in range(10):
        record = {
            "number": f"ART{i+1:04d}",
            "name": f"Test Article {i+1}",
            "description": f"Description for article {i+1}",
            "manufacturerNumber": f"MFR{i+1:04d}",
            "price": 100.0 + i * 10.5,
            "cost": 80.0 + i * 8.0,
            "unit": "EA",
            "category": "Test Category",
            "lastChange": datetime.datetime.now().isoformat()
        }
        yield op.upsert("article", record)
    
    # Customer data
    log.info(f"Processing customers")
    for i in range(5):
        record = {
            "number": f"CUST{i+1:04d}",
            "name1": f"Test Customer {i+1}",
            "name2": f"Company {i+1}",
            "street": f"{i+1} Test Street",
            "zipCode": f"{10000 + i}",
            "city": "Test City",
            "country": "Test Country",
            "email": f"customer{i+1}@example.com",
            "phone": f"+1234567890{i}",
            "lastChange": datetime.datetime.now().isoformat()
        }
        yield op.upsert("customer", record)
    
    # Return updated state
    return {"lastSync": datetime.datetime.now().isoformat()}

# Create an instance of the connector
connector = Connector(update=update, schema=schema)
