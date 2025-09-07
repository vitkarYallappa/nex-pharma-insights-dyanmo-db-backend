# Project Request Creation Orchestrator

## Overview

The Project Request Creation Orchestrator is a comprehensive service that handles the complete workflow for creating project requests with all related entities. It follows a structured sequence:

**Project → Request → Keywords → Source URLs → Statistics Tables**

This orchestrator ensures data consistency, proper logging, and error handling throughout the entire process.

## Features

- **Sequential Creation**: Creates entities in the correct order with proper relationships
- **Comprehensive Logging**: Detailed logging with orchestration IDs for tracking
- **Error Handling**: Graceful error handling with detailed error messages
- **Flexible Usage**: Supports both new project creation and adding requests to existing projects
- **Atomic Operations**: Each step is logged and can be tracked individually
- **Validation**: Comprehensive input validation at each step

## Architecture

### Core Components

1. **ProjectRequestCreationOrchestrator**: Main orchestrator class
2. **Individual Services**: Uses existing service classes for each entity type
3. **Models**: Leverages existing Pydantic models for data validation
4. **Logging**: Structured logging with orchestration IDs

### Service Dependencies

```
ProjectRequestCreationOrchestrator
├── ProjectService (projects table)
├── RequestsService (requests table)  
├── KeywordsService (keywords table)
├── SourceUrlsService (source_urls table)
├── ProjectRequestStatisticsService (project_request_statistics table)
└── ProjectModulesStatisticsService (project_modules_statistics table)
```

## API Endpoint

### POST `/projects/request`

Creates a complete project request with all related entities.

#### Request Body

```json
{

    "title": "Semaglutide and Tirzepatide Market Intelligence",
    "description": "Monitor market developments for Wegovy (Semaglutide) and emerging Tirzepatide therapies",
    "time_range": {
        "start": "2024-01-01",
        "end": "2025-12-31",
        "date_range": "2024-01-01 to 2025-12-31"
    },
    "priority": "high",
    "created_by": "user-uuid-here",
    "keywords": [
        "semaglutide",
        "tirzepatide",
        "wegovy",
        "obesity drug",
        "weight loss medication",
        "GLP-1 receptor agonist",
        "diabetes treatment",
        "clinical trials obesity"
    ],
    "base_urls": [
        {
            "source_type": "government",
            "source_name": "FDA",
            "url": "https://www.fda.gov"
        },
        {
            "source_type": "academic",
            "source_name": "NIH",
            "url": "https://www.nih.gov"
        },
        {
            "source_type": "clinical",
            "source_name": "ClinicalTrials.gov",
            "url": "https://clinicaltrials.gov"
        }
    ]
}
```

#### Response

```json
{
    "status": "success",
    "message": "Project request created successfully with all related entities",
    "data": {
        "project": {
            "id": "project-uuid",
            "name": "Semaglutide and Tirzepatide Market Intelligence",
            "description": "Monitor market developments...",
            "created_by": "user-uuid",
            "status": "active",
            "created_at": "2024-01-01T10:00:00Z"
        },
        "request": {
            "id": "request-uuid",
            "project_id": "project-uuid",
            "title": "Semaglutide and Tirzepatide Market Intelligence",
            "description": "Monitor market developments...",
            "priority": "high",
            "status": "pending",
            "created_at": "2024-01-01T10:00:00Z"
        },
        "keywords": [
            {
                "id": "keyword-uuid-1",
                "keyword": "semaglutide",
                "request_id": "request-uuid",
                "keyword_type": "user_defined"
            }
            // ... more keywords
        ],
        "source_urls": [
            {
                "id": "url-uuid-1",
                "request_id": "request-uuid",
                "url": "https://www.fda.gov",
                "source_name": "FDA",
                "source_type": "government",
                "is_active": true
            }
            // ... more URLs
        ],
        "orchestration_id": "abc12345",
        "created_at": "2024-01-01T10:00:00Z"
    },
    "request_id": "req-12345"
}
```

## Usage Examples

### 1. Create New Project with Request

```bash
curl -X POST "http://localhost:8000/projects/request" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Market Intelligence Project",
    "description": "Comprehensive market analysis",
    "priority": "high",
    "created_by": "user-123",
    "keywords": ["market", "analysis", "intelligence"],
    "base_urls": [
      {
        "source_type": "government",
        "source_name": "FDA",
        "url": "https://www.fda.gov"
      }
    ]
  }'
```

### 2. Add Request to Existing Project

```bash
curl -X POST "http://localhost:8000/projects/request" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "existing-project-uuid",
    "title": "Additional Analysis Request",
    "description": "Extended analysis for existing project",
    "priority": "medium",
    "created_by": "user-123",
    "keywords": ["extended", "analysis"],
    "base_urls": []
  }'
```

## Orchestration Flow

### New Project Creation Flow

1. **Validate Input**: Check required fields and data format
2. **Create Project**: Create new project record
3. **Create Request**: Create request linked to the project
4. **Create Keywords**: Add each keyword individually with logging
5. **Create Source URLs**: Add each URL individually with logging
6. **Create Statistics**: Initialize project request and modules statistics with zero data
7. **Return Results**: Return all created entities with IDs

### Existing Project Flow

1. **Validate Input**: Check required fields and project_id
2. **Verify Project**: Ensure project exists and is accessible
3. **Create Request**: Create request linked to existing project
4. **Create Keywords**: Add each keyword individually with logging
5. **Create Source URLs**: Add each URL individually with logging
6. **Update Statistics**: Update existing statistics or create new ones if needed
7. **Return Results**: Return all created entities with IDs

## Logging

The orchestrator provides comprehensive logging with structured format:

```
[orchestration_id] Step X: Description
[orchestration_id] Entity created: entity_id - details
[orchestration_id] Process completed: summary
```

### Log Levels

- **INFO**: Major steps and successful operations
- **DEBUG**: Detailed entity creation and data processing
- **WARNING**: Non-critical issues (e.g., empty keywords skipped)
- **ERROR**: Failures and exceptions

## Error Handling

### Exception Types

1. **ProjectRequestCreationException**: Orchestration-specific errors
2. **ValidationException**: Input validation errors
3. **EntityNotFoundException**: When referenced entities don't exist
4. **Service-specific exceptions**: From individual service layers

### Error Response Format

```json
{
    "status": "error",
    "message": "Project request creation failed: Detailed error message",
    "request_id": "req-12345"
}
```

## Data Validation

### Required Fields

- `title`: Project/request title (1-255 characters)
- `created_by`: User ID (UUID string)

### Optional Fields

- `project_id`: For adding to existing projects
- `description`: Detailed description (max 2000 characters)
- `time_range`: Start/end dates with optional date_range string
- `priority`: "low", "medium", "high" (default: "medium")
- `keywords`: Array of keyword strings
- `base_urls`: Array of URL objects with source information

### URL Object Structure

```json
{
    "source_type": "government|academic|clinical|commercial",
    "source_name": "Human readable source name",
    "url": "https://example.com",
    "country_region": "Optional country/region",
    "is_active": true,
    "url_metadata": {}
}
```

## Performance Considerations

- **Sequential Processing**: Keywords and URLs are processed one by one for better error handling
- **Partial Success**: Failed individual keywords/URLs don't stop the entire process
- **Logging Overhead**: Comprehensive logging may impact performance in high-volume scenarios
- **Database Connections**: Uses connection pooling through existing services

## Testing

Use the provided test script to verify functionality:

```bash
python test_orchestrator.py
```

The test script includes:
- Complete new project creation workflow
- Existing project request addition workflow
- Error handling verification
- Sample data validation

## Best Practices

1. **Always provide meaningful titles and descriptions**
2. **Use consistent user IDs for tracking**
3. **Validate URLs before submission**
4. **Monitor logs for orchestration tracking**
5. **Handle partial failures gracefully in client applications**
6. **Use appropriate priority levels**
7. **Provide time ranges for better request context**

## Troubleshooting

### Common Issues

1. **Invalid User ID**: Ensure created_by is a valid UUID string
2. **Empty Keywords**: Empty or whitespace-only keywords are skipped
3. **Invalid URLs**: Malformed URLs will cause individual URL creation to fail
4. **Project Not Found**: When using project_id, ensure the project exists
5. **Service Dependencies**: Ensure all dependent services are properly configured

### Debug Steps

1. Check orchestration logs using the orchestration_id
2. Verify individual service functionality
3. Validate input data format
4. Check database connectivity
5. Review service-specific error logs

## Future Enhancements

- **Rollback Mechanism**: Automatic cleanup on orchestration failure
- **Batch Processing**: Bulk keyword/URL creation for better performance
- **Async Notifications**: Real-time updates on orchestration progress
- **Caching**: Cache frequently used project/user data
- **Metrics**: Performance and success rate monitoring 