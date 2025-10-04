#!/bin/bash

echo "🌿 Starting Smart Garden Planner with Docker"
echo "============================================="

# Kill any processes on port 8000
echo "🔍 Checking for processes on port 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "No process found on port 8000"

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start services
echo "🚀 Building and starting services..."
docker-compose up --build -d

# Wait a moment for services to start
sleep 3

# Check status
echo "📊 Service status:"
docker-compose ps

echo ""
echo "✅ Services should be running at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "To stop services: docker-compose down"
echo "To view logs: docker-compose logs -f"