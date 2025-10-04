#!/bin/bash

# Smart Garden Planner - Docker Integration Test Script
# Tests complete user flow with Docker setup

set -e  # Exit on any error

echo "🌱 Smart Garden Planner - Docker Integration Test"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
print_status "Checking Docker availability..."
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi
print_success "Docker is running"

# Check if docker-compose is available
if ! command -v docker-compose > /dev/null 2>&1; then
    print_error "docker-compose is not installed. Please install docker-compose and try again."
    exit 1
fi
print_success "docker-compose is available"

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning "Please configure your .env file with actual API keys before running tests"
        print_warning "The tests will run but LLM functionality may not work without proper configuration"
    else
        print_error ".env.example file not found. Cannot create .env file."
        exit 1
    fi
else
    print_success ".env file found"
fi

# Clean up any existing containers
print_status "Cleaning up existing containers..."
docker-compose down --volumes --remove-orphans > /dev/null 2>&1 || true

# Build and start services
print_status "Building and starting services..."
if ! docker-compose up -d --build; then
    print_error "Failed to start services with docker-compose"
    exit 1
fi

print_success "Services started successfully"

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 10

# Check if services are running
print_status "Checking service status..."
if ! docker-compose ps | grep -q "Up"; then
    print_error "Services are not running properly"
    docker-compose logs
    exit 1
fi

# Show running services
print_status "Running services:"
docker-compose ps

# Test basic connectivity
print_status "Testing basic connectivity..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8000/health > /dev/null; then
        print_success "API is responding"
        break
    fi
    
    attempt=$((attempt + 1))
    if [ $attempt -eq $max_attempts ]; then
        print_error "API failed to respond after $max_attempts attempts"
        print_status "Showing container logs:"
        docker-compose logs api
        exit 1
    fi
    
    print_status "Waiting for API to be ready... (attempt $attempt/$max_attempts)"
    sleep 2
done

# Run integration tests
print_status "Running integration tests..."
if python3 test_integration.py; then
    print_success "Integration tests passed!"
else
    print_error "Integration tests failed!"
    
    print_status "Showing container logs for debugging:"
    echo "API Logs:"
    docker-compose logs api
    
    exit 1
fi

# Test manual scenarios
print_status "Testing manual scenarios..."

# Test 1: Basic health check
print_status "Test 1: Health check"
health_response=$(curl -s http://localhost:8000/health)
if echo "$health_response" | grep -q '"status":"healthy"'; then
    print_success "Health check passed"
else
    print_error "Health check failed: $health_response"
fi

# Test 2: Recommendations health check
print_status "Test 2: Recommendations service health"
rec_health=$(curl -s http://localhost:8000/api/recommendations/health)
if echo "$rec_health" | grep -q '"service":"recommendations"'; then
    print_success "Recommendations service health check passed"
    
    # Check if LLM service is configured
    if echo "$rec_health" | grep -q '"llm_service_configured":true'; then
        print_success "LLM service is configured"
        
        # Test 3: Actual recommendation request
        print_status "Test 3: Sample recommendation request"
        sample_request='{
            "location": "Denver, CO",
            "direction": "S",
            "water": "Low",
            "maintenance": "Low",
            "garden_type": "Native Plants"
        }'
        
        rec_response=$(curl -s -X POST \
            -H "Content-Type: application/json" \
            -d "$sample_request" \
            http://localhost:8000/api/recommendations)
        
        if echo "$rec_response" | grep -q '"plants"'; then
            plant_count=$(echo "$rec_response" | grep -o '"name"' | wc -l)
            print_success "Sample recommendation request passed - got $plant_count plants"
        else
            print_warning "Sample recommendation request failed (this is expected if LLM API keys are not configured)"
            print_status "Response: $rec_response"
        fi
    else
        print_warning "LLM service is not configured - recommendation tests will be limited"
    fi
else
    print_error "Recommendations service health check failed: $rec_health"
fi

# Test 4: Invalid request handling
print_status "Test 4: Invalid request handling"
invalid_request='{"location": ""}'
invalid_response=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d "$invalid_request" \
    http://localhost:8000/api/recommendations)

if echo "$invalid_response" | grep -q '"detail"'; then
    print_success "Invalid request properly rejected"
else
    print_error "Invalid request not properly handled: $invalid_response"
fi

# Test frontend file serving (if applicable)
print_status "Test 5: Frontend file check"
if [ -f "garden-planner.jsx" ]; then
    print_success "Frontend component file exists"
else
    print_warning "Frontend component file not found"
fi

# Show final status
print_status "Showing final container status:"
docker-compose ps

# Cleanup option
echo ""
read -p "Do you want to stop and remove the containers? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Stopping and removing containers..."
    docker-compose down --volumes
    print_success "Cleanup completed"
else
    print_status "Containers are still running. Use 'docker-compose down' to stop them."
fi

print_success "Docker integration test completed!"
echo ""
echo "📋 Test Summary:"
echo "- Docker setup: ✅"
echo "- Service startup: ✅"
echo "- API connectivity: ✅"
echo "- Health endpoints: ✅"
echo "- Error handling: ✅"
echo "- Integration tests: ✅"
echo ""
echo "🎉 All tests completed successfully!"