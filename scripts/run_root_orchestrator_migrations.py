#!/usr/bin/env python3
"""
Root Orchestrator Migration Script
Runs the migrations for market intelligence requests and processing logs tables
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from migrations.migration_manager import MigrationManager
from app.core.logging import get_logger
from app.config.settings import settings

logger = get_logger("root_orchestrator_migrations")

async def run_root_orchestrator_migrations():
    """Run the Root Orchestrator migrations"""
    
    print("=" * 60)
    print("Root Orchestrator DynamoDB Migration Script")
    print("=" * 60)
    print(f"Environment: {}")
    print(f"AWS Region: {settings.AWS_REGION}")
    print()
    
    try:
        # Initialize migration manager
        manager = MigrationManager()
        
        # Get current migration status
        print("Checking current migration status...")
        status = await manager.status()
        
        print(f"Total migrations: {status['total_migrations']}")
        print(f"Executed: {status['executed_count']}")
        print(f"Pending: {status['pending_count']}")
        print()
        
        # Show pending migrations
        if status['pending_migrations']:
            print("Pending migrations:")
            for migration in status['pending_migrations']:
                print(f"  - {migration}")
            print()
        
        # Filter for Root Orchestrator migrations
        root_orchestrator_migrations = [
            "migration_20241201_122000_create_market_intelligence_requests_table",
            "migration_20241201_122100_create_request_processing_logs_table"
        ]
        
        pending_root_migrations = [
            m for m in status['pending_migrations'] 
            if m in root_orchestrator_migrations
        ]
        
        if not pending_root_migrations:
            print("✅ All Root Orchestrator migrations are already executed!")
            print()
            
            # Show executed Root Orchestrator migrations
            executed_root_migrations = [
                m for m in status['executed_migrations']
                if m['name'] in root_orchestrator_migrations
            ]
            
            if executed_root_migrations:
                print("Executed Root Orchestrator migrations:")
                for migration in executed_root_migrations:
                    print(f"  ✅ {migration['name']} ({migration['executed_at']})")
            
            return True
        
        print(f"Found {len(pending_root_migrations)} Root Orchestrator migrations to run:")
        for migration in pending_root_migrations:
            print(f"  - {migration}")
        print()
        
        # Ask for confirmation
        response = input("Do you want to run these migrations? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Migration cancelled by user.")
            return False
        
        print("\nRunning Root Orchestrator migrations...")
        print("-" * 40)
        
        # Run each migration individually for better logging
        for migration_name in pending_root_migrations:
            print(f"\n🚀 Running: {migration_name}")
            success = await manager.migrate(migration_name)
            
            if success:
                print(f"✅ Completed: {migration_name}")
            else:
                print(f"❌ Failed: {migration_name}")
                return False
        
        print("\n" + "=" * 60)
        print("🎉 All Root Orchestrator migrations completed successfully!")
        print("=" * 60)
        
        # Show final status
        final_status = await manager.status()
        print(f"\nFinal status:")
        print(f"  Total migrations: {final_status['total_migrations']}")
        print(f"  Executed: {final_status['executed_count']}")
        print(f"  Pending: {final_status['pending_count']}")
        
        # Show created tables
        print(f"\n📋 Created tables (environment: {}):")
        print(f"  - {}-market_intelligence_requests")
        print(f"  - {}-request_processing_logs")
        
        print(f"\n📝 Tables created without secondary indexes (as requested)")
        print(f"  - Primary key only: request_id for market_intelligence_requests")
        print(f"  - Primary key only: log_id for request_processing_logs")
        
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        print(f"\n❌ Migration failed: {str(e)}")
        return False

async def rollback_root_orchestrator_migrations():
    """Rollback Root Orchestrator migrations"""
    
    print("=" * 60)
    print("Root Orchestrator Migration Rollback")
    print("=" * 60)
    print(f"Environment: {}")
    print()
    
    try:
        manager = MigrationManager()
        
        # Root Orchestrator migrations in reverse order for rollback
        root_orchestrator_migrations = [
            "migration_20241201_122100_create_request_processing_logs_table",
            "migration_20241201_122000_create_market_intelligence_requests_table"
        ]
        
        # Get executed migrations
        status = await manager.status()
        executed_root_migrations = [
            m['name'] for m in status['executed_migrations']
            if m['name'] in root_orchestrator_migrations
        ]
        
        if not executed_root_migrations:
            print("No Root Orchestrator migrations to rollback.")
            return True
        
        print(f"Found {len(executed_root_migrations)} Root Orchestrator migrations to rollback:")
        for migration in executed_root_migrations:
            print(f"  - {migration}")
        print()
        
        # Ask for confirmation
        response = input("⚠️  This will DELETE the tables! Are you sure? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Rollback cancelled by user.")
            return False
        
        print("\nRolling back Root Orchestrator migrations...")
        print("-" * 40)
        
        # Rollback in reverse order
        for migration_name in root_orchestrator_migrations:
            if migration_name in executed_root_migrations:
                print(f"\n🔄 Rolling back: {migration_name}")
                success = await manager.rollback(migration_name)
                
                if success:
                    print(f"✅ Rolled back: {migration_name}")
                else:
                    print(f"❌ Rollback failed: {migration_name}")
                    return False
        
        print("\n" + "=" * 60)
        print("🎉 Root Orchestrator migrations rolled back successfully!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"Rollback failed: {str(e)}")
        print(f"\n❌ Rollback failed: {str(e)}")
        return False

async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Root Orchestrator Migration Script")
    parser.add_argument('action', choices=['migrate', 'rollback', 'status'], 
                       help='Action to perform')
    
    args = parser.parse_args()
    
    if args.action == 'migrate':
        success = await run_root_orchestrator_migrations()
        sys.exit(0 if success else 1)
    elif args.action == 'rollback':
        success = await rollback_root_orchestrator_migrations()
        sys.exit(0 if success else 1)
    elif args.action == 'status':
        manager = MigrationManager()
        status = await manager.status()
        
        root_orchestrator_migrations = [
            "migration_20241201_122000_create_market_intelligence_requests_table",
            "migration_20241201_122100_create_request_processing_logs_table"
        ]
        
        print("Root Orchestrator Migration Status")
        print("=" * 40)
        
        executed_root = [
            m for m in status['executed_migrations']
            if m['name'] in root_orchestrator_migrations
        ]
        
        pending_root = [
            m for m in status['pending_migrations']
            if m in root_orchestrator_migrations
        ]
        
        print(f"Executed Root Orchestrator migrations: {len(executed_root)}")
        for migration in executed_root:
            print(f"  ✅ {migration['name']} ({migration['executed_at']})")
        
        print(f"\nPending Root Orchestrator migrations: {len(pending_root)}")
        for migration in pending_root:
            print(f"  ⏳ {migration}")

if __name__ == "__main__":
    asyncio.run(main()) 