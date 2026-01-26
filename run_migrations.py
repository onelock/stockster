#!/usr/bin/env python3
"""
Run Alembic migrations.
This script is used both locally and in Kubernetes migration job.
"""
import os
import sys
from alembic import command
from alembic.config import Config


def run_migrations():
    """Run database migrations using Alembic."""
    print("🚀 Starting database migration...")
    print("=" * 60)
    
    # Get database URL from environment or use default
    db_url = os.getenv(
        "DATABASE_URL"
    )
    
    # Mask password in output
    safe_url = db_url.split('@')[1] if '@' in db_url else db_url
    print(f"📍 Target database: {safe_url}")
    
    # Create Alembic config
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    
    try:
        # Show current revision
        print("\n📊 Current database revision:")
        try:
            command.current(alembic_cfg, verbose=True)
        except Exception:
            print("  No migrations applied yet")
        
        # Show pending migrations
        print("\n📋 Checking for pending migrations...")
        command.heads(alembic_cfg, verbose=True)
        
        # Run migrations
        print("\n🔄 Applying migrations...")
        command.upgrade(alembic_cfg, "head")
        
        # Show final state
        print("\n✅ Migration completed. Current revision:")
        command.current(alembic_cfg, verbose=True)
        
        print("\n" + "=" * 60)
        print("✅ All migrations applied successfully!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(run_migrations())
