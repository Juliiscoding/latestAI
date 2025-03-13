"""
Schema validation utility for the Mercurios.ai ETL pipeline.
This module provides schema validation with a fallback implementation for Lambda environments
where jsonschema might not be available.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple

# Try to import jsonschema, but provide a fallback if it's not available
try:
    import jsonschema
    from jsonschema import validate, ValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    # Define a simple ValidationError class for the fallback implementation
    class ValidationError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(message)

# Check if we're running in a Lambda environment
is_lambda = os.environ.get('AWS_LAMBDA_FUNCTION_NAME') is not None

from etl.utils.logger import logger

class SchemaValidator:
    """
    Validates data against JSON schemas.
    Provides a fallback implementation for Lambda environments where jsonschema might not be available.
    """
    
    def __init__(self, schemas_dir: Optional[Path] = None):
        """
        Initialize the schema validator.
        
        Args:
            schemas_dir: Directory containing JSON schema files
        """
        self.schemas_dir = schemas_dir or Path(__file__).parent / "schemas"
        self.schemas = {}
        self._load_schemas()
        
        # Log whether we're using jsonschema or the fallback implementation
        if is_lambda or not JSONSCHEMA_AVAILABLE:
            logger.info("Using simplified schema validation (jsonschema not available)")
        else:
            logger.info("Using full schema validation with jsonschema")
    
    def _load_schemas(self):
        """Load all schema files from the schemas directory."""
        if not self.schemas_dir.exists():
            logger.warning(f"Schemas directory {self.schemas_dir} does not exist")
            return
        
        for schema_file in self.schemas_dir.glob("*.json"):
            try:
                with open(schema_file, "r") as f:
                    schema = json.load(f)
                    entity_name = schema_file.stem
                    self.schemas[entity_name] = schema
                    logger.debug(f"Loaded schema for {entity_name}")
            except Exception as e:
                logger.error(f"Error loading schema from {schema_file}: {e}")
    
    def _simple_type_check(self, value: Any, expected_type: str) -> bool:
        """Simple type checking for the fallback implementation."""
        if expected_type == "string":
            return isinstance(value, str)
        elif expected_type == "number":
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        elif expected_type == "integer":
            return isinstance(value, int) and not isinstance(value, bool)
        elif expected_type == "boolean":
            return isinstance(value, bool)
        elif expected_type == "array":
            return isinstance(value, list)
        elif expected_type == "object":
            return isinstance(value, dict)
        elif expected_type == "null":
            return value is None
        return True  # Unknown type, assume valid
    
    def _simple_validate(self, data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Simple schema validation for the fallback implementation."""
        # Check required properties
        if "required" in schema and isinstance(schema["required"], list):
            for prop in schema["required"]:
                if prop not in data:
                    return False, f"Missing required property: {prop}"
        
        # Check property types
        if "properties" in schema and isinstance(schema["properties"], dict):
            for prop, prop_schema in schema["properties"].items():
                if prop in data and "type" in prop_schema:
                    if not self._simple_type_check(data[prop], prop_schema["type"]):
                        return False, f"Property {prop} has wrong type, expected {prop_schema['type']}"
        
        return True, None  # Validation passed
    
    def validate_item(self, entity_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a single data item against its schema.
        Uses jsonschema if available, otherwise falls back to a simple validation.
        
        Args:
            entity_name: Name of the entity (corresponds to schema file name)
            data: Data to validate
            
        Returns:
            The validated data (possibly cleaned)
            
        Raises:
            ValidationError: If validation fails
        """
        if entity_name not in self.schemas:
            logger.warning(f"No schema found for {entity_name}, skipping validation")
            return data
        
        # Use jsonschema if available, otherwise use our simple validation
        if JSONSCHEMA_AVAILABLE and not is_lambda:
            try:
                validate(instance=data, schema=self.schemas[entity_name])
                return data
            except ValidationError as e:
                logger.error(f"Validation error for {entity_name}: {e}")
                raise
        else:
            # Use our simple validation
            valid, error_msg = self._simple_validate(data, self.schemas[entity_name])
            if valid:
                return data
            else:
                logger.error(f"Validation error for {entity_name}: {error_msg}")
                raise ValidationError(error_msg)
    
    def validate_batch(self, entity_name: str, data_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate a batch of data items against their schema.
        
        Args:
            entity_name: Name of the entity (corresponds to schema file name)
            data_batch: Batch of data to validate
            
        Returns:
            List of valid data items (invalid items are filtered out)
        """
        if entity_name not in self.schemas:
            logger.warning(f"No schema found for {entity_name}, skipping validation")
            return data_batch
        
        valid_items = []
        for item in data_batch:
            try:
                valid_item = self.validate_item(entity_name, item)
                valid_items.append(valid_item)
            except ValidationError:
                # Error already logged in validate_item
                continue
        
        logger.info(f"Validated {len(valid_items)}/{len(data_batch)} items for {entity_name}")
        return valid_items
    
    def generate_schema(self, entity_name: str, data_samples: List[Dict[str, Any]], save: bool = True) -> Dict[str, Any]:
        """
        Generate a JSON schema from data samples.
        
        Args:
            entity_name: Name of the entity
            data_samples: Sample data to generate schema from
            save: Whether to save the generated schema to file
            
        Returns:
            The generated schema
        """
        if not data_samples:
            logger.error(f"Cannot generate schema for {entity_name}: no data samples provided")
            return {}
        
        # This is a very basic schema generator
        # For production, consider using a more sophisticated library
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": f"{entity_name.capitalize()} Schema",
            "type": "object",
            "properties": {},
            "required": []
        }
        
        # Use the first sample to determine property types
        sample = data_samples[0]
        for key, value in sample.items():
            if value is None:
                schema["properties"][key] = {"type": ["null", "string", "number", "boolean", "object", "array"]}
            elif isinstance(value, str):
                schema["properties"][key] = {"type": ["null", "string"]}
            elif isinstance(value, (int, float)):
                schema["properties"][key] = {"type": ["null", "number"]}
            elif isinstance(value, bool):
                schema["properties"][key] = {"type": ["null", "boolean"]}
            elif isinstance(value, dict):
                schema["properties"][key] = {"type": ["null", "object"]}
            elif isinstance(value, list):
                schema["properties"][key] = {"type": ["null", "array"]}
            
            # Add to required if present in all samples
            if all(key in sample and sample[key] is not None for sample in data_samples):
                schema["required"].append(key)
        
        if save:
            # Ensure schemas directory exists
            self.schemas_dir.mkdir(parents=True, exist_ok=True)
            
            # Save schema to file
            schema_path = self.schemas_dir / f"{entity_name}.json"
            with open(schema_path, "w") as f:
                json.dump(schema, f, indent=2)
            
            # Update in-memory schemas
            self.schemas[entity_name] = schema
            
            logger.info(f"Generated and saved schema for {entity_name}")
        
        return schema

# Create a singleton instance
schema_validator = SchemaValidator()
