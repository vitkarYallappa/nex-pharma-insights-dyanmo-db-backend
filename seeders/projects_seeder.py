"""
Projects Seeder
Populates initial project data for development and testing
"""

import sys
from pathlib import Path
import uuid
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from seeders.base_seeder import BaseSeeder
from app.core.database import dynamodb_client
from app.config.table_configs.projects_table import ProjectsTableConfig
from app.config.settings import settings
from typing import List, Dict, Any

class ProjectsSeeder(BaseSeeder):
    """Seeder for initial project data"""
    
    def __init__(self):
        super().__init__()
        self.table_name = ProjectsTableConfig.get_table_name()
        
    @property
    def name(self) -> str:
        return "ProjectsSeeder"
    
    @property
    def description(self) -> str:
        return "Seeds initial project records with different statuses and creators"
    
    @property
    def dependencies(self) -> List[str]:
        """Projects seeder depends on users being seeded first"""
        return ["UserSeeder"]
    
    async def seed(self) -> bool:
        """Populate initial project data"""
        try:
            self.log_info("Starting projects seeding...")
            
            projects_data = self._get_seed_data()
            created_count = 0
            
            # Get table reference
            table = dynamodb_client.get_table(self.table_name)
            
            for project_data in projects_data:
                # Check if project already exists
                try:
                    response = table.get_item(Key={'pk': project_data['pk']})
                    if 'Item' in response:
                        self.log_info(f"Project {project_data['name']} already exists, skipping...")
                        continue
                except Exception:
                    pass  # Item doesn't exist, continue with creation
                
                # Create new project
                table.put_item(Item=project_data)
                created_count += 1
                
                self.log_info(f"Created project: {project_data['name']} (status: {project_data['status']})")
            
            self.log_info(f"Projects seeding completed. Created {created_count} projects")
            return True
            
        except Exception as e:
            self.log_error(f"Projects seeding failed: {str(e)}")
            return False
    
    async def clear(self) -> bool:
        """Clear seeded project data"""
        try:
            self.log_info("Starting projects data cleanup...")
            
            projects_data = self._get_seed_data()
            deleted_count = 0
            
            # Get table reference
            table = dynamodb_client.get_table(self.table_name)
            
            for project_data in projects_data:
                # Delete project by primary key
                try:
                    table.delete_item(Key={'pk': project_data['pk']})
                    deleted_count += 1
                    self.log_info(f"Deleted project: {project_data['name']}")
                except Exception as e:
                    self.log_info(f"Project {project_data['name']} not found or error deleting: {str(e)}")
            
            self.log_info(f"Projects cleanup completed. Deleted {deleted_count} projects")
            return True
            
        except Exception as e:
            self.log_error(f"Projects cleanup failed: {str(e)}")
            return False
    
    def _get_seed_data(self) -> List[Dict[str, Any]]:
        """Get the seed data for projects - matches SQLAlchemy schema exactly"""
        now = datetime.utcnow().isoformat()
        
        # Generate some user UUIDs for created_by field
        user_ids = [
            str(uuid.uuid4()),  # admin user
            str(uuid.uuid4()),  # manager user  
            str(uuid.uuid4()),  # pharmacist user
            str(uuid.uuid4()),  # analyst user
            str(uuid.uuid4())   # test user
        ]
        
        return [
            {
                # SQLAlchemy: id (UUID) -> DynamoDB: pk (String)
                "pk": str(uuid.uuid4()),
                
                # SQLAlchemy: name (String) -> DynamoDB: name (String)
                "name": "Pharma Analytics Dashboard",
                
                # SQLAlchemy: description (Text) -> DynamoDB: description (String)
                "description": "Real-time analytics dashboard for pharmaceutical data insights",
                
                # SQLAlchemy: created_by (UUID) -> DynamoDB: created_by (String)
                "created_by": user_ids[0],
                
                # SQLAlchemy: status (String) -> DynamoDB: status (String)
                "status": "active",
                
                # SQLAlchemy: project_metadata (JSON) -> DynamoDB: project_metadata (Map)
                "project_metadata": {
                    "priority": "high",
                    "tags": ["analytics", "dashboard", "pharma"],
                    "budget": 150000,
                    "team_size": 8,
                    "start_date": "2024-01-15",
                    "end_date": "2024-06-30"
                },
                
                # SQLAlchemy: module_config (JSON) -> DynamoDB: module_config (Map)
                "module_config": {
                    "enabled_modules": ["analytics", "reporting", "visualization"],
                    "settings": {
                        "refresh_interval": 300,
                        "auto_export": True,
                        "notification_enabled": True
                    }
                },
                
                # SQLAlchemy: created_at (DateTime) -> DynamoDB: created_at (String)
                "created_at": now,
                
                # SQLAlchemy: updated_at (DateTime) -> DynamoDB: updated_at (String)
                "updated_at": now
            },
            {
                "pk": str(uuid.uuid4()),
                "name": "Drug Discovery Platform",
                "description": "AI-powered platform for accelerating drug discovery processes",
                "created_by": user_ids[1],
                "status": "planning",
                "project_metadata": {
                    "priority": "high",
                    "tags": ["ai", "drug-discovery", "research"],
                    "budget": 500000,
                    "team_size": 15,
                    "start_date": "2024-03-01",
                    "end_date": "2024-12-31"
                },
                "module_config": {
                    "enabled_modules": ["ai_engine", "molecular_analysis", "prediction"],
                    "settings": {
                        "ai_model": "transformer_v2",
                        "batch_processing": True,
                        "gpu_acceleration": True
                    }
                },
                "created_at": now,
                "updated_at": now
            },
            {
                "pk": str(uuid.uuid4()),
                "name": "Clinical Trial Management",
                "description": "Comprehensive system for managing clinical trial data and workflows",
                "created_by": user_ids[2],
                "status": "active",
                "project_metadata": {
                    "priority": "medium",
                    "tags": ["clinical", "trials", "management"],
                    "budget": 300000,
                    "team_size": 12,
                    "start_date": "2024-02-01",
                    "end_date": "2024-08-31"
                },
                "module_config": {
                    "enabled_modules": ["patient_management", "data_collection", "compliance"],
                    "settings": {
                        "encryption_level": "AES256",
                        "audit_trail": True,
                        "backup_frequency": "daily"
                    }
                },
                "created_at": now,
                "updated_at": now
            },
            {
                "pk": str(uuid.uuid4()),
                "name": "Regulatory Compliance Tracker",
                "description": "Automated tracking and reporting for regulatory compliance requirements",
                "created_by": user_ids[3],
                "status": "completed",
                "project_metadata": {
                    "priority": "medium",
                    "tags": ["compliance", "regulatory", "automation"],
                    "budget": 75000,
                    "team_size": 5,
                    "start_date": "2023-09-01",
                    "end_date": "2024-01-31"
                },
                "module_config": {
                    "enabled_modules": ["compliance_checker", "report_generator", "alert_system"],
                    "settings": {
                        "check_frequency": "weekly",
                        "auto_reports": True,
                        "alert_threshold": "medium"
                    }
                },
                "created_at": now,
                "updated_at": now
            },
            {
                "pk": str(uuid.uuid4()),
                "name": "Supply Chain Optimization",
                "description": "Optimization of pharmaceutical supply chain using predictive analytics",
                "created_by": user_ids[1],
                "status": "on_hold",
                "project_metadata": {
                    "priority": "low",
                    "tags": ["supply-chain", "optimization", "analytics"],
                    "budget": 200000,
                    "team_size": 6,
                    "start_date": "2024-05-01",
                    "end_date": "2024-11-30"
                },
                "module_config": {
                    "enabled_modules": ["inventory_tracker", "demand_predictor", "route_optimizer"],
                    "settings": {
                        "prediction_model": "arima",
                        "optimization_algorithm": "genetic",
                        "real_time_updates": False
                    }
                },
                "created_at": now,
                "updated_at": now
            },
            {
                "pk": str(uuid.uuid4()),
                "name": "Patient Portal Enhancement",
                "description": "Enhanced patient portal with mobile app and real-time notifications",
                "created_by": user_ids[4],
                "status": "active",
                "project_metadata": {
                    "priority": "medium",
                    "tags": ["patient-portal", "mobile", "notifications"],
                    "budget": 120000,
                    "team_size": 7,
                    "start_date": "2024-01-01",
                    "end_date": "2024-07-31"
                },
                "module_config": {
                    "enabled_modules": ["mobile_app", "notification_service", "patient_dashboard"],
                    "settings": {
                        "push_notifications": True,
                        "offline_mode": True,
                        "biometric_auth": True
                    }
                },
                "created_at": now,
                "updated_at": now
            }
        ] 