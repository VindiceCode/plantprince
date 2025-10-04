"""
API routes for plant recommendations using GenAI Agent.
"""
import logging
import json
import httpx
import os
from datetime import datetime
from fastapi import APIRouter, HTTPException
from models.schemas import (
    RecommendationRequest, 
    RecommendationResponse, 
    ErrorResponse,
    Plant
)
from services.logging_service import log_request
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["recommendations"])

# GenAI Agent configuration
DO_AGENT_API_KEY = os.getenv("DO_AGENT_API_KEY")
DO_AGENT_BASE_URL = os.getenv("DO_AGENT_BASE_URL")


def get_hardiness_zone(location: str) -> str:
    """Determine USDA hardiness zone from location."""
    location_lower = location.lower()
    
    zone_map = {
        "denver": "5b", "colorado": "5b",
        "seattle": "8b", "portland": "8b",
        "boston": "6b", "new york": "7a",
        "chicago": "6a", "atlanta": "8a",
        "miami": "10b", "los angeles": "10a",
        "phoenix": "9b", "austin": "8b",
        "dallas": "8a"
    }
    
    for city, zone in zone_map.items():
        if city in location_lower:
            return zone
    
    return "6b"  # Default zone


def get_current_season(zone: str) -> str:
    """Determine current planting season based on date and zone."""
    month = datetime.now().month
    
    if month in [3, 4, 5]:
        return "Spring Planting Season"
    elif month in [6, 7, 8]:
        return "Summer Growing Season"
    elif month in [9, 10, 11]:
        return "Fall Planting Season"
    else:
        return "Winter Planning Season"


def map_direction_to_sun(direction: str) -> str:
    """Map yard direction to sun exposure level"""
    sun_map = {
        'N': 'shade', 'NE': 'partial shade', 'NW': 'partial shade',
        'E': 'partial sun', 'W': 'partial sun',
        'SE': 'partial sun', 'SW': 'partial sun',
        'S': 'full sun'
    }
    return sun_map.get(direction.upper(), 'partial sun')


def construct_agent_prompt(request: RecommendationRequest, zone: str, season: str, sun_level: str) -> str:
    """Construct the prompt for the GenAI Agent."""
    prompt = f"""You are an expert horticulturist and landscape designer. Based on the following criteria, recommend 4-6 native, climate-appropriate plants for a home garden:

**Location & Climate:**
- Location: {request.location}
- USDA Hardiness Zone: {zone}
- Current Season: {season}

**Site Conditions:**
- Yard Direction: {request.direction} (Sun Exposure: {sun_level})
- Water Availability: {request.water}
- Maintenance Level Desired: {request.maintenance}

**Garden Preferences:**
- Garden Type: {request.garden_type}

**Instructions:**
1. Prioritize native plants for the region when possible
2. All plants MUST be compatible with zone {zone}
3. Match sun requirements to {sun_level} conditions
4. Respect water availability ({request.water}) and maintenance level ({request.maintenance})
5. Consider companion planting relationships
6. Indicate if each plant can be planted during the current season ({season})

**Required Response Format (JSON):**
Return ONLY a valid JSON object with this exact structure:

{{
  "location": "{request.location}",
  "season": "{season}",
  "plants": [
    {{
      "name": "Common Plant Name",
      "scientific_name": "Scientific Name",
      "sun_requirements": "Full Sun|Partial Sun|Shade",
      "water_needs": "Low|Medium|High",
      "maintenance_level": "Low|Medium|High",
      "plant_now": true|false,
      "spacing": "12-18 inches",
      "companion_plants": "companion plant 1, companion plant 2",
      "description": "Brief care notes and benefits"
    }}
  ]
}}

**Important:**
- Return ONLY the JSON object, no additional text
- Include 4-6 plants
- Ensure all plant data is accurate for zone {zone}
"""
    return prompt


async def call_genai_agent(prompt: str) -> Dict[str, Any]:
    """Call the GenAI Agent API."""
    if not DO_AGENT_API_KEY or not DO_AGENT_BASE_URL:
        raise HTTPException(
            status_code=503,
            detail="GenAI Agent not configured. Please check environment variables."
        )
    
    headers = {
        "Authorization": f"Bearer {DO_AGENT_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 2000,
        "k": 10,
        "retrieval_method": "rewrite",
        "include_retrieval_info": True,
        "stream": False
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{DO_AGENT_BASE_URL}/api/v1/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"GenAI Agent API error: {e.response.text}"
            )
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="Request to GenAI Agent timed out"
            )


def parse_agent_response(agent_response: Dict[str, Any]) -> Dict[str, Any]:
    """Parse the response from GenAI Agent."""
    try:
        choices = agent_response.get("choices", [])
        if not choices:
            raise ValueError("No choices in agent response")
        
        if "message" in choices[0]:
            content = choices[0]["message"]["content"]
        elif "delta" in choices[0]:
            content = choices[0]["delta"]["content"]
        else:
            raise ValueError("Invalid response structure from agent")
        
        try:
            recommendations = json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
                recommendations = json.loads(json_str)
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
                recommendations = json.loads(json_str)
            else:
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    recommendations = json.loads(json_match.group())
                else:
                    raise ValueError("Could not extract JSON from agent response")
        
        return recommendations
        
    except Exception as e:
        raise ValueError(f"Failed to parse agent response: {str(e)}")


@router.post(
    "/recommendations",
    response_model=RecommendationResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request data"},
        503: {"model": ErrorResponse, "description": "GenAI Agent unavailable"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_plant_recommendations(request: RecommendationRequest) -> RecommendationResponse:
    """
    Generate plant recommendations based on user preferences and location.
    
    This endpoint processes user input including location, yard direction,
    water availability, maintenance preferences, and garden type to generate
    personalized plant recommendations using GenAI Agent.
    
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
        
        # Step 1: Determine zone and season
        zone = get_hardiness_zone(request.location)
        season = get_current_season(zone)
        sun_level = map_direction_to_sun(request.direction)
        
        # Step 2: Construct prompt for GenAI Agent
        prompt = construct_agent_prompt(request, zone, season, sun_level)
        
        # Step 3: Call GenAI Agent
        agent_response = await call_genai_agent(prompt)
        
        # Step 4: Parse the agent's response
        recommendations = parse_agent_response(agent_response)
        
        # Step 5: Validate and create response model
        if "plants" not in recommendations:
            raise ValueError("Missing 'plants' field in GenAI Agent response")
        
        validated_plants = []
        for plant_data in recommendations["plants"]:
            try:
                # Map GenAI Agent response fields to our Plant model fields
                mapped_plant_data = {
                    "name": plant_data.get("name", "Unknown Plant"),
                    "scientific": plant_data.get("scientific_name", "Unknown species"),
                    "sun": plant_data.get("sun_requirements", "Partial Sun"),
                    "water": plant_data.get("water_needs", "Medium"),
                    "maintenance": plant_data.get("maintenance_level", "Medium"),
                    "plant_now": plant_data.get("plant_now", False),
                    "care_instructions": plant_data.get("description", "No care instructions available"),
                    "notes": plant_data.get("description", "No additional notes available")
                }
                
                plant = Plant(**mapped_plant_data)
                validated_plants.append(plant)
            except Exception as e:
                logger.warning(f"Skipping invalid plant data: {plant_data}, error: {e}")
                continue
        
        if not validated_plants:
            raise Exception("No valid plants in GenAI Agent response")
        
        # Create the final response
        response = RecommendationResponse(
            location=recommendations.get("location", request.location),
            season=recommendations.get("season", season),
            plants=validated_plants,
            generated_by="genai_agent"
        )
        
        # Calculate response time
        request_end_time = datetime.utcnow()
        response_time_ms = int((request_end_time - request_start_time).total_seconds() * 1000)
        
        # Update log data
        log_data.update({
            "success": True,
            "response_time_ms": response_time_ms,
            "plant_count": len(validated_plants)
        })
        
        # Log the successful request
        await log_request(log_data)
        
        logger.info(f"Successfully generated {len(validated_plants)} recommendations for {request.location}")
        
        return response
        
    except HTTPException:
        raise
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
            error_code = "genai_agent_unavailable"
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
            error_code = "genai_response_invalid"
            retry_suggested = True
        else:
            status_code = 500
            error_code = "genai_agent_failed"
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
        Dict with service status and GenAI Agent availability
    """
    return {
        "service": "recommendations",
        "status": "healthy",
        "genai_agent_configured": bool(DO_AGENT_API_KEY and DO_AGENT_BASE_URL),
        "timestamp": datetime.utcnow().isoformat()
    }