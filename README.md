# Smart Garden Planner

AI-powered plant recommendations using Digital Ocean's LLM services. This ultra-minimal application provides personalized plant recommendations based on location and gardening preferences.

## Quick Start with Docker

The fastest way to get started is using Docker:

1. **Clone and setup environment:**
   ```bash
   git clone <repository-url>
   cd smart-garden-planner
   cp .env.example .env
   ```

2. **Configure your Digital Ocean LLM API:**
   Edit `.env` and add your Digital Ocean LLM credentials:
   ```bash
   DIGITAL_OCEAN_LLM_API_KEY=your_api_key_here
   DIGITAL_OCEAN_LLM_ENDPOINT=your_endpoint_here
   ```

3. **Run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

4. **Access the application:**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## Development Setup

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) for dependency management
- Docker and Docker Compose (for containerized development)

### Local Development (without Docker)

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Setup environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Digital Ocean LLM credentials
   ```

3. **Run the development server:**
   ```bash
   uv run uvicorn main:app --reload
   ```

4. **Access the API at http://localhost:8000**

### Docker Development

#### Development Mode (with hot reload)
```bash
# Build and run with hot reload
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

#### Production Mode
```bash
# Build production image
docker build -t smart-garden-planner .

# Run with environment variables (managed by Terraform in production)
docker run -p 8000:8000 \
  -e DIGITAL_OCEAN_LLM_API_KEY=$DIGITAL_OCEAN_LLM_API_KEY \
  -e DIGITAL_OCEAN_LLM_ENDPOINT=$DIGITAL_OCEAN_LLM_ENDPOINT \
  -e ENVIRONMENT=production \
  smart-garden-planner

# Or with .env file for local testing
docker run -p 8000:8000 --env-file .env smart-garden-planner
```

## Configuration

### Required Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Digital Ocean LLM API Configuration (REQUIRED)
DIGITAL_OCEAN_LLM_API_KEY=your_api_key_here
DIGITAL_OCEAN_LLM_ENDPOINT=your_endpoint_here

# Digital Ocean Spaces Configuration (OPTIONAL - for request/response backup)
DO_SPACES_KEY=your_spaces_access_key_here
DO_SPACES_SECRET=your_spaces_secret_key_here
DO_SPACES_ENDPOINT=https://nyc3.digitaloceanspaces.com
DO_SPACES_REGION=nyc3
DO_SPACES_BUCKET=garden-planner-logs

# Application Configuration
ENVIRONMENT=development
DEBUG=true

# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./garden_planner.db

# Optional: Logging Configuration
LOG_LEVEL=INFO
```

### Digital Ocean Setup

1. **LLM API Access:**
   - Sign up for Digital Ocean
   - Enable LLM services in your account
   - Generate API key and endpoint URL

2. **Spaces (Optional):**
   - Create a Digital Ocean Space for request/response logging
   - Generate Spaces access keys

3. **Environment Management:**
   - **Local Development:** Use `.env` file for local testing
   - **Production/Staging:** Environment variables managed via Terraform
   - **Docker:** Environment variables passed through container runtime

## API Usage

### Get Plant Recommendations

```bash
curl -X POST "http://localhost:8000/api/recommendations" \
     -H "Content-Type: application/json" \
     -d '{
       "location": "Denver, CO",
       "direction": "S",
       "water": "Low",
       "maintenance": "Low",
       "garden_type": "Native Plants"
     }'
```

### Response Format

```json
{
  "location": "Denver, CO",
  "season": "Fall Planting Season",
  "plants": [
    {
      "name": "Blue Grama Grass",
      "scientific": "Bouteloua gracilis",
      "sun": "Full Sun",
      "water": "Low",
      "maintenance": "Low",
      "plant_now": true,
      "care_instructions": "Drought tolerant once established...",
      "notes": "Perfect for low-water gardens..."
    }
  ],
  "generated_by": "llm"
}
```

## Project Structure

```
├── main.py                 # FastAPI application entry point
├── config.py               # Environment configuration management
├── models/                 # Data models and database
│   ├── database.py         # Database connection and setup
│   └── schemas.py          # Pydantic models for API
├── services/               # Business logic and external services
│   ├── llm_service.py      # Digital Ocean LLM integration
│   ├── logging_service.py  # Request/response logging
│   └── storage.py          # Digital Ocean Spaces integration
├── routes/                 # API route handlers
│   └── recommendations.py  # Plant recommendation endpoints
├── pyproject.toml          # Project configuration and dependencies
├── Dockerfile              # Container configuration
├── docker-compose.yml      # Development orchestration
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Database

The application uses SQLite for simplicity:
- **Development:** Local SQLite file
- **Docker:** Persistent volume for database storage
- **Schema:** Minimal logging of requests and responses

## Troubleshooting

### Common Issues

1. **LLM API Errors:**
   - Verify your Digital Ocean LLM API key and endpoint
   - Check API quota and billing status
   - Review logs for specific error messages

2. **Docker Issues:**
   ```bash
   # Rebuild containers
   docker-compose down
   docker-compose up --build

   # Clear volumes (will reset database)
   docker-compose down -v
   ```

3. **Database Issues:**
   ```bash
   # Reset database in Docker
   docker-compose down -v
   docker-compose up --build
   ```

### Logs

```bash
# View application logs
docker-compose logs -f api

# View all logs
docker-compose logs -f
```

## Terraform Integration

This application is designed to work with Terraform-managed infrastructure:

### Environment Variables via Terraform

The application expects these environment variables to be provided by your Terraform configuration:

```hcl
# Example Terraform variables for container deployment
resource "digitalocean_app" "garden_planner" {
  spec {
    name   = "smart-garden-planner"
    region = "nyc"

    service {
      name               = "api"
      environment_slug   = "python"
      instance_count     = 1
      instance_size_slug = "basic-xxs"

      env {
        key   = "DIGITAL_OCEAN_LLM_API_KEY"
        value = var.do_llm_api_key
        type  = "SECRET"
      }

      env {
        key   = "DIGITAL_OCEAN_LLM_ENDPOINT"
        value = var.do_llm_endpoint
      }

      env {
        key   = "ENVIRONMENT"
        value = "production"
      }

      # Optional: Digital Ocean Spaces
      env {
        key   = "DO_SPACES_KEY"
        value = var.do_spaces_key
        type  = "SECRET"
      }
    }
  }
}
```

### Local Development vs Production

- **Local:** Use `.env` file for development and testing
- **Production:** Environment variables injected by Terraform/infrastructure
- **Docker:** Supports both `.env` files and runtime environment variables

## Development Notes

- The application prioritizes simplicity and rapid development
- Only Digital Ocean LLM service is used for plant recommendations
- No external plant databases or complex APIs
- SQLite database for minimal setup complexity
- Optional Digital Ocean Spaces for request/response backup
- Environment configuration designed for Terraform management