# FastAPI DynamoDB Application

A comprehensive FastAPI application with DynamoDB backend, featuring advanced table configuration, migration system, and data seeding capabilities.

## 🚀 Features

- **Advanced Table Configuration**: Centralized table management with environment-specific naming
- **Migration System**: Database schema management with up/down migrations via API
- **Data Seeding**: Automated data population and cleanup via API endpoints
- **DynamoDB Integration**: Local DynamoDB with admin interface
- **Environment Support**: Multi-environment configuration (local, dev, staging, prod)
- **Comprehensive Logging**: Structured logging with proper error handling
- **Repository Pattern**: Clean data access layer with essential CRUD operations
- **Docker Support**: Complete Docker setup with DynamoDB Local and Admin UI
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
- [Migration System](#migration-system)
- [Seeder System](#seeder-system)
- [Table Configuration](#table-configuration)
- [Configuration](#configuration)
- [Development](#development)
- [Docker Services](#docker-services)

## 🚀 Quick Start

### Using Docker (Recommended)

1. **Start all services**:
   ```bash
   docker-compose up -d
   ```

2. **Access the services**:
   - **API**: http://localhost:8002
   - **API Documentation**: http://localhost:8002/docs
   - **DynamoDB Admin**: http://localhost:8001
   - **DynamoDB Local**: http://localhost:8000

3. **Run migrations to create tables**:
   ```bash
   curl -X POST http://localhost:8002/api/v1/migrations/run
   ```

4. **Seed initial data**:
   ```bash
   curl -X POST http://localhost:8002/api/v1/seeders/run
   ```

### Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start DynamoDB Local** (in separate terminal):
   ```bash
   docker run -p 8000:8000 amazon/dynamodb-local -jar DynamoDBLocal.jar -sharedDb
   ```

3. **Run the application**:
   ```bash
   # Using the development script (recommended - avoids log reload loops)
   python3 start_dev.py
   
   # Or using uvicorn directly
   uvicorn app.main:app --reload --port 8002
   ```

4. **Setup database via API**:
   ```bash
   # Run migrations
   curl -X POST http://localhost:8002/api/v1/migrations/run
   
   # Seed data
   curl -X POST http://localhost:8002/api/v1/seeders/run
   ```

## 🔗 API Endpoints

### Core APIs

#### Health Check
- `GET /health` - Application and database health status
- `GET /` - API information and available endpoints

#### Users
- `GET /api/v1/users/` - List users with optional filters
- `GET /api/v1/users/{user_id}` - Get user by ID
- `GET /api/v1/users/email/{email}` - Get user by email

### Migration APIs

#### Run Migrations (migrate:up)
```bash
POST /api/v1/migrations/run
```
Creates tables and applies schema changes to the database.

**Response Example**:
```json
{
  "success": true,
  "message": "Successfully ran 1 migrations",
  "data": {
    "migrations_run": 1,
    "total_migrations": 1,
    "status": "completed",
    "results": [
      {
        "migration": "migration_20241201_120000_create_users_table.py",
        "status": "success",
        "description": "Create users table with email GSI"
      }
    ]
  }
}
```

#### Rollback Migrations (migrate:down)
```bash
POST /api/v1/migrations/rollback
```
Deletes tables and reverts schema changes from the database.

#### Migration Status
```bash
GET /api/v1/migrations/status
```
Shows available migrations and their current status.

### Seeder APIs

#### Run Seeders
```bash
POST /api/v1/seeders/run
# Or run specific seeders
POST /api/v1/seeders/run?seeder_names=user_seeder
```
Populates database with initial or test data.

**Response Example**:
```json
{
  "success": true,
  "message": "Successfully ran 1 seeders",
  "data": {
    "seeders_run": 1,
    "total_seeders": 1,
    "status": "completed",
    "results": [
      {
        "seeder": "UserSeeder",
        "file": "user_seeder.py",
        "status": "success",
        "description": "Seeds initial user accounts (admin, test users)"
      }
    ],
    "environment": "local"
  }
}
```

#### Clear Seeders
```bash
POST /api/v1/seeders/clear
# Or clear specific seeders
POST /api/v1/seeders/clear?seeder_names=user_seeder
```
Removes seeded data from the database.

#### Seeder Status
```bash
GET /api/v1/seeders/status
```
Shows available seeders and their information.

## 🔄 Migration System

### Overview
The migration system provides database schema management through API endpoints, allowing you to create, modify, and rollback database changes programmatically.

### Available Migrations
- **CreateUsersTableMigration**: Creates the users table with proper indexes

### Creating New Migrations
1. Create a new file in `migrations/` directory following the naming pattern:
   ```
   migration_YYYYMMDD_HHMMSS_description.py
   ```

2. Implement the migration class:
   ```python
   from migrations.migration_manager import BaseMigration
   from app.config.tables import TableNames, TableSchemas
   
   class YourMigration(BaseMigration):
       @property
       def description(self) -> str:
           return "Your migration description"
       
       async def up(self):
           # Create/modify tables
           pass
       
       async def down(self):
           # Rollback changes
           pass
   ```

### Migration Workflow
1. **Check Status**: `GET /api/v1/migrations/status`
2. **Run Migrations**: `POST /api/v1/migrations/run`
3. **Rollback if needed**: `POST /api/v1/migrations/rollback`

## 🌱 Seeder System

### Overview
The seeder system provides automated data population and cleanup through API endpoints, perfect for setting up development environments or test data.

### Available Seeders
- **UserSeeder**: Creates initial user accounts with different roles
  - Admin user: `admin@nexpharmacorp.com` (password: `admin123!`)
  - Manager: `manager@nexpharmacorp.com` (password: `manager123!`)
  - Pharmacist: `pharmacist@nexpharmacorp.com` (password: `pharma123!`)
  - Analyst: `analyst@nexpharmacorp.com` (password: `analyst123!`)
  - Test users: Various test accounts

### Creating New Seeders
1. Create a new file in `seeders/` directory:
   ```
   your_seeder.py
   ```

2. Implement the seeder class:
   ```python
   from seeders.base_seeder import BaseSeeder
   
   class YourSeeder(BaseSeeder):
       @property
       def name(self) -> str:
           return "YourSeeder"
       
       @property
       def description(self) -> str:
           return "Description of what this seeder does"
       
       async def seed(self) -> bool:
           # Populate data
           return True
       
       async def clear(self) -> bool:
           # Clear data
           return True
   ```

### Seeder Workflow
1. **Check Status**: `GET /api/v1/seeders/status`
2. **Run Seeders**: `POST /api/v1/seeders/run`
3. **Clear Data**: `POST /api/v1/seeders/clear`

## 🏗️ Table Configuration

### Overview
Centralized table configuration system supporting multiple environments with automatic table naming and complete schema definitions.

### Supported Tables
- **users**: User management with email and role indexes
- **products**: Product catalog with category and name indexes
- **orders**: Order management with user and status indexes
- **categories**: Product categories with name and parent indexes
- **inventory**: Inventory tracking with product indexes
- **analytics**: Analytics data with event and timestamp indexes
- **audit-logs**: Audit logging with user and action indexes

### Environment Support
| Environment | Suffix | Example Table Name |
|-------------|--------|--------------------|
| Local | `local` | `users-local` |
| Development | `dev` | `users-dev` |
| Staging | `staging` | `users-staging` |
| Production | `prod` | `users-prod` |

### Usage Examples
```python
from app.config.tables import TableNames, TableConfig

# Get table names
users_table = TableNames.get_users_table("prod")  # "users-prod"

# Get complete schema
config = TableConfig("prod")
schema = config.get_schema("users")

# List all tables for environment
all_tables = config.list_table_names()
```

### Demo Script
Run the table configuration demo to see all features:
```bash
python3 scripts/table_config_demo.py
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Environment
ENVIRONMENT=development
TABLE_ENVIRONMENT=local

# Server
HOST=0.0.0.0
PORT=8002

# DynamoDB
DYNAMODB_ENDPOINT=http://localhost:8000
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=dummy
AWS_SECRET_ACCESS_KEY=dummy

# Security
SECRET_KEY=your-secret-key-here-change-in-production
```

### DynamoDB Admin Credentials

Access the DynamoDB admin interface at http://localhost:8001 with:
- **Endpoint**: `http://dynamodb-local:8000`
- **Region**: `us-east-1`
- **Access Key**: `dummy`
- **Secret Key**: `dummy`

## 🛠️ Development

### Project Structure
```
├── app/
│   ├── config/
│   │   ├── settings.py          # Application settings
│   │   └── tables.py           # Table configurations (NEW)
│   ├── controllers/
│   │   ├── user_controller.py
│   │   ├── migration_controller.py  # Migration API controller (NEW)
│   │   └── seeder_controller.py     # Seeder API controller (NEW)
│   ├── core/                   # Core utilities
│   ├── models/                 # Data models
│   ├── repositories/           # Data access layer
│   ├── routes/
│   │   ├── user_routes.py
│   │   ├── migration_routes.py      # Migration API routes (NEW)
│   │   └── seeder_routes.py         # Seeder API routes (NEW)
│   └── services/               # Business logic
├── migrations/                 # Database migrations
│   ├── migration_manager.py
│   └── migration_20241201_120000_create_users_table.py
├── seeders/                    # Database seeders (NEW)
│   ├── base_seeder.py
│   └── user_seeder.py
├── scripts/
│   ├── setup_database.py
│   └── table_config_demo.py    # Table config demo (NEW)
└── docs/
    └── table_configuration.md  # Detailed table config docs (NEW)
```

### Repository Methods

The repository includes these essential methods:

1. **`create(item)`** - Create a new item
2. **`find_one_by_query(query)`** - Find single item by query
3. **`find_all_by_query(query, limit)`** - Find all items by query
4. **`update_by_query(query, update_data)`** - Update item by query

### Testing APIs

#### Test Migration APIs
```bash
# Check migration status
curl -X GET http://localhost:8002/api/v1/migrations/status

# Run migrations
curl -X POST http://localhost:8002/api/v1/migrations/run

# Rollback migrations
curl -X POST http://localhost:8002/api/v1/migrations/rollback
```

#### Test Seeder APIs
```bash
# Check seeder status
curl -X GET http://localhost:8002/api/v1/seeders/status

# Run all seeders
curl -X POST http://localhost:8002/api/v1/seeders/run

# Run specific seeder
curl -X POST "http://localhost:8002/api/v1/seeders/run?seeder_names=user_seeder"

# Clear all seeded data
curl -X POST http://localhost:8002/api/v1/seeders/clear
```

### Logging

Comprehensive logging configuration:
- Console output for development
- File logging to `logs/app.log`
- Structured logging with context
- Error tracking with stack traces

## 🐳 Docker Services

- **app**: FastAPI application (port 8002)
- **dynamodb-local**: Local DynamoDB instance (port 8000)
- **dynamodb-admin**: Web-based DynamoDB admin interface (port 8001)

All services are connected via the `dynamodb-network` bridge network.

### Docker Commands
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down

# Rebuild and start
docker-compose up -d --build
```

## 📚 Additional Resources

- **API Documentation**: Visit `/docs` for interactive Swagger UI
- **Table Configuration Guide**: See `docs/table_configuration.md`
- **Migration Examples**: Check `migrations/` directory
- **Seeder Examples**: Check `seeders/` directory

## 🔧 Troubleshooting

### Common Issues

1. **DynamoDB Connection Failed**:
   ```bash
   # Check if DynamoDB Local is running
   docker ps | grep dynamodb
   
   # Test connection
   python test_dynamodb_connection.py
   ```

2. **Migration/Seeder Import Errors**:
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python path configuration in migration/seeder files

3. **Port Conflicts**:
   - Default ports: 8000 (DynamoDB), 8001 (Admin), 8002 (API)
   - Modify `docker-compose.yml` if ports are in use

### Getting Help

- Check the logs: `docker-compose logs -f app`
- Visit the API documentation: http://localhost:8002/docs
- Test the health endpoint: http://localhost:8002/health

---

## 🎉 What's New

### v2.0 Features
- ✅ **Centralized Table Configuration**: Environment-specific table management
- ✅ **Migration APIs**: Database schema management via REST endpoints
- ✅ **Seeder APIs**: Data population and cleanup via REST endpoints
- ✅ **Multi-Environment Support**: Local, dev, staging, prod configurations
- ✅ **Enhanced Documentation**: Comprehensive API and system documentation

This application now provides a complete database management solution with API-driven migrations and seeding capabilities!
