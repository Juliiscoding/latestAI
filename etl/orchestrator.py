"""
ETL Orchestrator for the Mercurios.ai ETL pipeline.
"""
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

from sqlalchemy.orm import Session

from etl.connectors.prohandel_connector import ProHandelConnector
from etl.loaders.database_loader import DatabaseLoader
from etl.transformers.article_transformer import ArticleTransformer
from etl.transformers.sales_transformer import SalesTransformer
from etl.transformers.inventory_transformer import InventoryTransformer
from etl.transformers.customer_transformer import CustomerTransformer
from etl.transformers.supplier_transformer import SupplierTransformer
from etl.validators.schema_validator import SchemaValidator
from etl.utils.logger import logger
from etl.config.config import ETL_CONFIG, API_ENDPOINTS
from etl.models.models import ETLMetadata

class ETLOrchestrator:
    """
    Orchestrator for the ETL pipeline.
    Coordinates extraction, transformation, validation, and loading of data.
    """
    
    def __init__(self, db_session: Session, incremental: bool = True):
        """
        Initialize the ETL orchestrator.
        
        Args:
            db_session: SQLAlchemy database session
            incremental: Whether to use incremental loading
        """
        self.db_session = db_session
        self.incremental = incremental
        self.connector = ProHandelConnector()
        self.loader = DatabaseLoader(db_session)
        self.validator = SchemaValidator()
        
        # Initialize transformers
        self.article_transformer = None
        self.sales_transformer = None
        self.inventory_transformer = None
        self.customer_transformer = None
        self.supplier_transformer = None
        
        # Store extracted data for cross-entity transformations
        self.extracted_data = {}
        
        logger.info(f"Initialized ETL orchestrator (incremental={incremental})")
    
    def run_etl(self, entities: Optional[List[str]] = None) -> Dict[str, Dict[str, int]]:
        """
        Run the ETL pipeline for specified entities.
        
        Args:
            entities: List of entity names to process (None for all)
            
        Returns:
            Dictionary with ETL statistics for each entity
        """
        # Determine which entities to process
        if entities is None:
            entities = list(API_ENDPOINTS.keys())
        
        logger.info(f"Starting ETL pipeline for entities: {entities}")
        
        # Get last ETL run timestamps
        last_run_timestamps = self._get_last_run_timestamps(entities)
        
        # Extract and process data for each entity
        results = {}
        
        # First pass: extract data for all entities
        for entity_name in entities:
            try:
                extracted_data = self._extract_entity(entity_name, last_run_timestamps.get(entity_name))
                self.extracted_data[entity_name] = extracted_data
                logger.info(f"Extracted {len(extracted_data)} records for {entity_name}")
            except Exception as e:
                logger.error(f"Error extracting data for {entity_name}: {e}")
                self.extracted_data[entity_name] = []
        
        # Initialize transformers with cross-entity data
        self._initialize_transformers()
        
        # Second pass: transform, validate, and load data for each entity
        for entity_name in entities:
            try:
                entity_result = self._process_entity(entity_name)
                results[entity_name] = entity_result
            except Exception as e:
                logger.error(f"Error processing {entity_name}: {e}")
                results[entity_name] = {
                    "extracted": len(self.extracted_data.get(entity_name, [])),
                    "validated": 0,
                    "transformed": 0,
                    "loaded": 0,
                    "errors": 1
                }
        
        # Update ETL metadata
        self._update_etl_metadata(entities)
        
        logger.info(f"ETL pipeline completed for entities: {entities}")
        
        return results
    
    def _extract_entity(self, entity_name: str, last_timestamp: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Extract data for an entity.
        
        Args:
            entity_name: Name of the entity to extract
            last_timestamp: Timestamp of the last successful extraction
            
        Returns:
            List of extracted data records
        """
        logger.info(f"Extracting data for {entity_name}")
        
        # Get entity configuration
        entity_config = API_ENDPOINTS.get(entity_name, {})
        batch_size = entity_config.get("batch_size", ETL_CONFIG["default_batch_size"])
        
        # Extract data
        if self.incremental and last_timestamp and entity_config.get("timestamp_field"):
            # Incremental extraction
            timestamp_field = entity_config["timestamp_field"]
            logger.info(f"Performing incremental extraction for {entity_name} since {last_timestamp}")
            
            # Convert timestamp to string format expected by the API
            timestamp_str = last_timestamp.isoformat()
            
            # Extract data with timestamp filter
            data = self.connector.get_entity_list(
                entity_name,
                filter_params={timestamp_field: timestamp_str},
                batch_size=batch_size
            )
        else:
            # Full extraction
            logger.info(f"Performing full extraction for {entity_name}")
            data = self.connector.get_entity_list(entity_name, batch_size=batch_size)
        
        logger.info(f"Extracted {len(data)} records for {entity_name}")
        
        return data
    
    def _initialize_transformers(self):
        """Initialize transformers with cross-entity data."""
        logger.info("Initializing transformers with cross-entity data")
        
        # Initialize article transformer
        self.article_transformer = ArticleTransformer(
            inventory_data=self.extracted_data.get("inventory", []),
            sales_data=self.extracted_data.get("sale", [])
        )
        
        # Initialize sales transformer
        self.sales_transformer = SalesTransformer()
        
        # Initialize inventory transformer
        self.inventory_transformer = InventoryTransformer(
            sales_data=self.extracted_data.get("sale", [])
        )
        
        # Initialize customer transformer
        self.customer_transformer = CustomerTransformer(
            sales_data=self.extracted_data.get("sale", []),
            orders_data=self.extracted_data.get("order", [])
        )
        
        # Initialize supplier transformer
        self.supplier_transformer = SupplierTransformer(
            orders_data=self.extracted_data.get("order", [])
        )
    
    def _process_entity(self, entity_name: str) -> Dict[str, int]:
        """
        Process data for an entity (validate, transform, load).
        
        Args:
            entity_name: Name of the entity to process
            
        Returns:
            Dictionary with processing statistics
        """
        logger.info(f"Processing data for {entity_name}")
        
        # Get extracted data
        data = self.extracted_data.get(entity_name, [])
        
        if not data:
            logger.warning(f"No data to process for {entity_name}")
            return {
                "extracted": 0,
                "validated": 0,
                "transformed": 0,
                "loaded": 0,
                "errors": 0
            }
        
        # Validate data
        valid_data, validation_errors = self._validate_entity(entity_name, data)
        
        logger.info(f"Validated {len(valid_data)}/{len(data)} records for {entity_name}")
        
        if not valid_data:
            logger.warning(f"No valid data to process for {entity_name}")
            return {
                "extracted": len(data),
                "validated": 0,
                "transformed": 0,
                "loaded": 0,
                "errors": len(validation_errors)
            }
        
        # Transform data
        transformed_data, transformation_errors = self._transform_entity(entity_name, valid_data)
        
        logger.info(f"Transformed {len(transformed_data)}/{len(valid_data)} records for {entity_name}")
        
        if not transformed_data:
            logger.warning(f"No transformed data to load for {entity_name}")
            return {
                "extracted": len(data),
                "validated": len(valid_data),
                "transformed": 0,
                "loaded": 0,
                "errors": len(validation_errors) + len(transformation_errors)
            }
        
        # Load data
        loaded_count, load_errors = self._load_entity(entity_name, transformed_data)
        
        logger.info(f"Loaded {loaded_count}/{len(transformed_data)} records for {entity_name}")
        
        # Load aggregations if available
        self._load_aggregations(entity_name)
        
        return {
            "extracted": len(data),
            "validated": len(valid_data),
            "transformed": len(transformed_data),
            "loaded": loaded_count,
            "errors": len(validation_errors) + len(transformation_errors) + len(load_errors)
        }
    
    def _validate_entity(self, entity_name: str, data: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Validate data for an entity.
        
        Args:
            entity_name: Name of the entity to validate
            data: Data to validate
            
        Returns:
            Tuple of (valid_data, validation_errors)
        """
        logger.info(f"Validating {len(data)} records for {entity_name}")
        
        valid_data = []
        validation_errors = []
        
        for record in data:
            try:
                if self.validator.validate(entity_name, record):
                    valid_data.append(record)
            except Exception as e:
                logger.error(f"Validation error for {entity_name}: {e}")
                validation_errors.append({
                    "record": record,
                    "error": str(e)
                })
        
        return valid_data, validation_errors
    
    def _transform_entity(self, entity_name: str, data: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Transform data for an entity.
        
        Args:
            entity_name: Name of the entity to transform
            data: Data to transform
            
        Returns:
            Tuple of (transformed_data, transformation_errors)
        """
        logger.info(f"Transforming {len(data)} records for {entity_name}")
        
        transformed_data = []
        transformation_errors = []
        
        try:
            # Select the appropriate transformer
            if entity_name == "article":
                transformed_data = self.article_transformer.transform_batch(data)
            elif entity_name == "sale":
                transformed_data = self.sales_transformer.transform_batch(data)
            elif entity_name == "inventory":
                transformed_data = self.inventory_transformer.transform_batch(data)
            elif entity_name == "customer":
                transformed_data = self.customer_transformer.transform_batch(data)
            elif entity_name == "supplier":
                transformed_data = self.supplier_transformer.transform_batch(data)
            else:
                # For entities without a specific transformer, use a pass-through approach
                transformed_data = data
        except Exception as e:
            logger.error(f"Transformation error for {entity_name}: {e}")
            transformation_errors.append({
                "entity": entity_name,
                "error": str(e)
            })
        
        return transformed_data, transformation_errors
    
    def _load_entity(self, entity_name: str, data: List[Dict[str, Any]]) -> Tuple[int, List[Dict[str, Any]]]:
        """
        Load data for an entity.
        
        Args:
            entity_name: Name of the entity to load
            data: Data to load
            
        Returns:
            Tuple of (loaded_count, load_errors)
        """
        logger.info(f"Loading {len(data)} records for {entity_name}")
        
        load_errors = []
        
        try:
            loaded_count = self.loader.load_entity(entity_name, data)
            return loaded_count, load_errors
        except Exception as e:
            logger.error(f"Loading error for {entity_name}: {e}")
            load_errors.append({
                "entity": entity_name,
                "error": str(e)
            })
            return 0, load_errors
    
    def _load_aggregations(self, entity_name: str):
        """
        Load aggregations for an entity.
        
        Args:
            entity_name: Name of the entity
        """
        if entity_name == "sale":
            # Load sales aggregations
            try:
                # Daily aggregations
                daily_aggs = self.sales_transformer.get_daily_aggregations()
                if daily_aggs:
                    logger.info(f"Loading {len(daily_aggs)} daily sales aggregations")
                    self.loader.load_entity("sales_daily_aggregation", daily_aggs)
                
                # Weekly aggregations
                weekly_aggs = self.sales_transformer.get_weekly_aggregations()
                if weekly_aggs:
                    logger.info(f"Loading {len(weekly_aggs)} weekly sales aggregations")
                    self.loader.load_entity("sales_weekly_aggregation", weekly_aggs)
                
                # Monthly aggregations
                monthly_aggs = self.sales_transformer.get_monthly_aggregations()
                if monthly_aggs:
                    logger.info(f"Loading {len(monthly_aggs)} monthly sales aggregations")
                    self.loader.load_entity("sales_monthly_aggregation", monthly_aggs)
            except Exception as e:
                logger.error(f"Error loading sales aggregations: {e}")
        
        elif entity_name == "inventory":
            # Load inventory history
            try:
                inventory_history = self.inventory_transformer.get_inventory_history()
                if inventory_history:
                    # Flatten the history data
                    flat_history = []
                    for key, records in inventory_history.items():
                        flat_history.extend(records)
                    
                    if flat_history:
                        logger.info(f"Loading {len(flat_history)} inventory history records")
                        self.loader.load_entity("inventory_history", flat_history)
            except Exception as e:
                logger.error(f"Error loading inventory history: {e}")
        
        elif entity_name == "customer":
            # Load customer purchase patterns
            try:
                purchase_patterns = self.customer_transformer.get_customer_purchase_patterns()
                if purchase_patterns:
                    # Convert to list of records
                    pattern_records = []
                    for customer_id, patterns in purchase_patterns.items():
                        pattern_record = {
                            "customer_id": customer_id,
                            "patterns": patterns
                        }
                        pattern_records.append(pattern_record)
                    
                    if pattern_records:
                        logger.info(f"Loading {len(pattern_records)} customer purchase patterns")
                        self.loader.load_entity("customer_purchase_pattern", pattern_records)
            except Exception as e:
                logger.error(f"Error loading customer purchase patterns: {e}")
        
        elif entity_name == "supplier":
            # Load supplier metrics
            try:
                supplier_metrics = self.supplier_transformer.get_supplier_metrics()
                if supplier_metrics:
                    # Convert to list of records
                    metrics_records = []
                    for supplier_id, metrics in supplier_metrics.items():
                        metrics_record = {
                            "supplier_id": supplier_id,
                            **metrics
                        }
                        metrics_records.append(metrics_record)
                    
                    if metrics_records:
                        logger.info(f"Loading {len(metrics_records)} supplier metrics records")
                        self.loader.load_entity("supplier_metrics", metrics_records)
            except Exception as e:
                logger.error(f"Error loading supplier metrics: {e}")
    
    def _get_last_run_timestamps(self, entities: List[str]) -> Dict[str, datetime]:
        """
        Get timestamps of the last successful ETL run for each entity.
        
        Args:
            entities: List of entity names
            
        Returns:
            Dictionary of last run timestamps by entity
        """
        result = {}
        
        if not self.incremental:
            logger.info("Incremental loading disabled, skipping timestamp retrieval")
            return result
        
        logger.info("Retrieving last run timestamps for incremental loading")
        
        try:
            # Query ETL metadata for each entity
            for entity_name in entities:
                metadata = self.db_session.query(ETLMetadata).filter(
                    ETLMetadata.entity_name == entity_name,
                    ETLMetadata.status == "success"
                ).order_by(ETLMetadata.end_time.desc()).first()
                
                if metadata:
                    result[entity_name] = metadata.end_time
                    logger.info(f"Last successful run for {entity_name}: {metadata.end_time}")
                else:
                    logger.info(f"No previous successful run found for {entity_name}")
        except Exception as e:
            logger.error(f"Error retrieving last run timestamps: {e}")
        
        return result
    
    def _update_etl_metadata(self, entities: List[str]):
        """
        Update ETL metadata for the current run.
        
        Args:
            entities: List of processed entities
        """
        logger.info("Updating ETL metadata")
        
        end_time = datetime.now()
        
        try:
            for entity_name in entities:
                # Create metadata record
                metadata = ETLMetadata(
                    entity_name=entity_name,
                    start_time=datetime.now(),
                    end_time=end_time,
                    record_count=len(self.extracted_data.get(entity_name, [])),
                    status="success"
                )
                
                # Add to session
                self.db_session.add(metadata)
            
            # Commit changes
            self.db_session.commit()
            
            logger.info("ETL metadata updated successfully")
        except Exception as e:
            logger.error(f"Error updating ETL metadata: {e}")
            self.db_session.rollback()
