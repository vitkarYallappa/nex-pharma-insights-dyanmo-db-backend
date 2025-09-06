"""
Simple Database Setup Script
Creates required DynamoDB tables for the application
"""

import boto3
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.config.settings import settings
from app.config.tables import TableNames, TableSchemas
from app.core.logging import get_logger

logger = get_logger("setup_database")

def create_dynamodb_client():
    """Create DynamoDB client"""
    if settings.is_development and settings.DYNAMODB_ENDPOINT:
        return boto3.resource(
            'dynamodb',
            endpoint_url=settings.DYNAMODB_ENDPOINT,
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
    else:
        return boto3.resource(
            'dynamodb',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )

def create_users_table(dynamodb):
    """Create users table using schema configuration"""
    table_name = TableNames.get_users_table(settings.TABLE_ENVIRONMENT)
    users_schema = TableSchemas.USERS_SCHEMA
    
    try:
        # Check if table already exists
        existing_tables = [table.name for table in dynamodb.tables.all()]
        if table_name in existing_tables:
            logger.info(f"Table {table_name} already exists")
            return True
        
        # Create table using schema configuration
        logger.info(f"Creating table: {table_name}")
        
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=users_schema["key_schema"],
            AttributeDefinitions=users_schema["attribute_definitions"],
            BillingMode=users_schema["billing_mode"]
        )
        
        # Wait for table to be created
        logger.info(f"Waiting for table {table_name} to be active...")
        table.wait_until_exists()
        
        logger.info(f"Table {table_name} created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error creating table {table_name}: {str(e)}")
        return False

def main():
    """Main setup function"""
    logger.info("Starting database setup...")
    
    try:
        # Create DynamoDB client
        dynamodb = create_dynamodb_client()
        logger.info("Connected to DynamoDB")
        
        # Create tables
        success = create_users_table(dynamodb)
        
        if success:
            logger.info("Database setup completed successfully")
        else:
            logger.error("Database setup failed")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Database setup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()