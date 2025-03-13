"""
Database loader for the Mercurios.ai ETL pipeline.
"""
from datetime import datetime
from typing import Dict, List, Any, Type, Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.inspection import inspect

from etl.utils.database import SessionLocal, Base
from etl.utils.logger import logger
from etl.models.models import ETLMetadata

class DatabaseLoader:
    """
    Loads data into the database.
    Handles upserts, transactions, and error handling.
    """
    
    def __init__(self):
        """Initialize the database loader."""
        self.session = None
    
    def _get_session(self) -> Session:
        """Get a database session."""
        if not self.session:
            self.session = SessionLocal()
        return self.session
    
    def close_session(self):
        """Close the database session."""
        if self.session:
            self.session.close()
            self.session = None
    
    def _get_model_class(self, entity_name: str) -> Type[Base]:
        """
        Get the model class for an entity.
        
        Args:
            entity_name: Name of the entity
            
        Returns:
            Model class
        """
        # Import here to avoid circular imports
        from etl.models.models import (
            Article, Customer, Order, OrderPosition, Sale, Inventory,
            CustomerCard, Supplier, Branch, Category, Voucher, Invoice, Payment
        )
        
        entity_model_map = {
            "article": Article,
            "customer": Customer,
            "order": Order,
            "orderposition": OrderPosition,
            "sale": Sale,
            "inventory": Inventory,
            "customercard": CustomerCard,
            "supplier": Supplier,
            "branch": Branch,
            "category": Category,
            "voucher": Voucher,
            "invoice": Invoice,
            "payment": Payment,
        }
        
        if entity_name not in entity_model_map:
            raise ValueError(f"Unknown entity: {entity_name}")
        
        return entity_model_map[entity_name]
    
    def _prepare_data(self, entity_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare data for insertion into the database.
        Maps API field names to database column names.
        
        Args:
            entity_name: Name of the entity
            data: Data to prepare
            
        Returns:
            Prepared data
        """
        # Store the raw data
        prepared_data = {"raw_data": data}
        
        # Map common fields
        field_mappings = {
            "id": "id",
            "number": "number",
            "name": "name",
            "isActive": "is_active",
            "isDeleted": "is_deleted",
            "lastChange": "last_change",
        }
        
        # Entity-specific field mappings
        entity_field_mappings = {
            "article": {
                "purchasePrice": "purchase_price",
                "manufacturerNumber": "manufacturer_number",
                "supplierArticleNumber": "supplier_article_number",
                "firstPurchaseDate": "first_purchase_date",
                "lastPurchaseDate": "last_purchase_date",
                "information": "description",
            },
            "customer": {
                "name1": "name1",
                "name2": "name2",
                "name3": "name3",
                "searchTerm": "search_term",
                "revenue": "revenue",
                "bonusValue": "bonus_value",
                "loyalityPoints": "loyalty_points",
            },
            # Add mappings for other entities as needed
        }
        
        # Apply common mappings
        for api_field, db_field in field_mappings.items():
            if api_field in data:
                prepared_data[db_field] = data[api_field]
        
        # Apply entity-specific mappings
        if entity_name in entity_field_mappings:
            for api_field, db_field in entity_field_mappings[entity_name].items():
                if api_field in data:
                    prepared_data[db_field] = data[api_field]
        
        return prepared_data
    
    def upsert(self, entity_name: str, data: Dict[str, Any]) -> Optional[Base]:
        """
        Insert or update a record in the database.
        
        Args:
            entity_name: Name of the entity
            data: Data to insert or update
            
        Returns:
            The inserted or updated model instance
        """
        try:
            session = self._get_session()
            model_class = self._get_model_class(entity_name)
            
            # Prepare data
            prepared_data = self._prepare_data(entity_name, data)
            
            # Check if record exists
            instance = None
            if "id" in prepared_data:
                instance = session.query(model_class).filter_by(id=prepared_data["id"]).first()
            
            if instance:
                # Update existing record
                for key, value in prepared_data.items():
                    if hasattr(instance, key):
                        setattr(instance, key, value)
                logger.debug(f"Updated {entity_name} record with ID {prepared_data.get('id')}")
            else:
                # Insert new record
                instance = model_class(**prepared_data)
                session.add(instance)
                logger.debug(f"Inserted new {entity_name} record with ID {prepared_data.get('id')}")
            
            return instance
            
        except Exception as e:
            logger.error(f"Error upserting {entity_name} record: {e}")
            session.rollback()
            return None
    
    def bulk_upsert(self, entity_name: str, data_batch: List[Dict[str, Any]]) -> int:
        """
        Insert or update multiple records in the database.
        
        Args:
            entity_name: Name of the entity
            data_batch: Batch of data to insert or update
            
        Returns:
            Number of records successfully processed
        """
        if not data_batch:
            return 0
        
        session = self._get_session()
        success_count = 0
        
        try:
            # Process each record
            for data in data_batch:
                result = self.upsert(entity_name, data)
                if result:
                    success_count += 1
            
            # Commit the transaction
            session.commit()
            logger.info(f"Bulk upserted {success_count}/{len(data_batch)} {entity_name} records")
            
            return success_count
            
        except SQLAlchemyError as e:
            logger.error(f"Database error during bulk upsert of {entity_name}: {e}")
            session.rollback()
            return success_count
        except Exception as e:
            logger.error(f"Error during bulk upsert of {entity_name}: {e}")
            session.rollback()
            return success_count
    
    def update_etl_metadata(self, entity_name: str, record_count: int, status: str, 
                           last_record_timestamp: Optional[datetime] = None, 
                           error_message: Optional[str] = None) -> ETLMetadata:
        """
        Update ETL metadata for an entity.
        
        Args:
            entity_name: Name of the entity
            record_count: Number of records processed
            status: Status of the ETL process
            last_record_timestamp: Timestamp of the last record processed
            error_message: Error message if any
            
        Returns:
            The updated ETL metadata record
        """
        try:
            session = self._get_session()
            
            # Get existing metadata or create new
            metadata = session.query(ETLMetadata).filter_by(entity_name=entity_name).first()
            
            if not metadata:
                metadata = ETLMetadata(entity_name=entity_name)
                session.add(metadata)
            
            # Update fields
            metadata.last_extraction_time = datetime.utcnow()
            metadata.record_count = record_count
            metadata.status = status
            
            if last_record_timestamp:
                metadata.last_record_timestamp = last_record_timestamp
            
            if error_message:
                metadata.error_message = error_message
            
            session.commit()
            logger.info(f"Updated ETL metadata for {entity_name}: {status}, {record_count} records")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error updating ETL metadata for {entity_name}: {e}")
            session.rollback()
            return None

# Create a singleton instance
database_loader = DatabaseLoader()
