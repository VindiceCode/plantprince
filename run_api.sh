#!/bin/bash

echo "🌿 Starting Smart Garden Planner API"
echo "====================================="

# Kill any existing process on port 8000
echo "🔍 Checking for processes on port 8000..."
if lsof -ti:8000 >/dev/null 2>&1; then
    echo "Found process on port 8000, killing it..."
    lsof -ti:8000 | xargs kill -9
    sleep 2
    echo "Process killed"
else
    echo "No process on port 8000"
fi

echo "🚀 Starting API server..."
echo "Backend:  http://localhost:8001"
echo "API Docs: http://localhost:8001/docs"
echo "Frontend: Open frontend/index.html in browser"
echo ""
echo "Press Ctrl+C to stop"

# Start the API using uv (run from backend directory)
cd backend && uv run uvicorn services.requestinfo:app --host 0.0.0.0 --port 8001 --reload