#!/usr/bin/env python3
"""
Start the Smart Garden Planner using uv.
"""
import subprocess
import sys
import os
from pathlib import Path

def start_server():
    """Start the server using uv."""
    print("🌿 Starting Smart Garden Planner with UV")
    print("=" * 40)
    
    # Check if uv is available
    try:
        subprocess.run(["uv", "--version"], capture_output=True, check=True)
        print("✅ UV found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ UV not found. Please install uv first:")
        print("curl -LsSf https://astral.sh/uv/install.sh | sh")
        return False
    
    # Check if backend directory exists
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return False
    
    print("✅ Backend directory found")
    
    print("\n🚀 Starting server...")
    print("Backend:  http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("Frontend: Open frontend/index.html in browser")
    print("\nPress Ctrl+C to stop")
    
    try:
        # Start using the existing backend structure
        subprocess.run([
            "uv", "run", "--project", "backend", 
            "uvicorn", "services.requestinfo:app",
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
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