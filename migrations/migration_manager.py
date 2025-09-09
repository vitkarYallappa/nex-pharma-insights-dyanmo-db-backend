"""
DynamoDB Migration System
Handles table creation, updates, and data migrations
"""

import os
import sys
import importlib.util
from datetime import datetime
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import dynamodb_client
from app.config.settings import settings
from app.core.logging import get_logger

logger = get_logger("migrations")

class BaseMigration(ABC):
    """Base class for all migrations"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.timestamp = datetime.utcnow()
    
    @abstractmethod
    async def up(self):
        """Execute the migration"""
        pass
    
    @abstractmethod
    async def down(self):
        """Rollback the migration"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Migration description"""
        pass

class MigrationRecord:
    """Represents a migration record in the database"""
    
    def __init__(self, migration_name: str, executed_at: datetime, description: str = ""):
        self.migration_name = migration_name
        self.executed_at = executed_at
        self.description = description

class MigrationManager:
    """Manages database migrations"""
    
    MIGRATIONS_TABLE = "migration_history"
    
    def __init__(self):
        self.logger = get_logger("migration_manager")
        self.migrations_dir = Path(__file__).parent
        self._ensure_migrations_table()
    
    def _ensure_migrations_table(self):
        """Ensure the migrations table exists"""
        try:
            # Try to get the table first
            dynamodb_client.get_table(self.MIGRATIONS_TABLE)
            self.logger.info(f"Migrations table {self.MIGRATIONS_TABLE} already exists")
        except:
            # Create the migrations table
            self.logger.info(f"Creating migrations table: {self.MIGRATIONS_TABLE}")
            dynamodb_client.create_table(
                table_name=self.MIGRATIONS_TABLE,
                key_schema=[
                    {'AttributeName': 'migration_name', 'KeyType': 'HASH'}
                ],
                attribute_definitions=[
                    {'AttributeName': 'migration_name', 'AttributeType': 'S'}
                ]
            )
    
    async def get_executed_migrations(self) -> List[MigrationRecord]:
        """Get list of executed migrations"""
        try:
            table = dynamodb_client.get_table(self.MIGRATIONS_TABLE)
            response = table.scan()
            
            migrations = []
            for item in response.get('Items', []):
                migration = MigrationRecord(
                    migration_name=item['migration_name'],
                    executed_at=datetime.fromisoformat(item['executed_at']),
                    description=item.get('description', '')
                )
                migrations.append(migration)
            
            # Sort by execution time
            migrations.sort(key=lambda x: x.executed_at)
            return migrations
            
        except Exception as e:
            self.logger.error(f"Error getting executed migrations: {str(e)}")
            return []
    
    async def record_migration(self, migration_name: str, description: str = ""):
        """Record a successful migration"""
        try:
            table = dynamodb_client.get_table(self.MIGRATIONS_TABLE)
            table.put_item(Item={
                'migration_name': migration_name,
                'executed_at': datetime.utcnow().isoformat(),
                'description': description
            })
            self.logger.info(f"Recorded migration: {migration_name}")
        except Exception as e:
            self.logger.error(f"Error recording migration {migration_name}: {str(e)}")
            raise
    
    async def remove_migration_record(self, migration_name: str):
        """Remove a migration record (for rollbacks)"""
        try:
            table = dynamodb_client.get_table(self.MIGRATIONS_TABLE)
            table.delete_item(Key={'migration_name': migration_name})
            self.logger.info(f"Removed migration record: {migration_name}")
        except Exception as e:
            self.logger.error(f"Error removing migration record {migration_name}: {str(e)}")
            raise
    
    def discover_migrations(self) -> List[str]:
        """Discover all migration files"""
        migration_files = []
        
        for file_path in self.migrations_dir.glob("*.py"):
            if (file_path.name.startswith("migration_") and 
                file_path.name != "__init__.py" and 
                file_path.name != "migration_manager.py"):
                migration_files.append(file_path.stem)
        
        migration_files.sort()  # Sort alphabetically/chronologically
        self.logger.info(f"Discovered {len(migration_files)} migration files")
        return migration_files
    
    def load_migration(self, migration_name: str) -> BaseMigration:
        """Load a migration class from file"""
        try:
            file_path = self.migrations_dir / f"{migration_name}.py"
            
            if not file_path.exists():
                raise FileNotFoundError(f"Migration file {file_path} not found")
            
            spec = importlib.util.spec_from_file_location(migration_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find the migration class (should inherit from BaseMigration)
            migration_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, BaseMigration) and 
                    attr != BaseMigration):
                    migration_class = attr
                    break
            
            if not migration_class:
                raise ValueError(f"No migration class found in {migration_name}.py")
            
            return migration_class()
            
        except Exception as e:
            self.logger.error(f"Error loading migration {migration_name}: {str(e)}")
            raise
    
    async def get_pending_migrations(self) -> List[str]:
        """Get list of pending (not executed) migrations"""
        all_migrations = self.discover_migrations()
        executed_migrations = await self.get_executed_migrations()
        executed_names = {m.migration_name for m in executed_migrations}
        
        pending = [name for name in all_migrations if name not in executed_names]
        self.logger.info(f"Found {len(pending)} pending migrations")
        return pending
    
    async def migrate(self, target_migration: Optional[str] = None) -> bool:
        """Run pending migrations up to target migration"""
        try:
            pending_migrations = await self.get_pending_migrations()
            
            if not pending_migrations:
                self.logger.info("No pending migrations to run")
                return True
            
            migrations_to_run = pending_migrations
            if target_migration:
                try:
                    target_index = pending_migrations.index(target_migration)
                    migrations_to_run = pending_migrations[:target_index + 1]
                except ValueError:
                    self.logger.error(f"Target migration {target_migration} not found in pending migrations")
                    return False
            
            self.logger.info(f"Running {len(migrations_to_run)} migrations")
            
            for migration_name in migrations_to_run:
                self.logger.info(f"Executing migration: {migration_name}")
                
                migration = self.load_migration(migration_name)
                
                try:
                    await migration.up()
                    await self.record_migration(migration_name, migration.description)
                    self.logger.info(f"Migration {migration_name} completed successfully")
                except Exception as e:
                    self.logger.error(f"Migration {migration_name} failed: {str(e)}")
                    raise
            
            self.logger.info("All migrations completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Migration process failed: {str(e)}")
            return False
    
    async def rollback(self, migration_name: str) -> bool:
        """Rollback a specific migration"""
        try:
            self.logger.info(f"Rolling back migration: {migration_name}")
            
            # Check if migration was executed
            executed_migrations = await self.get_executed_migrations()
            executed_names = {m.migration_name for m in executed_migrations}
            
            if migration_name not in executed_names:
                self.logger.warning(f"Migration {migration_name} was not executed, nothing to rollback")
                return True
            
            migration = self.load_migration(migration_name)
            
            try:
                await migration.down()
                await self.remove_migration_record(migration_name)
                self.logger.info(f"Migration {migration_name} rolled back successfully")
                return True
            except Exception as e:
                self.logger.error(f"Rollback of {migration_name} failed: {str(e)}")
                raise
                
        except Exception as e:
            self.logger.error(f"Rollback process failed: {str(e)}")
            return False
    
    async def status(self) -> Dict[str, Any]:
        """Get migration status"""
        try:
            all_migrations = self.discover_migrations()
            executed_migrations = await self.get_executed_migrations()
            pending_migrations = await self.get_pending_migrations()
            
            return {
                'total_migrations': len(all_migrations),
                'executed_count': len(executed_migrations),
                'pending_count': len(pending_migrations),
                'executed_migrations': [
                    {
                        'name': m.migration_name,
                        'executed_at': m.executed_at.isoformat(),
                        'description': m.description
                    }
                    for m in executed_migrations
                ],
                'pending_migrations': pending_migrations
            }
            
        except Exception as e:
            self.logger.error(f"Error getting migration status: {str(e)}")
            raise

# Example migration template
class ExampleMigration(BaseMigration):
    """Example migration for reference"""
    
    @property
    def description(self) -> str:
        return "Example migration template"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Executing example migration")
        # Add your migration logic here
        pass
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back example migration")
        # Add your rollback logic here
        pass

# CLI functions for migration management
async def main():
    """Main CLI function for migration management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="DynamoDB Migration Manager")
    parser.add_argument('action', choices=['migrate', 'rollback', 'status', 'create'], 
                       help='Migration action to perform')
    parser.add_argument('--target', help='Target migration name')
    parser.add_argument('--name', help='Migration name for create action')
    
    args = parser.parse_args()
    
    manager = MigrationManager()
    
    if args.action == 'migrate':
        success = await manager.migrate(args.target)
        sys.exit(0 if success else 1)
    elif args.action == 'rollback':
        if not args.target:
            print("Error: --target required for rollback")
            sys.exit(1)
        success = await manager.rollback(args.target)
        sys.exit(0 if success else 1)
    elif args.action == 'status':
        status = await manager.status()
        print(f"Total migrations: {status['total_migrations']}")
        print(f"Executed: {status['executed_count']}")
        print(f"Pending: {status['pending_count']}")
        
        if status['executed_migrations']:
            print("\nExecuted migrations:")
            for migration in status['executed_migrations']:
                print(f"  - {migration['name']} ({migration['executed_at']})")
        
        if status['pending_migrations']:
            print("\nPending migrations:")
            for migration in status['pending_migrations']:
                print(f"  - {migration}")
    elif args.action == 'create':
        if not args.name:
            print("Error: --name required for create action")
            sys.exit(1)
        
        # Create new migration file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        migration_name = f"migration_{timestamp}_{args.name}"
        file_path = Path(__file__).parent / f"{migration_name}.py"
        
        template = f'''"""
{args.name.replace('_', ' ').title()} Migration
Created: {datetime.now().isoformat()}
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_manager import BaseMigration
from app.core.database import dynamodb_client
from app.core.logging import get_logger

logger = get_logger("migration.{args.name}")

class {args.name.replace('_', ' ').title().replace(' ', '')}Migration(BaseMigration):
    """
    {args.name.replace('_', ' ').title()} Migration
    """
    
    @property
    def description(self) -> str:
        return "{args.name.replace('_', ' ').title()}"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Executing {args.name} migration")
        
        # TODO: Add your migration logic here
        # Example:
        # dynamodb_client.create_table(
        #     table_name="new_table",
        #     key_schema=[{{'AttributeName': 'pk', 'KeyType': 'HASH'}}],
        #     attribute_definitions=[{{'AttributeName': 'pk', 'AttributeType': 'S'}}]
        # )
        
        pass
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back {args.name} migration")
        
        # TODO: Add your rollback logic here
        # Example:
        # dynamodb_client.delete_table("new_table")
        
        pass
'''
        
        with open(file_path, 'w') as f:
            f.write(template)
        
        print(f"Created migration file: {file_path}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())