"""
Database models and connection setup for SQLite.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import json
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./garden_planner.db")

# Create async engine
async_engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("DEBUG", "false").lower() == "true"
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for all models
Base = declarative_base()


class RequestLog(Base):
    """Model for logging user requests and responses."""
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Request data
    location = Column(String(100), nullable=False)
    direction = Column(String(10), nullable=False)
    water = Column(String(20), nullable=False)
    maintenance = Column(String(20), nullable=False)
    garden_type = Column(String(50), nullable=False)
    
    # Response data
    response_json = Column(Text, nullable=True)  # JSON string of the full response
    plant_count = Column(Integer, nullable=True)
    season = Column(String(100), nullable=True)
    
    # Metadata
    success = Column(Boolean, default=True, nullable=False)
    error_message = Column(Text, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    
    # Digital Ocean Spaces backup info
    spaces_backup_key = Column(String(200), nullable=True)  # S3 key if backed up
    spaces_backup_timestamp = Column(DateTime, nullable=True)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "location": self.location,
            "direction": self.direction,
            "water": self.water,
            "maintenance": self.maintenance,
            "garden_type": self.garden_type,
            "response_json": json.loads(self.response_json) if self.response_json else None,
            "plant_count": self.plant_count,
            "season": self.season,
            "success": self.success,
            "error_message": self.error_message,
            "processing_time_ms": self.processing_time_ms,
            "spaces_backup_key": self.spaces_backup_key,
            "spaces_backup_timestamp": self.spaces_backup_timestamp.isoformat() if self.spaces_backup_timestamp else None,
        }


async def get_db_session() -> AsyncSession:
    """Get database session for dependency injection."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_database():
    """Initialize database tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_database():
    """Close database connections."""
    await async_engine.dispose()