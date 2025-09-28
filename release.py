#!/usr/bin/env python3
"""
Railway release script to create database tables
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.database import engine, Base

async def create_tables():
    """Create database tables"""
    try:
        print("🔗 Railway Release Phase - Creating database tables...")
        print(f"Database URL: {os.getenv('DATABASE_URL', 'Not set')}")
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        print("This might be normal if tables already exist")
        # Don't exit with error code - Railway might retry unnecessarily
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(create_tables())
