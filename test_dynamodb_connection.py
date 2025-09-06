#!/usr/bin/env python3
"""
Test script to verify DynamoDB Local connection
Run this to ensure your DynamoDB Local container is working properly
"""

import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import dynamodb_client
from app.config.settings import settings
from app.config.tables import TableNames, TableSchemas

def test_dynamodb_connection():
    """Test DynamoDB Local connection and setup"""
    print("🔍 Testing DynamoDB Local Connection...")
    print(f"📍 Endpoint: {settings.DYNAMODB_ENDPOINT}")
    print(f"🌍 Region: {settings.AWS_REGION}")
    print(f"🏷️  Environment: {settings.ENVIRONMENT}")
    print("-" * 50)
    
    try:
        # Test basic connection
        print("1. Testing basic connection...")
        health = dynamodb_client.health_check()
        
        if health['status'] == 'healthy':
            print("✅ Connection successful!")
            print(f"   Response time: {health['response_time_seconds']}s")
            print(f"   Total tables: {health['total_tables']}")
        else:
            print("❌ Connection failed!")
            print(f"   Error: {health.get('error', 'Unknown error')}")
            return False
            
        # List existing tables
        print("\n2. Listing existing tables...")
        tables = dynamodb_client.list_tables()
        if tables:
            print(f"   Found {len(tables)} tables:")
            for table in tables:
                print(f"   - {table}")
        else:
            print("   No tables found (this is normal for a fresh setup)")
            
        # Test table creation (users table)
        users_table_name = TableNames.get_users_table(settings.TABLE_ENVIRONMENT)
        print(f"\n3. Testing table creation ({users_table_name})...")
        try:
            table_exists = False
            try:
                dynamodb_client.get_table(users_table_name)
                table_exists = True
                print(f"   ✅ Table '{users_table_name}' already exists")
            except:
                print(f"   📝 Table '{users_table_name}' doesn't exist, creating...")
                
            if not table_exists:
                # Create users table using schema configuration
                users_schema = TableSchemas.USERS_SCHEMA
                success = dynamodb_client.create_table(
                    table_name=users_table_name,
                    key_schema=users_schema["key_schema"],
                    attribute_definitions=users_schema["attribute_definitions"],
                    billing_mode=users_schema["billing_mode"]
                )
                
                if success:
                    print(f"   ✅ Table '{users_table_name}' created successfully!")
                else:
                    print(f"   ⚠️  Table '{users_table_name}' already existed")
                    
        except Exception as e:
            print(f"   ❌ Error with table operations: {str(e)}")
            
        # Final health check
        print("\n4. Final health check...")
        final_health = dynamodb_client.health_check()
        
        if final_health['status'] == 'healthy':
            print("✅ All tests passed! DynamoDB Local is ready to use.")
            print("\n🎉 Setup Summary:")
            print(f"   - DynamoDB Local: {settings.DYNAMODB_ENDPOINT}")
            print(f"   - Users Table: {users_table_name}")
            print(f"   - Total Tables: {final_health['total_tables']}")
            return True
        else:
            print("❌ Final health check failed!")
            return False
            
    except Exception as e:
        print(f"❌ Connection test failed: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure DynamoDB Local container is running:")
        print("      docker ps | grep dynamodb")
        print("   2. Check if port 8000 is accessible:")
        print("      curl http://localhost:8000")
        print("   3. Verify container logs:")
        print("      docker logs <container_name>")
        return False

if __name__ == "__main__":
    success = test_dynamodb_connection()
    sys.exit(0 if success else 1) 