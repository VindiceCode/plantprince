#!/usr/bin/env python3
"""
Test the simple Smart Garden Planner API.
"""
import asyncio
import httpx
import json

async def test_api():
    """Test the API endpoint."""
    print("🌿 Testing Simple Smart Garden Planner API")
    print("=" * 50)
    
    test_data = {
        "location": "Denver, CO",
        "direction": "S",
        "water": "Medium",
        "maintenance": "Low",
        "garden_type": "Native Plants"
    }
    
    print(f"📤 Sending request:")
    print(json.dumps(test_data, indent=2))
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:8000/api/recommendations",
                json=test_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print("\n✅ Success! Response:")
                print(f"Zone: {result.get('zone')}")
                print(f"Season: {result.get('season')}")
                print(f"Plants: {len(result.get('plants', []))}")
                
                for i, plant in enumerate(result.get('plants', []), 1):
                    print(f"\n{i}. {plant.get('name')}")
                    print(f"   Scientific: {plant.get('scientific_name')}")
                    print(f"   Sun: {plant.get('sun_requirements')}")
                    print(f"   Water: {plant.get('water_needs')}")
                    print(f"   Plant now: {'Yes' if plant.get('plant_now') else 'No'}")
                
                return True
            else:
                print(f"\n❌ Error: {response.status_code}")
                print(response.text)
                return False
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_api())
    exit(0 if success else 1)