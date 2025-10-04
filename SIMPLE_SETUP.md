# Simple Smart Garden Planner Setup

This is a simplified setup that works with just two files and minimal dependencies.

## Quick Start

### 1. Start the API Server
```bash
python run_simple_api.py
```

### 2. Open the Frontend
Open `frontend/index.html` in your browser or serve it with:
```bash
python serve_frontend.py
```

### 3. Test the API (Optional)
```bash
python test_simple_api.py
```

## How It Works

1. **Backend**: `backend/services/requestinfo.py` - Simple FastAPI app
2. **Frontend**: `frontend/index.html` - Static HTML with jQuery
3. **GenAI Integration**: Calls your custom GenAI Agent API
4. **Fallback**: Returns mock plant data if GenAI Agent isn't configured

## Environment Variables

Create `backend/.env` with:
```
DO_AGENT_API_KEY=your_api_key_here
DO_AGENT_BASE_URL=https://your-agent-url.agents.do-ai.run
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /api/recommendations` - Get plant recommendations
- `GET /docs` - API documentation

## Frontend Usage

1. Fill out the form with:
   - Location (e.g., "Denver, CO")
   - Yard direction (N, S, E, W, etc.)
   - Water availability (Low, Medium, High)
   - Maintenance level (Low, Medium, High)
   - Garden type (Native Plants, Flower Garden, etc.)

2. Click "Get My Plant Plan"

3. View personalized plant recommendations

## Troubleshooting

- **CORS Error**: Make sure you're serving the HTML file via HTTP (not opening directly)
- **API Not Found**: Ensure the backend is running on port 8000
- **No Recommendations**: Check that environment variables are set correctly

The system will work with mock data even if the GenAI Agent isn't configured!