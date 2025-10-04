"""
Service for logging requests and responses with optional backup to Digital Ocean Spaces.
"""
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.database import RequestLog
from models.schemas import RecommendationRequest, RecommendationResponse
from services.storage import spaces_client
import logging

logger = logging.getLogger(__name__)


class LoggingService:
    """Service for logging user requests and responses."""
    
    @staticmethod
    async def log_request(
        db: AsyncSession,
        request: RecommendationRequest,
        response: Optional[RecommendationResponse] = None,
        error_message: Optional[str] = None,
        processing_time_ms: Optional[int] = None
    ) -> Optional[RequestLog]:
        """
        Log a user request and optional response to the database.
        
        Args:
            db: Database session
            request: The user's recommendation request
            response: The generated response (if successful)
            error_message: Error message (if failed)
            processing_time_ms: Time taken to process the request
            
        Returns:
            The created RequestLog instance or None if failed
        """
        try:
            # Create log entry
            log_entry = RequestLog(
                timestamp=datetime.utcnow(),
                location=request.location,
                direction=request.direction.value,
                water=request.water.value,
                maintenance=request.maintenance.value,
                garden_type=request.garden_type.value,
                success=response is not None,
                error_message=error_message,
                processing_time_ms=processing_time_ms
            )
            
            # Add response data if available
            if response:
                log_entry.response_json = response.model_dump_json()
                log_entry.plant_count = len(response.plants)
                log_entry.season = response.season
            
            # Save to database
            db.add(log_entry)
            await db.commit()
            await db.refresh(log_entry)
            
            logger.info(f"Logged request for {request.location} (ID: {log_entry.id})")
            
            # Attempt backup to Spaces (async, don't block on failure)
            try:
                await LoggingService._backup_to_spaces(log_entry)
            except Exception as e:
                logger.warning(f"Spaces backup failed for log {log_entry.id}: {e}")
            
            return log_entry
            
        except Exception as e:
            logger.error(f"Failed to log request: {e}")
            await db.rollback()
            return None
    
    @staticmethod
    async def _backup_to_spaces(log_entry: RequestLog) -> None:
        """
        Backup log entry to Digital Ocean Spaces.
        
        Args:
            log_entry: The log entry to backup
        """
        if not spaces_client.enabled:
            return
        
        try:
            # Convert log entry to dict for backup
            log_data = log_entry.to_dict()
            
            # Attempt backup
            backup_key = await spaces_client.backup_request_log(log_data)
            
            if backup_key:
                # Update log entry with backup info (don't await commit to avoid blocking)
                log_entry.spaces_backup_key = backup_key
                log_entry.spaces_backup_timestamp = datetime.utcnow()
                logger.debug(f"Backed up log {log_entry.id} to Spaces: {backup_key}")
            
        except Exception as e:
            logger.warning(f"Spaces backup failed for log {log_entry.id}: {e}")
    
    @staticmethod
    async def get_recent_logs(
        db: AsyncSession,
        limit: int = 50,
        location_filter: Optional[str] = None
    ) -> list[RequestLog]:
        """
        Get recent request logs from the database.
        
        Args:
            db: Database session
            limit: Maximum number of logs to return
            location_filter: Optional location filter
            
        Returns:
            List of RequestLog instances
        """
        try:
            query = select(RequestLog).order_by(RequestLog.timestamp.desc()).limit(limit)
            
            if location_filter:
                query = query.where(RequestLog.location.ilike(f"%{location_filter}%"))
            
            result = await db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Failed to retrieve logs: {e}")
            return []
    
    @staticmethod
    async def get_log_stats(db: AsyncSession) -> Dict[str, Any]:
        """
        Get basic statistics about logged requests.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with statistics
        """
        try:
            # Get total count
            total_result = await db.execute(select(RequestLog.id).count())
            total_count = total_result.scalar()
            
            # Get success count
            success_result = await db.execute(
                select(RequestLog.id).where(RequestLog.success == True).count()
            )
            success_count = success_result.scalar()
            
            # Get recent logs for additional stats
            recent_logs = await LoggingService.get_recent_logs(db, limit=100)
            
            # Calculate average processing time
            processing_times = [
                log.processing_time_ms for log in recent_logs 
                if log.processing_time_ms is not None
            ]
            avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
            
            return {
                "total_requests": total_count,
                "successful_requests": success_count,
                "success_rate": (success_count / total_count * 100) if total_count > 0 else 0,
                "average_processing_time_ms": round(avg_processing_time, 2),
                "recent_requests_count": len(recent_logs),
                "spaces_backup_enabled": spaces_client.enabled
            }
            
        except Exception as e:
            logger.error(f"Failed to get log stats: {e}")
            return {
                "total_requests": 0,
                "successful_requests": 0,
                "success_rate": 0,
                "average_processing_time_ms": 0,
                "recent_requests_count": 0,
                "spaces_backup_enabled": spaces_client.enabled
            }


# Simple function wrapper for backward compatibility
async def log_request(log_data: Dict[str, Any]) -> None:
    """
    Simple function to log request data.
    This is a simplified version that doesn't require database session.
    
    Args:
        log_data: Dictionary containing request log data
    """
    try:
        # Log to console/file
        logger.info(f"Request log: {json.dumps(log_data, default=str)}")
        
        # Attempt backup to Spaces if available
        if spaces_client.enabled:
            try:
                backup_key = await spaces_client.backup_request_log(log_data)
                if backup_key:
                    logger.debug(f"Backed up request log to Spaces: {backup_key}")
            except Exception as e:
                logger.warning(f"Spaces backup failed: {e}")
                
    except Exception as e:
        logger.error(f"Failed to log request: {e}")