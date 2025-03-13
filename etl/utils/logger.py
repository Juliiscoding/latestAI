"""
Logging utility for the Mercurios.ai ETL pipeline.
"""
import os
import sys
import logging
from pathlib import Path

from etl.config.config import LOG_CONFIG

# Check if running in AWS Lambda environment
is_lambda = os.environ.get('AWS_LAMBDA_FUNCTION_NAME') is not None

# Modify log path for Lambda environment
if is_lambda:
    # In Lambda, we can only write to /tmp
    log_file = os.path.join('/tmp', 'mercurios_etl.log')
else:
    # Use the configured log file for non-Lambda environments
    log_file = LOG_CONFIG["file"]

# Create logs directory if it doesn't exist and not in Lambda
log_dir = Path(log_file).parent
if not is_lambda or (is_lambda and str(log_dir).startswith('/tmp')):
    log_dir.mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_CONFIG["level"]),
    format=LOG_CONFIG["format"],
    datefmt=LOG_CONFIG["date_format"],
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Create logger
logger = logging.getLogger("mercurios_etl")
logger.setLevel(getattr(logging, LOG_CONFIG["level"]))

# Add console handler for debugging
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(getattr(logging, LOG_CONFIG["level"]))
console_handler.setFormatter(logging.Formatter(LOG_CONFIG["format"], datefmt=LOG_CONFIG["date_format"]))
logger.addHandler(console_handler)

# Add file handler if not running in Lambda or using /tmp in Lambda
try:
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, LOG_CONFIG["level"]))
    file_handler.setFormatter(logging.Formatter(LOG_CONFIG["format"], datefmt=LOG_CONFIG["date_format"]))
    logger.addHandler(file_handler)
    logger.info(f"Logging to file: {log_file}")

except Exception as e:
    logger.warning(f"Could not set up file logging: {str(e)}")
    logger.info("Continuing with console logging only")

__all__ = ["logger"]
