"""
Database Configuration and Connection Management
Handles DynamoDB connections and table operations with logging
"""

import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError, NoCredentialsError
from app.config.settings import settings
from app.core.logging import get_logger
from typing import Optional, Dict, Any
import time

logger = get_logger("database")

class DynamoDBClient:
    """DynamoDB client with enhanced logging and error handling"""
    
    def __init__(self):
        self.dynamodb = None
        self.tables_cache = {}
        self.initialized = False
    
    def _initialize_client(self):
        """Initialize DynamoDB client with proper configuration"""
        if self.initialized:
            return
            
        try:
            if settings.is_development and settings.DYNAMODB_ENDPOINT:
                logger.info(f"Connecting to local DynamoDB at {settings.DYNAMODB_ENDPOINT}")
                self.dynamodb = boto3.resource(
                    'dynamodb',
                    endpoint_url=settings.DYNAMODB_ENDPOINT,
                    region_name=settings.AWS_REGION,
                    aws_access_key_id='dummy',
                    aws_secret_access_key='dummy'
                )
            else:
                logger.info(f"Connecting to AWS DynamoDB in region {settings.AWS_REGION}")
                if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
                    self.dynamodb = boto3.resource(
                        'dynamodb',
                        region_name=settings.AWS_REGION,
                        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                    )
                else:
                    # Use default credentials (IAM role, environment, etc.)
                    self.dynamodb = boto3.resource(
                        'dynamodb',
                        region_name=settings.AWS_REGION
                    )
            
            # Test connection
            self._test_connection()
            logger.info("DynamoDB client initialized successfully")
            self.initialized = True
            
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            raise Exception("AWS credentials not configured properly")
        except Exception as e:
            logger.error(f"Failed to initialize DynamoDB client: {str(e)}")
            raise Exception(f"Database connection failed: {str(e)}")
    
    def _test_connection(self):
        """Test DynamoDB connection"""
        try:
            # Try to list tables as a connection test
            start_time = time.time()
            list(self.dynamodb.tables.all())
            end_time = time.time()
            logger.info(f"DynamoDB connection test successful ({end_time - start_time:.2f}s)")
        except Exception as e:
            logger.error(f"DynamoDB connection test failed: {str(e)}")
            raise
    
    def get_table(self, table_name: str):
        """Get DynamoDB table with caching and validation"""
        if not self.initialized:
            self._initialize_client()
            
        try:
            if table_name not in self.tables_cache:
                logger.debug(f"Getting table: {table_name}")
                table = self.dynamodb.Table(table_name)
                
                # Validate table exists and is active
                table.load()
                if table.table_status != 'ACTIVE':
                    raise Exception(f"Table {table_name} is not active (status: {table.table_status})")
                
                self.tables_cache[table_name] = table
                logger.debug(f"Table {table_name} cached successfully")
            
            return self.tables_cache[table_name]
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                logger.error(f"Table {table_name} does not exist")
                raise Exception(f"Table {table_name} not found")
            else:
                logger.error(f"Error accessing table {table_name}: {str(e)}")
                raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting table {table_name}: {str(e)}")
            raise
    
    def create_table(self, table_name: str, key_schema: list, attribute_definitions: list, 
                    billing_mode: str = 'PAY_PER_REQUEST', **kwargs) -> bool:
        """Create a DynamoDB table with logging"""
        try:
            logger.info(f"Creating table: {table_name}")
            
            table_config = {
                'TableName': table_name,
                'KeySchema': key_schema,
                'AttributeDefinitions': attribute_definitions,
                'BillingMode': billing_mode
            }
            
            # Add any additional configuration
            table_config.update(kwargs)
            
            table = self.dynamodb.create_table(**table_config)
            
            # Wait for table to be created
            logger.info(f"Waiting for table {table_name} to be active...")
            table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
            
            logger.info(f"Table {table_name} created successfully")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceInUseException':
                logger.warning(f"Table {table_name} already exists")
                return False
            else:
                logger.error(f"Error creating table {table_name}: {str(e)}")
                raise Exception(f"Failed to create table: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error creating table {table_name}: {str(e)}")
            raise
    
    def delete_table(self, table_name: str) -> bool:
        """Delete a DynamoDB table with logging"""
        try:
            logger.warning(f"Deleting table: {table_name}")
            
            table = self.dynamodb.Table(table_name)
            table.delete()
            
            # Wait for table to be deleted
            logger.info(f"Waiting for table {table_name} to be deleted...")
            table.meta.client.get_waiter('table_not_exists').wait(TableName=table_name)
            
            # Remove from cache
            if table_name in self.tables_cache:
                del self.tables_cache[table_name]
            
            logger.info(f"Table {table_name} deleted successfully")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                logger.warning(f"Table {table_name} does not exist")
                return False
            else:
                logger.error(f"Error deleting table {table_name}: {str(e)}")
                raise Exception(f"Failed to delete table: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error deleting table {table_name}: {str(e)}")
            raise
    
    def list_tables(self) -> list:
        """List all DynamoDB tables"""
        try:
            logger.debug("Listing all tables")
            tables = [table.name for table in self.dynamodb.tables.all()]
            logger.debug(f"Found {len(tables)} tables: {tables}")
            return tables
        except Exception as e:
            logger.error(f"Error listing tables: {str(e)}")
            raise
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get detailed table information"""
        try:
            table = self.get_table(table_name)
            table.reload()
            
            info = {
                'table_name': table.table_name,
                'table_status': table.table_status,
                'item_count': table.item_count,
                'table_size_bytes': table.table_size_bytes,
                'creation_date_time': table.creation_date_time,
                'key_schema': table.key_schema,
                'attribute_definitions': table.attribute_definitions
            }
            
            logger.debug(f"Retrieved info for table {table_name}")
            return info
            
        except Exception as e:
            logger.error(f"Error getting table info for {table_name}: {str(e)}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """Perform database health check"""
        try:
            if not self.initialized:
                self._initialize_client()
                
            start_time = time.time()
            
            # Test basic connectivity
            tables = [table.name for table in self.dynamodb.tables.all()]
            
            # Test table access for configured tables
            table_status = {}
            configured_tables = [settings.USERS_TABLE]
            
            for table_name in configured_tables:
                try:
                    table = self.get_table(table_name)
                    table_status[table_name] = "healthy"
                except Exception as e:
                    table_status[table_name] = f"error: {str(e)}"
            
            end_time = time.time()
            response_time = end_time - start_time
            
            health_info = {
                'status': 'healthy',
                'response_time_seconds': round(response_time, 3),
                'total_tables': len(tables),
                'configured_tables': table_status,
                'endpoint': settings.DYNAMODB_ENDPOINT if settings.is_development else 'AWS DynamoDB',
                'region': settings.AWS_REGION
            }
            
            logger.info(f"Database health check completed successfully ({response_time:.3f}s)")
            return health_info
            
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'endpoint': settings.DYNAMODB_ENDPOINT if settings.is_development else 'AWS DynamoDB',
                'region': settings.AWS_REGION
            }

# Singleton instance
dynamodb_client = DynamoDBClient()

# Convenience function for getting tables
def get_table(table_name: str):
    """Convenience function to get a table"""
    return dynamodb_client.get_table(table_name)