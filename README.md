# Smart Garden Planner

AI-powered plant recommendations using LLM services.

## Development Setup

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

### Prerequisites

- Python 3.11+
- uv (install from https://docs.astral.sh/uv/getting-started/installation/)

### Local Development

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Run the development server:
   ```bash
   uv run uvicorn main:app --reload
   ```

3. Access the API at http://localhost:8000
   - API docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

### Docker Development

1. Build and run with docker-compose:
   ```bash
   docker-compose up --build
   ```

2. Access the API at http://localhost:8000

### Project Structure

```
├── main.py              # FastAPI application entry point
├── models/              # Pydantic models
├── services/            # Business logic and external API clients
├── routes/              # API route handlers
├── pyproject.toml       # Project configuration and dependencies
├── Dockerfile           # Container configuration
└── docker-compose.yml   # Local development orchestration
```

## Environment Variables

Create a `.env` file with:

```bash
DIGITAL_OCEAN_LLM_API_KEY=your_key_here
DIGITAL_OCEAN_LLM_ENDPOINT=your_endpoint_here
ENVIRONMENT=development
DEBUG=true
```