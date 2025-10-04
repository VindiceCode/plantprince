#!/usr/bin/env python3
"""
Run the simple Smart Garden Planner API.
"""
import subprocess
import sys
import os
from pathlib import Path

def run_api():
    """Run the simple FastAPI server."""
    print("🌿 Starting Simple Smart Garden Planner API")
    print("=" * 50)
    
    # Change to backend/services directory
    api_file = Path("backend/services/requestinfo.py")
    
    if not api_file.exists():
        print("❌ API file not found!")
        return False
    
    print("🚀 Starting API server...")
    print("API will be available at: http://localhost:8000")
    print("API docs will be available at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        # Run the API directly
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "backend.services.requestinfo:app",
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 API server stopped")
    except Exception as e:
        print(f"❌ Error starting API: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_api()
    sys.exit(0 if success else 1)