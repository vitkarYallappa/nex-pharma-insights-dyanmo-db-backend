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
        self.table_name = ProjectsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
        
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
                        self.log_info(f"Project {project_data['project_name']} already exists, skipping...")
                        continue
                except Exception:
                    pass  # Item doesn't exist, continue with creation
                
                # Create new project
                table.put_item(Item=project_data)
                created_count += 1
                
                self.log_info(f"Created project: {project_data['project_name']} (status: {project_data['status']})")
            
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
                    self.log_info(f"Deleted project: {project_data['project_name']}")
                except Exception as e:
                    self.log_info(f"Project {project_data['project_name']} not found or error deleting: {str(e)}")
            
            self.log_info(f"Projects cleanup completed. Deleted {deleted_count} projects")
            return True
            
        except Exception as e:
            self.log_error(f"Projects cleanup failed: {str(e)}")
            return False
    
    def _get_seed_data(self) -> List[Dict[str, Any]]:
        """Get the seed data for projects"""
        now = datetime.utcnow().isoformat()
        
        return [
            {
                "pk": str(uuid.uuid4()),
                "project_name": "Pharma Analytics Dashboard",
                "description": "Real-time analytics dashboard for pharmaceutical data insights",
                "created_by": "admin@nexpharmacorp.com",
                "status": "active",
                "priority": "high",
                "start_date": "2024-01-15",
                "end_date": "2024-06-30",
                "budget": 150000,
                "team_size": 8,
                "created_at": now,
                "updated_at": now
            },
            {
                "pk": str(uuid.uuid4()),
                "project_name": "Drug Discovery Platform",
                "description": "AI-powered platform for accelerating drug discovery processes",
                "created_by": "manager@nexpharmacorp.com",
                "status": "planning",
                "priority": "high",
                "start_date": "2024-03-01",
                "end_date": "2024-12-31",
                "budget": 500000,
                "team_size": 15,
                "created_at": now,
                "updated_at": now
            },
            {
                "pk": str(uuid.uuid4()),
                "project_name": "Clinical Trial Management",
                "description": "Comprehensive system for managing clinical trial data and workflows",
                "created_by": "pharmacist@nexpharmacorp.com",
                "status": "active",
                "priority": "medium",
                "start_date": "2024-02-01",
                "end_date": "2024-08-31",
                "budget": 300000,
                "team_size": 12,
                "created_at": now,
                "updated_at": now
            },
            {
                "pk": str(uuid.uuid4()),
                "project_name": "Regulatory Compliance Tracker",
                "description": "Automated tracking and reporting for regulatory compliance requirements",
                "created_by": "analyst@nexpharmacorp.com",
                "status": "completed",
                "priority": "medium",
                "start_date": "2023-09-01",
                "end_date": "2024-01-31",
                "budget": 75000,
                "team_size": 5,
                "created_at": now,
                "updated_at": now
            },
            {
                "pk": str(uuid.uuid4()),
                "project_name": "Supply Chain Optimization",
                "description": "Optimization of pharmaceutical supply chain using predictive analytics",
                "created_by": "manager@nexpharmacorp.com",
                "status": "on_hold",
                "priority": "low",
                "start_date": "2024-05-01",
                "end_date": "2024-11-30",
                "budget": 200000,
                "team_size": 6,
                "created_at": now,
                "updated_at": now
            },
            {
                "pk": str(uuid.uuid4()),
                "project_name": "Patient Portal Enhancement",
                "description": "Enhanced patient portal with mobile app and real-time notifications",
                "created_by": "test.user@nexpharmacorp.com",
                "status": "active",
                "priority": "medium",
                "start_date": "2024-01-01",
                "end_date": "2024-07-31",
                "budget": 120000,
                "team_size": 7,
                "created_at": now,
                "updated_at": now
            }
        ] 