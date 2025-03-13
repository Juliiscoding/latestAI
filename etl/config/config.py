"""
Configuration module for the Mercurios.ai ETL pipeline.
"""
import os
from typing import Dict, Any

from dotenv import load_dotenv

# Load environment variables from .env file with override to ensure .env values take precedence
load_dotenv(override=True)

# API Configuration
API_CONFIG = {
    "api_key": os.getenv("PROHANDEL_API_KEY"),
    "api_secret": os.getenv("PROHANDEL_API_SECRET"),
    "auth_url": os.getenv("PROHANDEL_AUTH_URL", "https://auth.prohandel.cloud/api/v4"),
    "api_url": os.getenv("PROHANDEL_API_URL", "https://api.prohandel.de/api/v2"),
    "token_expiry_buffer": int(os.getenv("TOKEN_EXPIRY_BUFFER", "300")),  # 5 minutes in seconds
    "token_refresh_minutes": int(os.getenv("TOKEN_REFRESH_MINUTES", "55")),  # Refresh token after 55 minutes
}

# API Endpoints Configuration
API_ENDPOINTS = {
    "article": {
        "endpoint": "/article",
        "batch_size": 100,
        "timestamp_field": "lastChange",
        "schema_file": "article.json",
        "id_field": "id",
    },
    "customer": {
        "endpoint": "/customer",
        "batch_size": 100,
        "timestamp_field": "lastChange",
        "schema_file": "customer.json",
        "id_field": "id",
    },
    "order": {
        "endpoint": "/order",
        "batch_size": 50,
        "timestamp_field": "lastChange",
        "schema_file": "order.json",
        "id_field": "id",
    },
    "sale": {
        "endpoint": "/sale",
        "batch_size": 200,
        "timestamp_field": "date",
        "schema_file": "sale.json",
        "id_field": "id",
    },
    "inventory": {
        "endpoint": "/inventory",
        "batch_size": 200,
        "timestamp_field": "lastChange",
        "schema_file": "inventory.json",
        "id_field": "id",
    },
    "branch": {
        "endpoint": "/branch",
        "batch_size": 50,
        "timestamp_field": "lastChange",
        "schema_file": "branch.json",
        "id_field": "id",
    },
    "supplier": {
        "endpoint": "/supplier",
        "batch_size": 100,
        "timestamp_field": "lastChange",
        "schema_file": "supplier.json",
        "id_field": "id",
    },
    "category": {
        "endpoint": "/category",
        "batch_size": 100,
        "timestamp_field": "lastChange",
        "schema_file": "category.json",
        "id_field": "id",
    },
    "staff": {
        "endpoint": "/staff",
        "batch_size": 50,
        "timestamp_field": "lastChange",
        "schema_file": "staff.json",
        "id_field": "id",
    },
    "shop": {
        "endpoint": "/shop",
        "batch_size": 50,
        "timestamp_field": "lastChange",
        "schema_file": "shop.json",
        "id_field": "id",
    },
    "articlesize": {
        "endpoint": "/articlesize",
        "batch_size": 100,
        "timestamp_field": "lastChange",
        "schema_file": "articlesize.json",
        "id_field": "id",
    },
    "country": {
        "endpoint": "/country",
        "batch_size": 50,
        "timestamp_field": "lastChange",
        "schema_file": "country.json",
        "id_field": "id",
    },
    "currency": {
        "endpoint": "/currency",
        "batch_size": 50,
        "timestamp_field": "lastChange",
        "schema_file": "currency.json",
        "id_field": "id",
    },
    "invoice": {
        "endpoint": "/invoice",
        "batch_size": 100,
        "timestamp_field": "lastChange",
        "schema_file": "invoice.json",
        "id_field": "id",
    },
    "payment": {
        "endpoint": "/payment",
        "batch_size": 100,
        "timestamp_field": "lastChange",
        "schema_file": "payment.json",
        "id_field": "id",
    },
    "season": {
        "endpoint": "/season",
        "batch_size": 50,
        "timestamp_field": "lastChange",
        "schema_file": "season.json",
        "id_field": "id",
    },
    "size": {
        "endpoint": "/size",
        "batch_size": 50,
        "timestamp_field": "lastChange",
        "schema_file": "size.json",
        "id_field": "id",
    },
    "voucher": {
        "endpoint": "/voucher",
        "batch_size": 100,
        "timestamp_field": "lastChange",
        "schema_file": "voucher.json",
        "id_field": "id",
    },
}

# Database Configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "mercurios"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
    "schema": os.getenv("DB_SCHEMA", "prohandel"),
    "pool_size": int(os.getenv("DB_POOL_SIZE", "5")),
    "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "10")),
    "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
    "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "1800")),
}

# Logging Configuration
# Check if running in AWS Lambda environment
is_lambda = os.environ.get('AWS_LAMBDA_FUNCTION_NAME') is not None

# Use /tmp for logs in Lambda environment
default_log_file = "/tmp/etl.log" if is_lambda else "logs/etl.log"

LOG_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S",
    "file": os.getenv("LOG_FILE", default_log_file),
    "rotation": os.getenv("LOG_ROTATION", "1 day"),
    "retention": os.getenv("LOG_RETENTION", "30 days"),
}

# ETL Configuration
ETL_CONFIG = {
    "batch_size": int(os.getenv("ETL_BATCH_SIZE", "100")),
    "max_retries": int(os.getenv("ETL_MAX_RETRIES", "3")),
    "retry_delay": int(os.getenv("ETL_RETRY_DELAY", "5")),
    "incremental_load": os.getenv("ETL_INCREMENTAL_LOAD", "True").lower() == "true",
    "data_retention_days": int(os.getenv("DATA_RETENTION_DAYS", "90")),
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
    "log_file": os.getenv("LOG_FILE", default_log_file),  # Use the same default log file as LOG_CONFIG
    "schema_validation": os.getenv("SCHEMA_VALIDATION", "True").lower() == "true",
}

# Fivetran Lambda Configuration
LAMBDA_CONFIG = {
    "memory_size": int(os.getenv("LAMBDA_MEMORY_SIZE", "256")),
    "timeout": int(os.getenv("LAMBDA_TIMEOUT", "180")),
    "runtime": os.getenv("LAMBDA_RUNTIME", "python3.9"),
    "handler": os.getenv("LAMBDA_HANDLER", "lambda_function.lambda_handler"),
    "role": os.getenv("LAMBDA_ROLE", "arn:aws:iam::689864027744:role/lambda-prohandel-connector"),
    "function_name": os.getenv("LAMBDA_FUNCTION_NAME", "prohandel-fivetran-connector"),
    "region": os.getenv("AWS_REGION", "eu-central-1"),
}
