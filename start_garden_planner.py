#!/usr/bin/env python3
"""
Start both frontend and backend for Smart Garden Planner.
"""
import subprocess
import sys
import os
import time
import signal
from pathlib import Path

def start_services():
    """Start both frontend and backend services."""
    print("🌿 Starting Smart Garden Planner")
    print("=" * 50)
    
    processes = []
    
    try:
        # Start backend
        print("🚀 Starting backend server...")
        backend_process = subprocess.Popen([
            "uv", "run", "--project", "backend", 
            "uvicorn", "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], cwd="backend")
        processes.append(("Backend", backend_process))
        
        # Wait a moment for backend to start
        time.sleep(2)
        
        # Start frontend
        print("🌐 Starting frontend server...")
        frontend_process = subprocess.Popen([
            sys.executable, "serve_frontend.py"
        ])
        processes.append(("Frontend", frontend_process))
        
        print("\n✅ Services started successfully!")
        print("Frontend: http://localhost:3000")
        print("Backend:  http://localhost:8000")
        print("API Docs: http://localhost:8000/docs")
        print("\nPress Ctrl+C to stop all services")
        
        # Wait for processes
        while True:
            time.sleep(1)
            # Check if any process has died
            for name, process in processes:
                if process.poll() is not None:
                    print(f"❌ {name} process has stopped")
                    return False
    
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        for name, process in processes:
            print(f"Stopping {name}...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        print("👋 All services stopped")
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = start_services()
    sys.exit(0 if success else 1)