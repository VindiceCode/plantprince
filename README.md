# Smart Garden Planner

AI-powered plant recommendations using your custom GenAI Agent API.

## Quick Start

### 1. Start the API Server
```bash
./run_api.sh
```

### 2. Open the Frontend
Open `frontend/index.html` in your browser or serve it with:
```bash
python serve_frontend.py
```

That's it! The app will be running at:
- **Backend**: http://localhost:8001
- **Frontend**: Open `frontend/index.html` in browser
- **API Docs**: http://localhost:8001/docs

## How It Works

1. **Backend**: `backend/services/requestinfo.py` - FastAPI app with GenAI Agent integration
2. **Frontend**: `frontend/index.html` - Static HTML with jQuery
3. **GenAI Integration**: Calls your custom GenAI Agent API for plant recommendations
4. **Smart Fallback**: Returns realistic mock plant data if GenAI Agent isn't configured

## Environment Variables

The API will work with mock data by default. To use your GenAI Agent, create `backend/.env`:

```bash
# GenAI Agent API Configuration
DO_AGENT_API_KEY=your_api_key_here
DO_AGENT_BASE_URL=https://your-agent-url.agents.do-ai.run
```

## Using the App

1. **Fill out the garden form:**
   - Location (e.g., "Denver, CO")
   - Yard direction (N, S, E, W, NE, SE, SW, NW)
   - Water availability (Low, Medium, High)
   - Maintenance level (Low, Medium, High)
   - Garden type (Native Plants, Flower Garden, Vegetable Garden, Mixed)

2. **Click "Get My Plant Plan"**

3. **View your personalized recommendations:**
   - 4-6 native plants suited to your location and preferences
   - Plant details: sun requirements, water needs, maintenance level
   - Planting timing (can plant now or wait for season)
   - Companion plant suggestions
   - Care instructions

4. **Customize your selection:**
   - Check/uncheck plants to customize your garden plan
   - View selection count
   - Print your final garden plan

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check  
- `POST /api/recommendations` - Get plant recommendations
- `GET /docs` - Interactive API documentation

## Troubleshooting

**Port already in use:**
```bash
# Kill any process on port 8001
lsof -ti:8001 | xargs kill -9
```

**Permission errors with .venv:**
```bash
# Clean up and let uv recreate
sudo rm -rf backend/.venv
./run_api.sh
```

**CORS errors:**
- Make sure you're serving the HTML file via HTTP (use `python serve_frontend.py`)
- Don't open `index.html` directly in browser

**No plant recommendations:**
- Check that the API is running on http://localhost:8001
- The system works with mock data even without GenAI Agent configured

## Development

**View logs:**
The API server shows real-time logs including:
- GenAI Agent configuration status
- API requests and responses
- Error messages

**Test the API directly:**
```bash
python test_connection.py
```

**Restart after changes:**
The server auto-reloads when you modify the code.

## Features

✅ **Works immediately** - Mock data fallback  
✅ **GenAI Agent integration** - Real AI recommendations when configured  
✅ **Location-aware** - USDA hardiness zones and seasonal planting  
✅ **Native plant focus** - Environmentally friendly recommendations  
✅ **Interactive UI** - Select/deselect plants, view details  
✅ **Responsive design** - Works on desktop and mobile  
✅ **No Docker required** - Simple Python setup with uv

## Architecture

```
Smart Garden Planner
├── frontend/
│   └── index.html          # Static HTML frontend
├── backend/
│   ├── services/
│   │   └── requestinfo.py  # FastAPI app
│   └── .env               # Environment variables
├── run_api.sh             # Start script
└── serve_frontend.py      # Frontend server
```

The app uses a simple architecture with a FastAPI backend that integrates with your GenAI Agent API and a static HTML frontend. No complex build processes or Docker required!