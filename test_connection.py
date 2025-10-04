#!/usr/bin/env python3
"""
Test connection to the API server.
"""
import requests
import json

def test_connection():
    """Test basic connection to the API."""
    print("🔍 Testing API Connection")
    print("=" * 30)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Health check
    try:
        print("1. Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Health check passed")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return False
    
    # Test 2: Root endpoint
    try:
        print("2. Testing root endpoint...")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Root endpoint passed")
        else:
            print(f"   ❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Root endpoint failed: {e}")
    
    # Test 3: Recommendations endpoint
    try:
        print("3. Testing recommendations endpoint...")
        test_data = {
            "location": "Denver, CO",
            "direction": "S",
            "water": "Medium",
            "maintenance": "Low",
            "garden_type": "Native Plants"
        }
        
        response = requests.post(
            f"{base_url}/api/recommendations",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Recommendations endpoint passed")
            print(f"   📊 Returned {len(result.get('plants', []))} plants")
            return True
        else:
            print(f"   ❌ Recommendations failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Recommendations failed: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    if success:
        print("\n🎉 All tests passed! API is working correctly.")
    else:
        print("\n💥 Some tests failed. Check the server.")
    
    exit(0 if success else 1)