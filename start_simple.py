#!/usr/bin/env python3
"""
Start the simple Smart Garden Planner with dependency checking.
"""
import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = ['fastapi', 'uvicorn', 'httpx', 'pydantic', 'python-dotenv']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("Install with: pip install fastapi uvicorn httpx pydantic python-dotenv")
        return False
    
    print("✅ All dependencies found")
    return True

def start_server():
    """Start the simple test server."""
    print("🌿 Starting Simple Smart Garden Planner")
    print("=" * 40)
    
    if not check_dependencies():
        return False
    
    # Check if .env file exists
    env_file = Path("backend/.env")
    if env_file.exists():
        print("✅ Environment file found")
    else:
        print("⚠️  No .env file found - will use mock data")
    
    print("\n🚀 Starting server...")
    print("Frontend: Open frontend/index.html in browser")
    print("Backend:  http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop")
    
    try:
        # Start the simple test server using uv
        subprocess.run([
            "uv", "run", "--project", "backend", "python", "../simple_test_server.py"
        ])
        return True
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = start_server()
    sys.exit(0 if success else 1)