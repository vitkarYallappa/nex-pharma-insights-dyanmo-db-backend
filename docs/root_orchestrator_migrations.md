# Root Orchestrator DynamoDB Migrations

This document describes the DynamoDB table migrations for the Root Orchestrator system.

## Overview

The Root Orchestrator system requires 2 primary DynamoDB tables:

1. **market_intelligence_requests** - Main requests table for managing intelligence requests
2. **request_processing_logs** - Processing logs and audit trail (optional)

## Migration Files

### 1. Market Intelligence Requests Table
- **File**: `migration_20241201_122000_create_market_intelligence_requests_table.py`
- **Description**: Creates the main requests table with all Global Secondary Indexes
- **Table Name**: `{environment}-market_intelligence_requests`

#### Global Secondary Indexes:
- `user-index` - Query by user_id and created_at
- `project-index` - Query by project_id and created_at  
- `status-index` - Query by status and created_at
- `strategy-index` - Query by processing_strategy and priority

### 2. Request Processing Logs Table
- **File**: `migration_20241201_122100_create_request_processing_logs_table.py`
- **Description**: Creates the processing logs table for audit trail
- **Table Name**: `{environment}-request_processing_logs`

#### Global Secondary Indexes:
- `request-logs-index` - Query logs by request_id and timestamp

## Running Migrations

### Using the Dedicated Script (Recommended)

```bash
# Run Root Orchestrator migrations
python scripts/run_root_orchestrator_migrations.py migrate

# Check migration status
python scripts/run_root_orchestrator_migrations.py status

# Rollback migrations (⚠️ This will delete tables!)
python scripts/run_root_orchestrator_migrations.py rollback
```

### Using the General Migration Manager

```bash
# Run all pending migrations (including Root Orchestrator)
python migrations/migration_manager.py migrate

# Run specific migration
python migrations/migration_manager.py migrate --target migration_20241201_122000_create_market_intelligence_requests_table

# Check overall migration status
python migrations/migration_manager.py status
```

## Environment-Specific Table Names

The tables are created with environment-specific prefixes:

- **Development**: `dev-market_intelligence_requests`, `dev-request_processing_logs`
- **Staging**: `staging-market_intelligence_requests`, `staging-request_processing_logs`
- **Production**: `prod-market_intelligence_requests`, `prod-request_processing_logs`

## Table Configurations

The table schemas are defined in:
- `app/config/table_configs/market_intelligence_requests_table.py`
- `app/config/table_configs/request_processing_logs_table.py`

## Sample Data

In development environment, the migrations will create sample data:

### Market Intelligence Requests
- Sample request with semaglutide intelligence configuration
- Includes keywords, sources, and processing configuration
- Status tracking and progress monitoring fields

### Request Processing Logs
- Sample log entries showing different log levels
- Processing stages and metadata
- Associated with sample request

## Query Patterns

### Common Queries for Market Intelligence Requests

```python
# Get request by ID
response = dynamodb.get_item(
    TableName='dev-market_intelligence_requests',
    Key={'request_id': {'S': 'req_1757412789250_a08ac7ad'}}
)

# Get requests by user
response = dynamodb.query(
    TableName='dev-market_intelligence_requests',
    IndexName='user-index',
    KeyConditionExpression='user_id = :user_id',
    ExpressionAttributeValues={':user_id': {'S': 'test-user-123'}}
)

# Get pending requests
response = dynamodb.query(
    TableName='dev-market_intelligence_requests',
    IndexName='status-index',
    KeyConditionExpression='#status = :status',
    ExpressionAttributeNames={'#status': 'status'},
    ExpressionAttributeValues={':status': {'S': 'pending'}}
)

# Get requests by processing strategy and priority
response = dynamodb.query(
    TableName='dev-market_intelligence_requests',
    IndexName='strategy-index',
    KeyConditionExpression='processing_strategy = :strategy',
    ExpressionAttributeValues={':strategy': {'S': 'table'}},
    ScanIndexForward=False  # Descending order by priority
)
```

### Common Queries for Processing Logs

```python
# Get logs for a specific request
response = dynamodb.query(
    TableName='dev-request_processing_logs',
    IndexName='request-logs-index',
    KeyConditionExpression='request_id = :request_id',
    ExpressionAttributeValues={':request_id': {'S': 'req_1757412789250_a08ac7ad'}},
    ScanIndexForward=True  # Ascending order by timestamp
)
```

## Troubleshooting

### Migration Fails
1. Check AWS credentials and permissions
2. Verify DynamoDB service is available in your region
3. Check the logs in `logs/` directory
4. Ensure no table name conflicts

### Table Already Exists Error
- The migration will skip creation if table already exists
- Use `status` command to check current state
- Use `rollback` to delete and recreate if needed

### Permission Issues
Ensure your AWS credentials have the following permissions:
- `dynamodb:CreateTable`
- `dynamodb:DeleteTable`
- `dynamodb:DescribeTable`
- `dynamodb:PutItem`
- `dynamodb:GetItem`
- `dynamodb:Query`
- `dynamodb:Scan`

## Rollback Considerations

⚠️ **Warning**: Rollback will permanently delete the tables and all data!

- Always backup important data before rollback
- Rollback runs in reverse order (logs table first, then requests table)
- Test rollback in development environment first

## Next Steps

After running the migrations:

1. Verify tables are created in AWS Console
2. Test basic CRUD operations
3. Set up monitoring and alarms
4. Configure backup policies
5. Implement TTL for log cleanup (optional)

## Support

For issues with migrations:
1. Check the migration logs
2. Verify AWS configuration
3. Review table configurations
4. Test with a minimal example 