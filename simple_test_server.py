#!/usr/bin/env python3
"""
Super simple test server to verify basic functionality.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Test API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Test API is working!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/recommendations")
async def get_recommendations(request: dict):
    """Simple test endpoint that returns mock data."""
    return {
        "zone": "6b",
        "season": "Fall Planting Season",
        "plants": [
            {
                "name": "Purple Coneflower",
                "scientific_name": "Echinacea purpurea",
                "sun_requirements": "Full Sun",
                "water_needs": "Medium",
                "maintenance_level": "Low",
                "plant_now": True,
                "spacing": "18-24 inches",
                "companion_plants": "Black-eyed Susan, Bee Balm",
                "description": "Native perennial that attracts butterflies and birds."
            },
            {
                "name": "Black-eyed Susan",
                "scientific_name": "Rudbeckia fulgida",
                "sun_requirements": "Full Sun",
                "water_needs": "Low",
                "maintenance_level": "Low",
                "plant_now": True,
                "spacing": "12-18 inches",
                "companion_plants": "Purple Coneflower",
                "description": "Bright yellow flowers bloom from summer to fall."
            }
        ]
    }

if __name__ == "__main__":
    print("🌿 Starting Simple Test Server")
    print("Available at: http://localhost:8000")
    print("Test endpoint: http://localhost:8000/api/recommendations")
    print("Press Ctrl+C to stop")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)