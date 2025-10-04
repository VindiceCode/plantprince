"""
Pydantic models for API requests and responses.
"""
from typing import List
from enum import Enum
from pydantic import BaseModel, Field, validator


class DirectionEnum(str, Enum):
    """Yard direction options for sun exposure."""
    NORTH = "N"
    NORTHEAST = "NE"
    EAST = "E"
    SOUTHEAST = "SE"
    SOUTH = "S"
    SOUTHWEST = "SW"
    WEST = "W"
    NORTHWEST = "NW"


class WaterLevelEnum(str, Enum):
    """Water availability levels."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class MaintenanceLevelEnum(str, Enum):
    """Maintenance level preferences."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class GardenTypeEnum(str, Enum):
    """Garden type preferences."""
    NATIVE = "Native Plants"
    FLOWER = "Flower Garden"
    VEGETABLE = "Vegetable Garden"
    MIXED = "Mixed Garden"


class SunRequirementEnum(str, Enum):
    """Sun requirement levels for plants."""
    FULL_SUN = "Full Sun"
    PARTIAL_SUN = "Partial Sun"
    PARTIAL_SHADE = "Partial Shade"
    SHADE = "Shade"


class RecommendationRequest(BaseModel):
    """Request model for plant recommendations."""
    location: str = Field(
        ..., 
        min_length=3, 
        max_length=100,
        description="City and state, e.g., 'Denver, CO'"
    )
    direction: DirectionEnum = Field(
        ...,
        description="Yard direction for sun exposure calculation"
    )
    water: WaterLevelEnum = Field(
        ...,
        description="Available water level for plants"
    )
    maintenance: MaintenanceLevelEnum = Field(
        ...,
        description="Desired maintenance level"
    )
    garden_type: GardenTypeEnum = Field(
        ...,
        description="Type of garden to create"
    )

    @validator('location')
    def validate_location(cls, v):
        """Validate location format."""
        if not v or v.strip() == "":
            raise ValueError("Location cannot be empty")
        
        # Basic validation for city, state format
        parts = v.split(',')
        if len(parts) < 2:
            raise ValueError("Location should include city and state (e.g., 'Denver, CO')")
        
        return v.strip()


class Plant(BaseModel):
    """Plant recommendation model."""
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Common plant name"
    )
    scientific: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Scientific plant name"
    )
    sun: SunRequirementEnum = Field(
        ...,
        description="Sun requirements for the plant"
    )
    water: WaterLevelEnum = Field(
        ...,
        description="Water requirements for the plant"
    )
    maintenance: MaintenanceLevelEnum = Field(
        ...,
        description="Maintenance level required"
    )
    plant_now: bool = Field(
        ...,
        description="Whether the plant can be planted in current season"
    )
    care_instructions: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Brief care instructions"
    )
    notes: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Why this plant suits the user's preferences"
    )


class RecommendationResponse(BaseModel):
    """Response model for plant recommendations."""
    location: str = Field(
        ...,
        description="The location for which recommendations were generated"
    )
    season: str = Field(
        ...,
        min_length=5,
        max_length=100,
        description="Current planting season description"
    )
    plants: List[Plant] = Field(
        ...,
        min_items=1,
        max_items=10,
        description="List of recommended plants"
    )
    generated_by: str = Field(
        default="llm",
        description="Source of the recommendations"
    )

    @validator('plants')
    def validate_plants_count(cls, v):
        """Ensure we have a reasonable number of plant recommendations."""
        if len(v) < 1:
            raise ValueError("At least one plant recommendation is required")
        if len(v) > 10:
            raise ValueError("Too many plant recommendations (max 10)")
        return v


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(
        ...,
        description="Error code or type"
    )
    message: str = Field(
        ...,
        description="Human-readable error message"
    )
    retry_suggested: bool = Field(
        default=False,
        description="Whether the user should retry the request"
    )