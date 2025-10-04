"""
API routes for plant recommendations.
"""
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from models.schemas import (
    RecommendationRequest, 
    RecommendationResponse, 
    ErrorResponse
)
from services.llm_service import llm_service
from services.logging_service import log_request
from typing import Dict, Any

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["recommendations"])


async def validate_llm_service():
    """Dependency to check if LLM service is available."""
    if not llm_service.enabled:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "llm_service_unavailable",
                "message": "LLM service is not configured. Please check environment variables.",
                "retry_suggested": False
            }
        )


@router.post(
    "/recommendations",
    response_model=RecommendationResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request data"},
        503: {"model": ErrorResponse, "description": "LLM service unavailable"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_plant_recommendations(
    request: RecommendationRequest,
    _: None = Depends(validate_llm_service)
) -> RecommendationResponse:
    """
    Generate plant recommendations based on user preferences and location.
    
    This endpoint processes user input including location, yard direction,
    water availability, maintenance preferences, and garden type to generate
    personalized plant recommendations using Digital Ocean's LLM service.
    
    Args:
        request: RecommendationRequest containing user preferences
        
    Returns:
        RecommendationResponse with 4-6 plant recommendations
        
    Raises:
        HTTPException: For various error conditions
    """
    request_start_time = datetime.utcnow()
    log_data = {
        "timestamp": request_start_time.isoformat(),
        "location": request.location,
        "direction": request.direction,
        "water": request.water,
        "maintenance": request.maintenance,
        "garden_type": request.garden_type,
        "success": False,
        "error": None,
        "response_time_ms": 0,
        "plant_count": 0
    }
    
    try:
        logger.info(f"Processing recommendation request for {request.location}")
        
        # Get recommendations from LLM service
        response = await llm_service.get_recommendations(request)
        
        # Calculate response time
        request_end_time = datetime.utcnow()
        response_time_ms = int((request_end_time - request_start_time).total_seconds() * 1000)
        
        # Update log data
        log_data.update({
            "success": True,
            "response_time_ms": response_time_ms,
            "plant_count": len(response.plants)
        })
        
        # Log the successful request
        await log_request(log_data)
        
        logger.info(f"Successfully generated {len(response.plants)} recommendations for {request.location}")
        
        return response
        
    except Exception as e:
        # Calculate response time for error case
        request_end_time = datetime.utcnow()
        response_time_ms = int((request_end_time - request_start_time).total_seconds() * 1000)
        
        error_message = str(e)
        logger.error(f"Failed to generate recommendations: {error_message}")
        
        # Update log data with error
        log_data.update({
            "success": False,
            "error": error_message,
            "response_time_ms": response_time_ms
        })
        
        # Log the failed request
        await log_request(log_data)
        
        # Determine appropriate HTTP status code and error response
        if "not configured" in error_message.lower():
            status_code = 503
            error_code = "llm_service_unavailable"
            retry_suggested = False
        elif "authentication" in error_message.lower() or "api key" in error_message.lower():
            status_code = 503
            error_code = "authentication_failed"
            retry_suggested = False
        elif "timeout" in error_message.lower():
            status_code = 504
            error_code = "request_timeout"
            retry_suggested = True
        elif "rate limit" in error_message.lower():
            status_code = 429
            error_code = "rate_limit_exceeded"
            retry_suggested = True
        elif "invalid" in error_message.lower() and "json" in error_message.lower():
            status_code = 502
            error_code = "llm_response_invalid"
            retry_suggested = True
        else:
            status_code = 500
            error_code = "llm_service_failed"
            retry_suggested = True
        
        # Create error response
        error_response = ErrorResponse(
            error=error_code,
            message=f"Unable to generate plant recommendations: {error_message}",
            retry_suggested=retry_suggested
        )
        
        raise HTTPException(
            status_code=status_code,
            detail=error_response.dict()
        )


@router.get("/recommendations/health")
async def recommendations_health_check():
    """
    Health check endpoint for the recommendations service.
    
    Returns:
        Dict with service status and LLM service availability
    """
    return {
        "service": "recommendations",
        "status": "healthy",
        "llm_service_configured": llm_service.enabled,
        "timestamp": datetime.utcnow().isoformat()
    }