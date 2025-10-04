#!/usr/bin/env python3
"""
Start the Smart Garden Planner backend server.
"""
import subprocess
import sys
import os
from pathlib import Path

def start_backend():
    """Start the FastAPI backend server."""
    backend_dir = Path("backend")
    
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return False
    
    print("🚀 Starting Smart Garden Planner Backend")
    print("Backend will be available at: http://localhost:8000")
    print("API docs will be available at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        # Change to backend directory and start uvicorn
        os.chdir(backend_dir)
        subprocess.run([
            "uv", "run", "uvicorn", "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Backend server stopped")
    except FileNotFoundError:
        print("❌ 'uv' command not found. Please install uv or use:")
        print("cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
        return False
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = start_backend()
    sys.exit(0 if success else 1)