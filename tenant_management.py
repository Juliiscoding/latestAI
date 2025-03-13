"""
Tenant Management Module for Mercurios.ai

This module provides functionality for managing tenants in the Mercurios.ai system,
including tenant registration, configuration, and deployment of tenant-specific resources.
"""

import os
import json
import uuid
import boto3
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class TenantManager:
    """Manages tenant-related operations for Mercurios.ai."""
    
    def __init__(self, aws_region: str = "eu-central-1"):
        """Initialize the TenantManager with AWS region."""
        self.aws_region = aws_region
        self.lambda_client = boto3.client('lambda', region_name=aws_region)
        self.secrets_client = boto3.client('secretsmanager', region_name=aws_region)
        self.s3_client = boto3.client('s3', region_name=aws_region)
        
        # S3 bucket for tenant configurations
        self.config_bucket = os.environ.get('TENANT_CONFIG_BUCKET', 'mercurios-tenant-configs')
        
        # Lambda function name template
        self.lambda_function_template = os.environ.get('LAMBDA_FUNCTION_TEMPLATE', 'prohandel-fivetran-connector-{tenant_id}')
        
        logger.info(f"Initialized TenantManager with region: {aws_region}")
    
    def register_tenant(self, 
                       tenant_name: str, 
                       prohandel_api_key: str, 
                       prohandel_api_secret: str,
                       contact_email: str,
                       pos_system: str = "ProHandel") -> Dict:
        """
        Register a new tenant in the system.
        
        Args:
            tenant_name: Name of the tenant (company name)
            prohandel_api_key: ProHandel API key
            prohandel_api_secret: ProHandel API secret
            contact_email: Contact email for the tenant
            pos_system: POS system used by the tenant (default: ProHandel)
            
        Returns:
            Dict containing tenant information including tenant_id
        """
        # Generate a unique tenant ID
        tenant_id = str(uuid.uuid4())
        
        # Create tenant record
        tenant_info = {
            "tenant_id": tenant_id,
            "tenant_name": tenant_name,
            "contact_email": contact_email,
            "pos_system": pos_system,
            "created_at": datetime.utcnow().isoformat(),
            "status": "pending",
            "api_credentials": {
                "type": pos_system,
                "api_key": prohandel_api_key,
                "api_secret": prohandel_api_secret
            }
        }
        
        try:
            # Store tenant configuration in S3
            self._store_tenant_config(tenant_id, tenant_info)
            
            # Store API credentials in AWS Secrets Manager
            self._store_api_credentials(tenant_id, prohandel_api_key, prohandel_api_secret)
            
            # Deploy tenant-specific Lambda function
            lambda_function_name = self._deploy_tenant_lambda(tenant_id, prohandel_api_key, prohandel_api_secret)
            
            # Update tenant record with Lambda function name
            tenant_info["lambda_function_name"] = lambda_function_name
            tenant_info["status"] = "active"
            
            # Update tenant configuration
            self._store_tenant_config(tenant_id, tenant_info)
            
            logger.info(f"Successfully registered tenant: {tenant_name} with ID: {tenant_id}")
            
            # Return tenant information (excluding sensitive data)
            return {
                "tenant_id": tenant_id,
                "tenant_name": tenant_name,
                "contact_email": contact_email,
                "pos_system": pos_system,
                "created_at": tenant_info["created_at"],
                "status": "active",
                "lambda_function_name": lambda_function_name
            }
            
        except Exception as e:
            logger.error(f"Failed to register tenant {tenant_name}: {str(e)}")
            # Attempt to clean up any resources that were created
            self._cleanup_tenant_resources(tenant_id)
            raise
    
    def _store_tenant_config(self, tenant_id: str, tenant_info: Dict) -> None:
        """Store tenant configuration in S3."""
        # Create a copy without sensitive information for storage
        storage_info = tenant_info.copy()
        if "api_credentials" in storage_info:
            # Remove sensitive data before storing
            storage_info["api_credentials"] = {
                "type": storage_info["api_credentials"]["type"]
            }
        
        # Store in S3
        self.s3_client.put_object(
            Bucket=self.config_bucket,
            Key=f"tenants/{tenant_id}/config.json",
            Body=json.dumps(storage_info),
            ContentType="application/json"
        )
        
        logger.info(f"Stored configuration for tenant: {tenant_id}")
    
    def _store_api_credentials(self, tenant_id: str, api_key: str, api_secret: str) -> None:
        """Store API credentials in AWS Secrets Manager."""
        secret_name = f"mercurios/tenant/{tenant_id}/api-credentials"
        
        # Create the secret
        self.secrets_client.create_secret(
            Name=secret_name,
            SecretString=json.dumps({
                "PROHANDEL_API_KEY": api_key,
                "PROHANDEL_API_SECRET": api_secret
            })
        )
        
        logger.info(f"Stored API credentials for tenant: {tenant_id}")
    
    def _deploy_tenant_lambda(self, tenant_id: str, api_key: str, api_secret: str) -> str:
        """
        Deploy a tenant-specific Lambda function.
        
        Returns:
            Lambda function name
        """
        # Generate Lambda function name
        function_name = self.lambda_function_template.format(tenant_id=tenant_id)
        
        # Check if the function already exists
        try:
            self.lambda_client.get_function(FunctionName=function_name)
            # Function exists, update it
            logger.info(f"Updating existing Lambda function: {function_name}")
            self._update_lambda_function(function_name, tenant_id, api_key, api_secret)
        except self.lambda_client.exceptions.ResourceNotFoundException:
            # Function doesn't exist, create it
            logger.info(f"Creating new Lambda function: {function_name}")
            self._create_lambda_function(function_name, tenant_id, api_key, api_secret)
        
        return function_name
    
    def _create_lambda_function(self, function_name: str, tenant_id: str, api_key: str, api_secret: str) -> None:
        """Create a new Lambda function for the tenant."""
        # This would typically involve:
        # 1. Getting the Lambda function code from a template
        # 2. Customizing it for the tenant
        # 3. Creating the Lambda function with appropriate IAM role
        # 4. Setting environment variables
        
        # For this example, we'll just log the operation
        logger.info(f"Would create Lambda function: {function_name} for tenant: {tenant_id}")
        logger.info("This is a placeholder for the actual Lambda function creation")
    
    def _update_lambda_function(self, function_name: str, tenant_id: str, api_key: str, api_secret: str) -> None:
        """Update an existing Lambda function for the tenant."""
        # Update environment variables
        self.lambda_client.update_function_configuration(
            FunctionName=function_name,
            Environment={
                'Variables': {
                    'TENANT_ID': tenant_id,
                    'PROHANDEL_API_KEY': api_key,
                    'PROHANDEL_API_SECRET': api_secret
                }
            }
        )
        
        logger.info(f"Updated Lambda function configuration: {function_name}")
    
    def _cleanup_tenant_resources(self, tenant_id: str) -> None:
        """Clean up resources if tenant registration fails."""
        try:
            # Delete S3 configuration
            self.s3_client.delete_object(
                Bucket=self.config_bucket,
                Key=f"tenants/{tenant_id}/config.json"
            )
        except Exception as e:
            logger.error(f"Failed to delete S3 configuration for tenant {tenant_id}: {str(e)}")
        
        try:
            # Delete Secrets Manager secret
            secret_name = f"mercurios/tenant/{tenant_id}/api-credentials"
            self.secrets_client.delete_secret(
                SecretId=secret_name,
                ForceDeleteWithoutRecovery=True
            )
        except Exception as e:
            logger.error(f"Failed to delete secret for tenant {tenant_id}: {str(e)}")
        
        try:
            # Delete Lambda function
            function_name = self.lambda_function_template.format(tenant_id=tenant_id)
            self.lambda_client.delete_function(
                FunctionName=function_name
            )
        except Exception as e:
            logger.error(f"Failed to delete Lambda function for tenant {tenant_id}: {str(e)}")
        
        logger.info(f"Cleaned up resources for tenant: {tenant_id}")
    
    def get_tenant(self, tenant_id: str) -> Optional[Dict]:
        """Get tenant information by ID."""
        try:
            response = self.s3_client.get_object(
                Bucket=self.config_bucket,
                Key=f"tenants/{tenant_id}/config.json"
            )
            tenant_info = json.loads(response['Body'].read().decode('utf-8'))
            return tenant_info
        except Exception as e:
            logger.error(f"Failed to get tenant {tenant_id}: {str(e)}")
            return None
    
    def list_tenants(self) -> List[Dict]:
        """List all tenants in the system."""
        tenants = []
        try:
            # List objects with the tenants/ prefix
            response = self.s3_client.list_objects_v2(
                Bucket=self.config_bucket,
                Prefix="tenants/"
            )
            
            # Get tenant IDs from object keys
            for obj in response.get('Contents', []):
                key = obj['Key']
                if key.endswith('/config.json'):
                    tenant_id = key.split('/')[1]
                    tenant_info = self.get_tenant(tenant_id)
                    if tenant_info:
                        tenants.append(tenant_info)
            
            return tenants
        except Exception as e:
            logger.error(f"Failed to list tenants: {str(e)}")
            return []
    
    def update_tenant(self, tenant_id: str, updates: Dict) -> Optional[Dict]:
        """Update tenant information."""
        tenant_info = self.get_tenant(tenant_id)
        if not tenant_info:
            logger.error(f"Tenant not found: {tenant_id}")
            return None
        
        # Update tenant information
        for key, value in updates.items():
            if key != "tenant_id" and key != "created_at":  # Don't allow changing these fields
                tenant_info[key] = value
        
        # Update last modified timestamp
        tenant_info["last_modified"] = datetime.utcnow().isoformat()
        
        # Store updated configuration
        self._store_tenant_config(tenant_id, tenant_info)
        
        logger.info(f"Updated tenant: {tenant_id}")
        return tenant_info
    
    def deactivate_tenant(self, tenant_id: str) -> bool:
        """Deactivate a tenant (without deleting resources)."""
        tenant_info = self.get_tenant(tenant_id)
        if not tenant_info:
            logger.error(f"Tenant not found: {tenant_id}")
            return False
        
        # Update tenant status
        tenant_info["status"] = "inactive"
        tenant_info["deactivated_at"] = datetime.utcnow().isoformat()
        
        # Store updated configuration
        self._store_tenant_config(tenant_id, tenant_info)
        
        logger.info(f"Deactivated tenant: {tenant_id}")
        return True
    
    def delete_tenant(self, tenant_id: str) -> bool:
        """Delete a tenant and all associated resources."""
        try:
            # Clean up resources
            self._cleanup_tenant_resources(tenant_id)
            
            logger.info(f"Deleted tenant: {tenant_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete tenant {tenant_id}: {str(e)}")
            return False


# Example usage
if __name__ == "__main__":
    # This is just for demonstration
    manager = TenantManager()
    
    # Register a new tenant
    tenant = manager.register_tenant(
        tenant_name="Example Retail GmbH",
        prohandel_api_key="example_key",
        prohandel_api_secret="example_secret",
        contact_email="contact@example-retail.de",
        pos_system="ProHandel"
    )
    
    print(f"Registered tenant: {tenant}")
