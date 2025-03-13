"""
Database utility for the Mercurios.ai ETL pipeline.
This module provides database functionality for local development and dummy implementations
for AWS Lambda environment where database connections are not needed for the Fivetran connector.
"""
import os
from datetime import datetime, timedelta
from etl.utils.logger import logger

# Check if running in AWS Lambda environment
is_lambda = os.environ.get('AWS_LAMBDA_FUNCTION_NAME') is not None

# Only import SQLAlchemy if not running in Lambda
if not is_lambda:
    try:
        from sqlalchemy import create_engine, MetaData
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker
        from etl.config.config import DB_CONFIG

        # Create database URL
        DB_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

        # Create engine
        engine = create_engine(DB_URL, echo=False)

        # Create session factory
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        # Create base class for models
        Base = declarative_base()

        # Create metadata object
        metadata = MetaData()
    except ImportError:
        logger.warning("SQLAlchemy not available, using dummy implementations")
        # Provide dummy objects
        engine = None
        SessionLocal = None
        Base = None
        metadata = None
else:
    logger.info("Running in Lambda environment, using dummy database implementations")
    # Provide dummy objects for Lambda environment
    engine = None
    SessionLocal = None
    Base = None
    metadata = None

def get_db_session():
    """Get a database session."""
    if is_lambda:
        logger.info("Database sessions not available in Lambda environment")
        return None
    
    if SessionLocal is None:
        logger.warning("SessionLocal not initialized, cannot create database session")
        return None
        
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize the database."""
    if is_lambda:
        logger.info("Database initialization not needed in Lambda environment")
        return
        
    if Base is None or engine is None:
        logger.warning("Base or engine not initialized, cannot initialize database")
        return
        
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

def get_last_timestamp(table_name, timestamp_field):
    """
    Get the last timestamp from a table for incremental loading.
    In Lambda environment, returns a dummy timestamp 30 days ago.
    
    Args:
        table_name (str): The name of the table
        timestamp_field (str): The name of the timestamp field
        
    Returns:
        datetime: The last timestamp or None if the table is empty
    """
    if is_lambda:
        # For Lambda, return a timestamp 30 days ago to ensure we get some data
        logger.info(f"Using dummy timestamp for {table_name}.{timestamp_field} in Lambda environment")
        return datetime.now() - timedelta(days=30)
        
    if engine is None:
        logger.warning("Database engine not initialized, returning dummy timestamp")
        return datetime.now() - timedelta(days=30)
        
    try:
        with engine.connect() as conn:
            result = conn.execute(
                f"SELECT MAX({timestamp_field}) FROM {table_name}"
            ).fetchone()
            return result[0] if result and result[0] else None
    except Exception as e:
        logger.error(f"Error getting last timestamp from {table_name}: {e}")
        return None
