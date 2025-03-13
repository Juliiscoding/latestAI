"""
ETL orchestrator for the Mercurios.ai ETL pipeline.
"""
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Set

from etl.config.config import API_ENDPOINTS, ETL_CONFIG
from etl.connectors.prohandel_connector import prohandel_connector
from etl.loaders.database_loader import database_loader
from etl.utils.logger import logger
from etl.utils.database import init_db
from etl.models.models import ETLMetadata

class ETLOrchestrator:
    """
    Orchestrates the ETL process for the Mercurios.ai ETL pipeline.
    """
    
    def __init__(self):
        """Initialize the ETL orchestrator."""
        self.connector = prohandel_connector
        self.loader = database_loader
        self.batch_size = ETL_CONFIG["batch_size"]
        self.incremental_load = ETL_CONFIG["incremental_load"]
    
    def setup_database(self):
        """Set up the database schema."""
        try:
            logger.info("Setting up database schema...")
            init_db()
            logger.info("Database schema setup complete")
        except Exception as e:
            logger.error(f"Error setting up database schema: {e}")
            raise
    
    def generate_schemas(self):
        """Generate JSON schemas for all entity types."""
        try:
            logger.info("Generating JSON schemas...")
            schemas = self.connector.generate_schemas_from_samples(save=True)
            logger.info(f"Generated {len(schemas)} JSON schemas")
        except Exception as e:
            logger.error(f"Error generating JSON schemas: {e}")
    
    def extract_load_entity(self, entity_name: str, validate: bool = True, 
                           incremental: Optional[bool] = None) -> Dict[str, Any]:
        """
        Extract and load data for a specific entity.
        
        Args:
            entity_name: Name of the entity
            validate: Whether to validate the data
            incremental: Whether to use incremental loading
            
        Returns:
            Dictionary with extraction statistics
        """
        if entity_name not in API_ENDPOINTS:
            raise ValueError(f"Unknown entity: {entity_name}")
        
        start_time = time.time()
        total_records = 0
        total_loaded = 0
        last_timestamp = None
        status = "success"
        error_message = None
        
        try:
            logger.info(f"Starting extraction and loading for {entity_name}...")
            
            # Extract data in batches
            for batch in self.connector.extract_all_entities(entity_name, validate=validate, incremental=incremental):
                # Load batch into database
                loaded_count = self.loader.bulk_upsert(entity_name, batch)
                
                # Update counters
                batch_size = len(batch)
                total_records += batch_size
                total_loaded += loaded_count
                
                # Get last timestamp for incremental loading
                if batch and API_ENDPOINTS[entity_name].get("timestamp_field"):
                    timestamp_field = API_ENDPOINTS[entity_name]["timestamp_field"]
                    for item in batch:
                        if timestamp_field in item and item[timestamp_field]:
                            item_timestamp = item[timestamp_field]
                            if isinstance(item_timestamp, str):
                                try:
                                    item_timestamp = datetime.fromisoformat(item_timestamp.replace('Z', '+00:00'))
                                except ValueError:
                                    continue
                            
                            if isinstance(item_timestamp, datetime) and (not last_timestamp or item_timestamp > last_timestamp):
                                last_timestamp = item_timestamp
                
                logger.info(f"Loaded {loaded_count}/{batch_size} {entity_name} records (total: {total_loaded}/{total_records})")
            
        except Exception as e:
            logger.error(f"Error during extraction and loading for {entity_name}: {e}")
            status = "error"
            error_message = str(e)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Update ETL metadata
        self.loader.update_etl_metadata(
            entity_name=entity_name,
            record_count=total_records,
            status=status,
            last_record_timestamp=last_timestamp,
            error_message=error_message
        )
        
        # Log summary
        logger.info(f"Completed {entity_name} extraction and loading: {total_loaded}/{total_records} records in {duration:.2f} seconds")
        
        # Return statistics
        return {
            "entity_name": entity_name,
            "total_records": total_records,
            "total_loaded": total_loaded,
            "duration": duration,
            "status": status,
            "error_message": error_message,
            "last_timestamp": last_timestamp,
        }
    
    def run_full_etl(self, entities: Optional[List[str]] = None, validate: bool = True, 
                    incremental: Optional[bool] = None) -> Dict[str, Dict[str, Any]]:
        """
        Run the full ETL process for all or specified entities.
        
        Args:
            entities: List of entity names to process (None for all)
            validate: Whether to validate the data
            incremental: Whether to use incremental loading
            
        Returns:
            Dictionary with ETL statistics for each entity
        """
        # Determine which entities to process
        entities_to_process = entities or list(API_ENDPOINTS.keys())
        
        # Validate entity names
        invalid_entities = [e for e in entities_to_process if e not in API_ENDPOINTS]
        if invalid_entities:
            raise ValueError(f"Unknown entities: {', '.join(invalid_entities)}")
        
        start_time = time.time()
        results = {}
        
        logger.info(f"Starting full ETL process for {len(entities_to_process)} entities...")
        
        try:
            # Process each entity
            for entity_name in entities_to_process:
                results[entity_name] = self.extract_load_entity(
                    entity_name=entity_name,
                    validate=validate,
                    incremental=incremental
                )
        except Exception as e:
            logger.error(f"Error during full ETL process: {e}")
        finally:
            # Close database session
            self.loader.close_session()
        
        # Calculate total duration
        total_duration = time.time() - start_time
        
        # Log summary
        total_records = sum(r["total_records"] for r in results.values())
        total_loaded = sum(r["total_loaded"] for r in results.values())
        success_count = sum(1 for r in results.values() if r["status"] == "success")
        
        logger.info(f"Completed full ETL process: {success_count}/{len(entities_to_process)} entities successful")
        logger.info(f"Total records: {total_loaded}/{total_records} loaded in {total_duration:.2f} seconds")
        
        return results
    
    def get_etl_status(self) -> List[Dict[str, Any]]:
        """
        Get the status of all ETL processes.
        
        Returns:
            List of ETL metadata records
        """
        try:
            session = self.loader._get_session()
            metadata_records = session.query(ETLMetadata).all()
            return [record.to_dict() for record in metadata_records]
        except Exception as e:
            logger.error(f"Error getting ETL status: {e}")
            return []
        finally:
            self.loader.close_session()

# Create a singleton instance
etl_orchestrator = ETLOrchestrator()
