#!/usr/bin/env python
"""
Main script to run the Mercurios.ai ETL pipeline.
"""
import argparse
import json
import sys
import time
from typing import List, Optional

from etl.etl_orchestrator import etl_orchestrator
from etl.utils.logger import logger
from etl.config.config import API_ENDPOINTS

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the Mercurios.ai ETL pipeline")
    
    parser.add_argument(
        "--entities",
        type=str,
        nargs="+",
        help="Entities to process (space-separated, e.g., 'article customer')",
    )
    
    parser.add_argument(
        "--validate",
        action="store_true",
        default=True,
        help="Validate data against schemas",
    )
    
    parser.add_argument(
        "--no-validate",
        action="store_false",
        dest="validate",
        help="Skip data validation",
    )
    
    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Use incremental loading",
    )
    
    parser.add_argument(
        "--full",
        action="store_false",
        dest="incremental",
        help="Use full loading (not incremental)",
    )
    
    parser.add_argument(
        "--setup-db",
        action="store_true",
        help="Set up database schema",
    )
    
    parser.add_argument(
        "--generate-schemas",
        action="store_true",
        help="Generate JSON schemas from sample data",
    )
    
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show ETL status",
    )
    
    return parser.parse_args()

def validate_entities(entities: Optional[List[str]]) -> List[str]:
    """Validate entity names."""
    if not entities:
        return list(API_ENDPOINTS.keys())
    
    valid_entities = []
    invalid_entities = []
    
    for entity in entities:
        if entity in API_ENDPOINTS:
            valid_entities.append(entity)
        else:
            invalid_entities.append(entity)
    
    if invalid_entities:
        logger.warning(f"Unknown entities: {', '.join(invalid_entities)}")
        logger.info(f"Available entities: {', '.join(API_ENDPOINTS.keys())}")
    
    return valid_entities

def show_etl_status():
    """Show ETL status."""
    status_records = etl_orchestrator.get_etl_status()
    
    if not status_records:
        logger.info("No ETL status records found")
        return
    
    logger.info(f"ETL Status ({len(status_records)} entities):")
    logger.info("-" * 80)
    
    for record in status_records:
        entity_name = record["entity_name"]
        status = record["status"]
        record_count = record["record_count"] or 0
        last_extraction = record["last_extraction_time"]
        last_timestamp = record["last_record_timestamp"]
        
        logger.info(f"Entity: {entity_name}")
        logger.info(f"  Status: {status}")
        logger.info(f"  Records: {record_count}")
        logger.info(f"  Last Extraction: {last_extraction}")
        logger.info(f"  Last Record Timestamp: {last_timestamp}")
        
        if record["error_message"]:
            logger.info(f"  Error: {record['error_message']}")
        
        logger.info("-" * 80)

def main():
    """Main function."""
    args = parse_args()
    
    try:
        # Show ETL status
        if args.status:
            show_etl_status()
            return
        
        # Set up database schema
        if args.setup_db:
            logger.info("Setting up database schema...")
            etl_orchestrator.setup_database()
            logger.info("Database schema setup complete")
        
        # Generate JSON schemas
        if args.generate_schemas:
            logger.info("Generating JSON schemas...")
            etl_orchestrator.generate_schemas()
            logger.info("JSON schema generation complete")
        
        # Run ETL process
        if not args.status and not args.setup_db and not args.generate_schemas:
            # Validate entities
            entities = validate_entities(args.entities)
            
            if not entities:
                logger.error("No valid entities specified")
                return
            
            # Log ETL parameters
            logger.info(f"Running ETL process for {len(entities)} entities:")
            logger.info(f"  Entities: {', '.join(entities)}")
            logger.info(f"  Validate: {args.validate}")
            logger.info(f"  Incremental: {args.incremental}")
            
            # Run ETL process
            start_time = time.time()
            results = etl_orchestrator.run_full_etl(
                entities=entities,
                validate=args.validate,
                incremental=args.incremental
            )
            duration = time.time() - start_time
            
            # Log results
            logger.info(f"ETL process completed in {duration:.2f} seconds")
            logger.info(f"Results: {json.dumps(results, default=str, indent=2)}")
    
    except Exception as e:
        logger.error(f"Error running ETL process: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
