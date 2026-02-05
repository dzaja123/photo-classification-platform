"""Database setup script for Auth Service.

This script helps initialize the database and run migrations.

Usage:
    python setup_db.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from app.config import get_settings
from app.core.database import engine, Base
from app.models import User, RefreshToken


async def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully!")


async def drop_tables():
    """Drop all database tables (use with caution!)."""
    print("⚠️  WARNING: This will drop all tables!")
    response = input("Are you sure? (yes/no): ")
    if response.lower() == "yes":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        print("✅ Database tables dropped successfully!")
    else:
        print("❌ Operation cancelled.")


async def check_connection():
    """Check database connection."""
    print("Checking database connection...")
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        print("✅ Database connection successful!")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


async def main():
    """Main setup function."""
    settings = get_settings()
    
    print(f"\n{'='*60}")
    print(f"  Auth Service Database Setup")
    print(f"{'='*60}\n")
    print(f"Database URL: {settings.database_url}")
    print(f"\nOptions:")
    print("  1. Check database connection")
    print("  2. Create tables (use Alembic instead for production)")
    print("  3. Drop all tables (DANGEROUS!)")
    print("  4. Exit")
    
    choice = input("\nEnter your choice (1-4): ")
    
    if choice == "1":
        await check_connection()
    elif choice == "2":
        if await check_connection():
            await create_tables()
    elif choice == "3":
        if await check_connection():
            await drop_tables()
    elif choice == "4":
        print("Exiting...")
    else:
        print("Invalid choice!")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
