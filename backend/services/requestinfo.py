"""
FastAPI Backend for Smart Garden Planner
Integrates with DigitalOcean Gradient AI Agent
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import httpx
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
load_dotenv()

app = FastAPI(title="Smart Garden Planner API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
DO_AGENT_API_KEY = os.getenv("DO_AGENT_API_KEY")
DO_AGENT_BASE_URL = os.getenv("DO_AGENT_BASE_URL")

print(f"API Key: {'✓' if DO_AGENT_API_KEY else '✗'}")
print(f"Base URL: {DO_AGENT_BASE_URL}")

if not DO_AGENT_API_KEY or not DO_AGENT_BASE_URL:
    print("⚠️  Warning: DO_AGENT_API_KEY and DO_AGENT_BASE_URL not configured")
    print("The API will return mock data instead of calling the GenAI Agent")


# ============================================================================
# Pydantic Models
# ============================================================================

class PlantRecommendationRequest(BaseModel):
    """Request model for plant recommendations"""
    location: str = Field(..., description="User's address (e.g., '123 Main St, Denver, CO')")
    direction: str = Field(..., description="Yard direction (N, S, E, W, NE, SE, SW, NW)")
    water: str = Field(..., description="Water availability (Low, Medium, High)")
    maintenance: str = Field(..., description="Maintenance level (Low, Medium, High)")
    garden_type: str = Field(..., description="Garden type (Native Plants, Flower Garden, Vegetable Garden, Mixed)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "location": "Denver, CO",
                "direction": "S",
                "water": "Low",
                "maintenance": "Low",
                "garden_type": "Native Plants"
            }
        }


class Plant(BaseModel):
    """Individual plant recommendation"""
    name: str
    scientific_name: str = ""
    sun_requirements: str = "Partial Sun"
    water_needs: str = "Medium"
    maintenance_level: str = "Medium"
    plant_now: bool = False
    spacing: str = "12-18 inches"
    companion_plants: str = ""
    description: str = ""


class PlantRecommendationResponse(BaseModel):
    """Response model for plant recommendations"""
    zone: str
    season: str
    plants: List[Plant]


# ============================================================================
# Helper Functions
# ============================================================================

def get_hardiness_zone(location: str) -> str:
    """
    Determine USDA hardiness zone from location.
    TODO: Implement actual geocoding and zone lookup.
    For now, returns a default zone based on common cities.
    """
    location_lower = location.lower()
    
    # Simple lookup table - in production, use geocoding API
    zone_map = {
        "denver": "5b",
        "colorado": "5b",
        "seattle": "8b",
        "portland": "8b",
        "boston": "6b",
        "new york": "7a",
        "chicago": "6a",
        "atlanta": "8a",
        "miami": "10b",
        "los angeles": "10a",
        "phoenix": "9b",
        "austin": "8b",
        "dallas": "8a"
    }
    
    for city, zone in zone_map.items():
        if city in location_lower:
            return zone
    
    # Default zone
    return "6b"


def get_current_season(zone: str) -> str:
    """
    Determine current planting season based on date and zone.
    """
    month = datetime.now().month
    
    # Simplified season logic
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
        'N': 'shade',
        'NE': 'partial shade',
        'NW': 'partial shade',
        'E': 'partial sun',
        'W': 'partial sun',
        'SE': 'partial sun',
        'SW': 'partial sun',
        'S': 'full sun'
    }
    return sun_map.get(direction.upper(), 'partial sun')


def construct_agent_prompt(request: PlantRecommendationRequest, zone: str, season: str, sun_level: str) -> str:
    """
    Construct the prompt for the DO Gradient AI Agent.
    """
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
  "zone": "{zone}",
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


async def call_do_agent(prompt: str) -> Dict[str, Any]:
    """
    Call the DigitalOcean Gradient AI Agent API.
    """
    headers = {
        "Authorization": f"Bearer {DO_AGENT_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 2000,
        "k": 10,  # Retrieve top 10 results from knowledge base
        "retrieval_method": "rewrite",  # Use query rewriting for better retrieval
        "include_retrieval_info": True,  # Include info about retrieved documents
        "stream": False  # Get complete response at once
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
                detail=f"DO Agent API error: {e.response.text}"
            )
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="Request to DO Agent timed out"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error calling DO Agent: {str(e)}"
            )


def parse_agent_response(agent_response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse the response from DO Gradient AI Agent.
    Extract the plant recommendations from the response.
    """
    try:
        # Extract the message content from the response
        choices = agent_response.get("choices", [])
        if not choices:
            raise ValueError("No choices in agent response")
        
        # Get the message content
        if "message" in choices[0]:  # Non-streaming response
            content = choices[0]["message"]["content"]
        elif "delta" in choices[0]:  # Streaming response (shouldn't happen with stream=False)
            content = choices[0]["delta"]["content"]
        else:
            raise ValueError("Invalid response structure from agent")
        
        # The agent should return JSON directly
        # Try to parse it
        try:
            recommendations = json.loads(content)
        except json.JSONDecodeError:
            # If the agent wrapped the JSON in markdown code blocks, extract it
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
                # Try to extract JSON from text
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    recommendations = json.loads(json_match.group())
                else:
                    raise ValueError("Could not extract JSON from agent response")
        
        return recommendations
        
    except Exception as e:
        raise ValueError(f"Failed to parse agent response: {str(e)}")


# ============================================================================
# API Routes
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Smart Garden Planner API",
        "agent_configured": DO_AGENT_API_KEY is not None
    }


@app.post("/api/recommendations", response_model=PlantRecommendationResponse)
async def get_recommendations(request: PlantRecommendationRequest):
    """
    Get plant recommendations based on location and preferences.
    """
    try:
        # Step 1: Determine zone and season
        zone = get_hardiness_zone(request.location)
        season = get_current_season(zone)
        sun_level = map_direction_to_sun(request.direction)
        
        # Step 2: Try to call GenAI Agent, fallback to mock data
        if DO_AGENT_API_KEY and DO_AGENT_BASE_URL:
            try:
                # Step 3: Construct prompt for AI agent
                prompt = construct_agent_prompt(request, zone, season, sun_level)
                
                # Step 4: Call GenAI Agent
                agent_response = await call_do_agent(prompt)
                
                # Step 5: Parse the agent's response
                recommendations = parse_agent_response(agent_response)
                
                return PlantRecommendationResponse(**recommendations)
            except Exception as e:
                print(f"GenAI Agent failed: {e}, falling back to mock data")
        
        # Fallback: Return mock data
        mock_plants = [
            Plant(
                name="Purple Coneflower",
                scientific_name="Echinacea purpurea",
                sun_requirements="Full Sun",
                water_needs=request.water,
                maintenance_level=request.maintenance,
                plant_now=True,
                spacing="18-24 inches",
                companion_plants="Black-eyed Susan, Bee Balm",
                description="Native perennial that attracts butterflies and birds. Drought tolerant once established."
            ),
            Plant(
                name="Black-eyed Susan",
                scientific_name="Rudbeckia fulgida",
                sun_requirements="Full Sun",
                water_needs=request.water,
                maintenance_level=request.maintenance,
                plant_now=True,
                spacing="12-18 inches",
                companion_plants="Purple Coneflower, Bee Balm",
                description="Bright yellow flowers bloom from summer to fall. Very low maintenance native plant."
            ),
            Plant(
                name="Bee Balm",
                scientific_name="Monarda fistulosa",
                sun_requirements="Partial Sun",
                water_needs=request.water,
                maintenance_level=request.maintenance,
                plant_now=False,
                spacing="18-24 inches",
                companion_plants="Purple Coneflower, Black-eyed Susan",
                description="Fragrant native plant that attracts bees, butterflies, and hummingbirds."
            ),
            Plant(
                name="Little Bluestem",
                scientific_name="Schizachyrium scoparium",
                sun_requirements="Full Sun",
                water_needs="Low",
                maintenance_level="Low",
                plant_now=True,
                spacing="12-18 inches",
                companion_plants="Buffalo Grass, Blue Grama",
                description="Native ornamental grass with beautiful fall color. Extremely drought tolerant."
            )
        ]
        
        return PlantRecommendationResponse(
            zone=zone,
            season=season,
            plants=mock_plants
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendations: {str(e)}"
        )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Smart Garden Planner API",
        "docs": "/docs",
        "health": "/health"
    }


# ============================================================================
# For local development
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
