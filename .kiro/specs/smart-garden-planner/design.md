# Design Document

## Overview

The Smart Garden Planner is designed as an ultra-minimal viable product focusing purely on LLM-powered plant recommendations. The system uses a simple FastAPI backend with a React frontend, eliminating all external APIs except Digital Ocean's LLM service. The architecture prioritizes extreme simplicity and rapid development with minimal dependencies.

## Architecture

### High-Level Architecture

```
┌─────────────────┐    HTTP/JSON    ┌─────────────────┐
│   React SPA     │ ◄──────────────► │  FastAPI Server │
│   (Frontend)    │                  │   (Backend)     │
└─────────────────┘                  └─────────────────┘
                                              │
                                              ▼
                                     ┌─────────────────┐
                                     │ Digital Ocean   │
                                     │   LLM Service   │
                                     └─────────────────┘
```

### Technology Stack

**Backend:**
- FastAPI (Python) - Fast development, automatic API docs
- Pydantic - Data validation and serialization
- httpx - Async HTTP client for LLM API
- uvicorn - ASGI server

**Frontend:**
- React (existing component) - Already implemented UI
- Axios - HTTP client for API calls

**External Services:**
- Digital Ocean LLM API - All plant recommendations and gardening advice

## Components and Interfaces

### Backend Components

#### 1. Main Application (`main.py`)
- FastAPI app initialization
- CORS middleware for frontend communication
- Single route registration
- Basic error handling middleware

#### 2. API Routes (`routes/`)

**Recommendations Service (`routes/recommendations.py`)**
```python
POST /api/recommendations
{
  "location": "Denver, CO",
  "direction": "S",
  "water": "Low",
  "maintenance": "Low",
  "garden_type": "Native Plants"
}
→ {
  "location": "Denver, CO",
  "season": "Fall Planting Season",
  "plants": [...],
  "generated_by": "llm"
}
```

#### 3. Services (`services/`)

**LLM Service (`services/llm_service.py`)**
- Interface to Digital Ocean LLM API
- Prompt engineering for plant recommendations
- JSON response parsing and validation
- Error handling for API failures

#### 4. Models (`models/`)

**Request Models**
```python
class RecommendationRequest(BaseModel):
    location: str    # "Denver, CO" or "Austin, TX"
    direction: str   # N, S, E, W, etc.
    water: str       # Low, Medium, High
    maintenance: str # Low, Medium, High
    garden_type: str # Native Plants, Flower Garden, etc.
```

**Response Models**
```python
class Plant(BaseModel):
    name: str
    scientific: str
    sun: str
    water: str
    maintenance: str
    plant_now: bool
    care_instructions: str
    notes: str

class RecommendationResponse(BaseModel):
    location: str
    season: str
    plants: List[Plant]
    generated_by: str
```

### Frontend Integration

The existing React component will be updated to:
1. Replace mock API calls with single FastAPI endpoint
2. Add proper error handling for LLM API failures
3. Implement loading states during LLM processing
4. Handle edge cases (no recommendations, malformed LLM responses)

## Data Models

### LLM Prompt Structure
```python
PLANT_RECOMMENDATION_PROMPT = """
You are a gardening expert. Based on the following information, recommend 4-6 plants suitable for this location and preferences:

Location: {location}
Yard Direction: {direction} (affects sun exposure)
Water Availability: {water}
Maintenance Level: {maintenance}
Garden Type: {garden_type}
Current Season: {current_season}

Please respond with a JSON object containing:
- location: the provided location
- season: current planting season description
- plants: array of plant objects with:
  - name: common plant name
  - scientific: scientific name
  - sun: sun requirements (Full Sun/Partial Sun/Shade)
  - water: water needs (Low/Medium/High)
  - maintenance: care level (Low/Medium/High)
  - plant_now: boolean if plantable in current season
  - care_instructions: brief care tips
  - notes: why this plant suits their preferences

Focus on plants appropriate for the climate and region specified.
"""
```

### Sun Exposure Mapping
```python
SUN_MAPPING = {
    "N": "Shade to Partial Shade",
    "NE": "Partial Shade", "NW": "Partial Shade",
    "E": "Partial Sun", "W": "Partial Sun",
    "SE": "Partial Sun", "SW": "Partial Sun",
    "S": "Full Sun"
}
```

## Error Handling

### API Error Responses
```python
{
    "error": "llm_service_failed",
    "message": "Unable to generate recommendations. Please try again.",
    "retry_suggested": true
}
```

### Fallback Strategies
1. **LLM Service Down**: Display user-friendly error with retry option
2. **Malformed LLM Response**: Request user to try again with different inputs
3. **Invalid JSON from LLM**: Parse partial response or show error
4. **Timeout**: Suggest trying again or simplifying the request

## Testing Strategy

### Manual Testing Focus (Ultra-Simple Approach)
1. **Happy Path Testing**: Complete user flow with valid inputs
2. **Error Scenarios**: LLM API failures, malformed responses
3. **Edge Cases**: Unusual locations, extreme preferences
4. **Browser Testing**: Chrome/Firefox compatibility

### API Testing
- Test single endpoint with FastAPI auto-docs
- Verify LLM response parsing
- Test with various location inputs

### Integration Testing
- Frontend-backend communication
- LLM API integration
- Error handling activation

## Deployment Considerations

### Environment Variables
```bash
# Required
DIGITAL_OCEAN_LLM_API_KEY=your_key_here
DIGITAL_OCEAN_LLM_ENDPOINT=your_endpoint_here

# Optional
ENVIRONMENT=development
DEBUG=true
```

### Quick Deployment Options
1. **Local Development**: `uvicorn main:app --reload`
2. **Demo Deployment**: Railway, Render, or Vercel
3. **Static Frontend**: Netlify or Vercel for React build

## Performance Considerations

### Optimization for Demo
- Implement request timeouts (10 seconds max for LLM)
- Use async/await for LLM API calls
- Cache common location requests if needed
- Keep prompts concise for faster LLM response

### Monitoring
- Log all LLM requests/responses
- Track LLM service response times
- Monitor error rates for retry logic