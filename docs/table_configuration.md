# DynamoDB Table Configuration System

## 📋 Overview

This document describes the DynamoDB table configuration system for the Nex Pharma Insights application. The system is designed for **simplicity and speed** with tables using **primary keys only** - no Global Secondary Indexes (GSIs) for faster table creation and reduced complexity.

## 🏗️ Architecture

### Directory Structure
```
app/config/
├── tables.py                    # Main configuration orchestrator
├── table_configs/              # Individual table configurations
│   ├── __init__.py
│   ├── users_table.py          # Users table configuration
│   └── projects_table.py       # Projects table configuration
└── settings.py                 # Environment settings
```

## 📊 Current Tables

### 1. Users Table (`users`)

**Purpose**: User management and authentication

**Schema**:
```json
{
  "table_name": "users",
  "key_schema": [
    {"AttributeName": "pk", "KeyType": "HASH"}
  ],
  "attribute_definitions": [
    {"AttributeName": "pk", "AttributeType": "S"}
  ],
  "billing_mode": "PAY_PER_REQUEST"
}
```

**Configuration File**: `app/config/table_configs/users_table.py`

### 2. Projects Details Table (`projects_details`)

**Purpose**: Project information and tracking

**Schema**:
```json
{
  "table_name": "projects_details",
  "key_schema": [
    {"AttributeName": "pk", "KeyType": "HASH"}
  ],
  "attribute_definitions": [
    {"AttributeName": "pk", "AttributeType": "S"}
  ],
  "billing_mode": "PAY_PER_REQUEST"
}
```

**Configuration File**: `app/config/table_configs/projects_table.py`

## 🌍 Environment Support

Tables use consistent names across all environments:

| Table | Name |
|-------|------|
| **Users** | `users` |
| **Projects** | `projects_details` |

## 💻 Usage Examples

### Basic Usage

```python
from app.config.tables import TableNames, TableConfig

# Get environment-specific table names
users_table = TableNames.get_users_table('prod')
projects_table = TableNames.get_projects_table('prod')

# Initialize table configuration
table_config = TableConfig(environment='prod')

# Get all table names
all_tables = table_config.list_table_names()
# Returns: ['users-prod', 'projects_details-prod']
```

### Direct Table Configuration Access

```python
from app.config.table_configs.users_table import UsersTableConfig
from app.config.table_configs.projects_table import ProjectsTableConfig

# Get table names
users_table = UsersTableConfig.get_table_name('local')
projects_table = ProjectsTableConfig.get_table_name('local')

# Get complete schemas
users_schema = UsersTableConfig.get_schema('local')
projects_schema = ProjectsTableConfig.get_schema('local')

# Get descriptions
users_desc = UsersTableConfig.get_description()
projects_desc = ProjectsTableConfig.get_description()
```

### Schema Retrieval

```python
from app.config.tables import TableConfig

table_config = TableConfig(environment='local')

# Get specific table schema
users_schema = table_config.get_schema('users')

# Get all schemas
all_schemas = table_config.get_all_schemas()

# Get table information
table_info = table_config.get_table_info()
```

## 🔧 Configuration Classes

### TableConfig Class

Main orchestrator for table configuration management.

**Methods**:
- `get_table_name(base_name: str) -> str`: Get environment-specific table name
- `get_schema(table_name: str) -> Dict[str, Any]`: Get table schema
- `get_all_schemas() -> Dict[str, Dict[str, Any]]`: Get all table schemas
- `list_table_names() -> List[str]`: List all environment-specific table names
- `list_available_tables() -> List[str]`: List base table names
- `get_table_info() -> Dict[str, Dict[str, Any]]`: Get table information summary

### Individual Table Config Classes

Each table has its own configuration class with these methods:

**UsersTableConfig** / **ProjectsTableConfig**:
- `get_table_name(environment: str) -> str`: Get environment-specific name
- `get_schema(environment: str) -> Dict[str, Any]`: Get complete schema
- `get_description() -> str`: Get table description

## 🚀 Migration Integration

The table configuration integrates seamlessly with the migration system:

```python
# In migration files
from app.config.table_configs.users_table import UsersTableConfig

class CreateUsersTableMigration:
    def up(self):
        schema = UsersTableConfig.get_schema()
        table_name = UsersTableConfig.get_table_name()
        # Create table using schema...
```

## 📝 Adding New Tables

To add a new table to the system:

### 1. Create Table Configuration File

Create `app/config/table_configs/new_table.py`:

```python
from typing import Dict, Any

class NewTableConfig:
    TABLE_NAME = "new_table"
    
    SCHEMA = {
        "table_name": TABLE_NAME,
        "key_schema": [
            {"AttributeName": "pk", "KeyType": "HASH"}
        ],
        "attribute_definitions": [
            {"AttributeName": "pk", "AttributeType": "S"}
        ],
        "billing_mode": "PAY_PER_REQUEST"
    }
    
    @classmethod
    def get_table_name(cls, environment: str = "local") -> str:
        return f"{cls.TABLE_NAME}-{environment}"
    
    @classmethod
    def get_schema(cls, environment: str = "local") -> Dict[str, Any]:
        schema = cls.SCHEMA.copy()
        schema["table_name"] = cls.get_table_name(environment)
        return schema
    
    @classmethod
    def get_description(cls) -> str:
        return "Description of the new table"
```

### 2. Update Main Configuration

Add to `app/config/table_configs/__init__.py`:
```python
from .new_table import NewTableConfig
__all__ = ["UsersTableConfig", "ProjectsTableConfig", "NewTableConfig"]
```

Add to `app/config/tables.py`:
```python
from .table_configs.new_table import NewTableConfig

class TableNames:
    NEW_TABLE = "new_table"
    
    @classmethod
    def get_new_table(cls, environment: str = "local") -> str:
        return NewTableConfig.get_table_name(environment)
```

### 3. Create Migration

Create migration file following the existing pattern in `migrations/` directory.

## 🎯 Design Principles

### 1. **Simplicity First**
- Primary keys only - no Global Secondary Indexes
- Minimal attribute definitions
- Fast table creation and deletion

### 2. **Environment Isolation**
- Clear separation between environments
- Consistent naming conventions
- Easy environment switching

### 3. **Modular Configuration**
- Each table in its own file
- Reusable configuration classes
- Clean separation of concerns

### 4. **Developer Experience**
- Intuitive API design
- Comprehensive error handling
- Clear documentation and examples

## 🔍 Testing Configuration

Use the demo script to test the configuration:

```bash
python3 scripts/table_config_demo.py
```

This will show:
- Table names for all environments
- Schema details
- Configuration validation
- Usage examples

## 🚨 Important Notes

### Performance Considerations
- **No GSIs**: Tables use primary key access only for maximum speed
- **PAY_PER_REQUEST**: Billing mode optimized for variable workloads
- **Simple Schema**: Minimal overhead for table operations

### Environment Variables
Set the table environment in your `.env` file:
```
# TABLE_ENVIRONMENT is no longer used - tables have consistent names
```

### Migration Best Practices
- Always test migrations in local environment first
- Use the migration APIs for consistent table management
- Keep migration files focused on single table operations

## 📚 API Integration

The table configuration works with these API endpoints:

### Migration APIs
- `POST /api/v1/migrations/run` - Create all tables
- `POST /api/v1/migrations/rollback` - Delete all tables  
- `GET /api/v1/migrations/status` - Check migration status

### Seeder APIs
- `POST /api/v1/seeders/run` - Populate tables with sample data
- `POST /api/v1/seeders/clear` - Remove seeded data
- `GET /api/v1/seeders/status` - Check seeder status

## 🛠️ Troubleshooting

### Common Issues

1. **Table Not Found**: Ensure DynamoDB Local is running and tables are created via migrations
2. **Import Errors**: Check that table config files are in the correct directory structure
3. **Table Names**: All tables now use consistent names without environment suffixes

### Debug Commands

```bash
# Test table configuration
python3 scripts/table_config_demo.py

# Check migration status
curl http://localhost:8002/api/v1/migrations/status

# Test DynamoDB connection
python3 test_dynamodb_connection.py
```

## 📈 Future Enhancements

While the current system focuses on simplicity with primary keys only, future enhancements could include:

- **Optional GSI Support**: Add GSIs when specific query patterns require them
- **Composite Keys**: Support for sort keys when needed
- **Table Relationships**: Configuration for table relationships and foreign keys
- **Auto-scaling**: Configuration for provisioned throughput and auto-scaling
- **Backup Configuration**: Automated backup and restore settings

---

**Last Updated**: December 2024  
**Version**: 2.0 (Simplified - Primary Keys Only) 