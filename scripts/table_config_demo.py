#!/usr/bin/env python3
"""
Table Configuration Demo Script
Demonstrates how to use the new centralized table configuration system
"""

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.config.tables import TableConfig, TableNames, TableEnvironment

def demo_table_configuration():
    """Demonstrate the table configuration system"""
    
    print("🏗️  DynamoDB Table Configuration Demo")
    print("=" * 50)
    
    # 1. Show different environments
    print("\n1. Table Names for Different Environments:")
    print("-" * 40)
    
    environments = ["local", "dev", "staging", "prod"]
    for env in environments:
        users_table = TableNames.get_users_table(env)
        projects_table = TableNames.get_projects_table(env)
        
        print(f"  {env.upper()}:")
        print(f"    - Users: {users_table}")
        print(f"    - Projects: {projects_table}")
    
    # 2. Show table configuration for local environment
    print("\n2. Table Configuration (Local Environment):")
    print("-" * 40)
    
    table_config = TableConfig("local")
    
    print(f"  Environment: {table_config.environment}")
    print(f"  All table names: {table_config.list_table_names()}")
    
    # 3. Show schema details for users table
    print("\n3. Users Table Schema Details:")
    print("-" * 40)
    
    users_schema = table_config.get_schema(TableNames.USERS)
    
    print(f"  Table Name: {users_schema['table_name']}")
    print(f"  Billing Mode: {users_schema['billing_mode']}")
    print(f"  Key Schema: {users_schema['key_schema']}")
    print(f"  Attribute Definitions: {len(users_schema['attribute_definitions'])} attributes")
    print(f"  Global Secondary Indexes: 0 indexes (primary key only)")
    
    # 4. Show all available schemas
    print("\n4. All Available Table Schemas:")
    print("-" * 40)
    
    all_schemas = table_config.get_all_schemas()
    for table_name, schema in all_schemas.items():
        print(f"  - {table_name}: 0 GSIs (primary key only)")
    
    # 5. Show how to use in different environments
    print("\n5. Environment-Specific Configuration:")
    print("-" * 40)
    
    for env in ["local", "prod"]:
        config = TableConfig(env)
        users_table = config.get_table_name(TableNames.USERS)
        print(f"  {env.upper()}: Users table = {users_table}")
    
    # 6. Show schema structure for different tables
    print("\n6. Schema Comparison:")
    print("-" * 40)
    
    table_types = [TableNames.USERS, TableNames.PROJECTS_DETAILS]
    
    for table_type in table_types:
        try:
            schema = table_config.get_schema(table_type)
            key_count = len(schema['key_schema'])
            attr_count = len(schema['attribute_definitions'])
            
            print(f"  {table_type.upper()}:")
            print(f"    - Keys: {key_count}, Attributes: {attr_count}, GSIs: 0 (primary key only)")
            
            # Show key schema details
            for key in schema['key_schema']:
                key_type = "PK" if key['KeyType'] == 'HASH' else "SK"
                print(f"    - {key_type}: {key['AttributeName']}")
                
        except ValueError as e:
            print(f"  {table_type.upper()}: {str(e)}")
    
    print("\n✅ Demo completed! The simplified table configuration system provides:")
    print("   - Clean separation: Only required tables (users, projects_details)")
    print("   - Individual table files for better organization")
    print("   - Environment-specific naming")
    print("   - Complete schema configurations")
    print("   - Easy schema retrieval and management")
    print("\n📚 Usage in your code:")
    print("   from app.config.tables import TableNames, TableConfig")
    print("   from app.config.tables.users_table import UsersTableConfig")
    print("   from app.config.tables.projects_table import ProjectsTableConfig")
    print("   ")
    print("   # Get table names")
    print("   users_table = TableNames.get_users_table('prod')")
    print("   projects_table = TableNames.get_projects_table('prod')")
    print("   ")
    print("   # Get schemas directly from table configs")
    print("   users_schema = UsersTableConfig.get_schema('prod')")
    print("   projects_schema = ProjectsTableConfig.get_schema('prod')")

if __name__ == "__main__":
    demo_table_configuration() 