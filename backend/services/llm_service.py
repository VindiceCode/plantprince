"""
GenAI Agent API service interface for plant recommendations.
"""
import os
import json
import httpx
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from models.schemas import RecommendationRequest, RecommendationResponse, Plant

# Ensure environment variables are loaded
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger(__name__)


class GenAIAgentService:
    """Service for interacting with GenAI Agent API."""
    
    def __init__(self):
        """Initialize the GenAI Agent service."""
        self.api_key = os.getenv("GENAI_API_KEY")
        self.endpoint = os.getenv("GENAI_ENDPOINT")
        self.timeout = int(os.getenv("LLM_TIMEOUT", "30"))
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "2000"))
        
        # Debug logging
        logger.debug(f"GENAI_API_KEY present: {bool(self.api_key)}")
        logger.debug(f"GENAI_ENDPOINT: {self.endpoint}")
        
        self.enabled = self._is_configured()
        
        if not self.enabled:
            logger.warning("GenAI Agent service not configured")
    
    def _is_configured(self) -> bool:
        """Check if GenAI Agent service is properly configured."""
        return all([
            self.api_key and self.api_key.strip(),
            self.endpoint and self.endpoint.strip()
        ])
    
    def _get_current_season(self) -> str:
        """Get current season description for planting context."""
        month = datetime.now().month
        
        if month in [12, 1, 2]:
            return "Winter - Indoor planning season"
        elif month in [3, 4, 5]:
            return "Spring - Prime planting season"
        elif month in [6, 7, 8]:
            return "Summer - Maintenance and late planting"
        else:  # 9, 10, 11
            return "Fall - Fall planting and preparation season"
    
    def _get_sun_exposure(self, direction: str) -> str:
        """Map yard direction to sun exposure description."""
        sun_mapping = {
            "N": "Shade to Partial Shade (north-facing)",
            "NE": "Partial Shade (northeast-facing)",
            "NW": "Partial Shade (northwest-facing)",
            "E": "Partial Sun (east-facing, morning sun)",
            "W": "Partial Sun (west-facing, afternoon sun)",
            "SE": "Partial Sun to Full Sun (southeast-facing)",
            "SW": "Partial Sun to Full Sun (southwest-facing)",
            "S": "Full Sun (south-facing)"
        }
        return sun_mapping.get(direction, "Unknown sun exposure")
    
    def _create_prompt(self, request: RecommendationRequest) -> str:
        """Create structured prompt for plant recommendations."""
        current_season = self._get_current_season()
        sun_exposure = self._get_sun_exposure(request.direction)
        
        prompt = f"""You are a professional gardening expert. Based on the following information, recommend 4-6 plants suitable for this specific location and preferences.

Location: {request.location}
Yard Direction: {request.direction} ({sun_exposure})
Water Availability: {request.water}
Maintenance Level: {request.maintenance}
Garden Type: {request.garden_type}
Current Season: {current_season}

Please respond with ONLY a valid JSON object in this exact format:
{{
  "location": "{request.location}",
  "season": "current planting season description",
  "plants": [
    {{
      "name": "common plant name",
      "scientific": "scientific name",
      "sun": "Full Sun|Partial Sun|Partial Shade|Shade",
      "water": "Low|Medium|High",
      "maintenance": "Low|Medium|High",
      "plant_now": true/false,
      "care_instructions": "brief care tips (50-100 words)",
      "notes": "why this plant suits their preferences (50-100 words)"
    }}
  ]
}}

Requirements:
- Focus on plants appropriate for the climate and region specified
- Consider the yard's sun exposure based on direction
- Match water and maintenance preferences
- Indicate if plants can be planted in the current season
- Provide practical, actionable care instructions
- Explain why each plant fits their specific needs
- Ensure all plants are realistic for the location's hardiness zone

Respond with ONLY the JSON object, no additional text."""

        return prompt
    
    async def get_recommendations(self, request: RecommendationRequest) -> RecommendationResponse:
        """
        Get plant recommendations from GenAI Agent service.
        
        Args:
            request: The recommendation request with user preferences
            
        Returns:
            RecommendationResponse with plant recommendations
            
        Raises:
            Exception: If GenAI Agent service fails or returns invalid data
        """
        if not self.enabled:
            raise Exception("GenAI Agent service not configured")
        
        prompt = self._create_prompt(request)
        
        # Prepare the API request for GenAI Agent API
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": self.max_tokens,
            "temperature": 0.7,
            "top_p": 0.9,
            "stream": False
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Sending GenAI Agent request for location: {request.location}")
                
                # Use the correct endpoint path for GenAI Agent API
                api_url = f"{self.endpoint.rstrip('/')}/api/v1/chat/completions"
                
                response = await client.post(
                    api_url,
                    headers=headers,
                    json=payload
                )
                
                response.raise_for_status()
                
                # Parse the response
                response_data = response.json()
                
                # Extract the content from the GenAI Agent response
                if "choices" not in response_data or not response_data["choices"]:
                    raise Exception("Invalid GenAI Agent response format: no choices")
                
                content = response_data["choices"][0].get("message", {}).get("content", "")
                
                if not content:
                    raise Exception("Empty response from GenAI Agent service")
                
                # Parse the JSON content
                try:
                    recommendation_data = json.loads(content.strip())
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse GenAI Agent JSON response: {content}")
                    raise Exception(f"Invalid JSON response from GenAI Agent: {str(e)}")
                
                # Validate and create the response model
                try:
                    # Ensure we have the required fields
                    if "plants" not in recommendation_data:
                        raise ValueError("Missing 'plants' field in GenAI Agent response")
                    
                    # Validate each plant
                    validated_plants = []
                    for plant_data in recommendation_data["plants"]:
                        try:
                            plant = Plant(**plant_data)
                            validated_plants.append(plant)
                        except Exception as e:
                            logger.warning(f"Skipping invalid plant data: {plant_data}, error: {e}")
                            continue
                    
                    if not validated_plants:
                        raise Exception("No valid plants in GenAI Agent response")
                    
                    # Create the final response
                    response_obj = RecommendationResponse(
                        location=recommendation_data.get("location", request.location),
                        season=recommendation_data.get("season", self._get_current_season()),
                        plants=validated_plants,
                        generated_by="genai_agent"
                    )
                    
                    logger.info(f"Successfully generated {len(validated_plants)} plant recommendations")
                    return response_obj
                    
                except Exception as e:
                    logger.error(f"Failed to validate GenAI Agent response: {e}")
                    raise Exception(f"Invalid response format from GenAI Agent: {str(e)}")
                
        except httpx.TimeoutException:
            logger.error("GenAI Agent request timed out")
            raise Exception("Request timed out - please try again")
        
        except httpx.HTTPStatusError as e:
            logger.error(f"GenAI Agent API error: {e.response.status_code} - {e.response.text}")
            if e.response.status_code == 401:
                raise Exception("Authentication failed - check API key")
            elif e.response.status_code == 429:
                raise Exception("Rate limit exceeded - please try again later")
            else:
                raise Exception(f"GenAI Agent service error: {e.response.status_code}")
        
        except Exception as e:
            logger.error(f"Unexpected error in GenAI Agent service: {e}")
            raise Exception(f"Failed to get recommendations: {str(e)}")


# Global instance
llm_service = GenAIAgentService()