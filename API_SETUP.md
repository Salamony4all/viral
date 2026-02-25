# 🔌 Backend API Setup

## Overview

The backend is a **FastAPI** server that bridges the React frontend with the Python agents.

## What It Does

1. **Receives requests** from the React frontend
2. **Orchestrates agents** (Alpha, Beta, Gamma, Delta)
3. **Manages the generation pipeline**
4. **Returns results** in JSON format

## Installation

### 1. Install FastAPI

The API server is already set up. Just ensure dependencies are installed:

```bash
cd viral_engine

# Install if not already done
pip install -r requirements.txt

# Or just install FastAPI:
pip install fastapi uvicorn
```

### 2. Start the Backend Server

```bash
python api.py
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Press CTRL+C to quit
```

### 3. Verify It's Working

In a browser or terminal:
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "ok",
  "timestamp": "2026-01-14T16:30:00.000000"
}
```

## API Endpoints

### 1. Health Check
```
GET /health
```
Check if the API is running.

### 2. Generate Campaign
```
POST /generate
Content-Type: application/json

{
  "topic": "productivity hack",
  "auto_post": false
}
```

Starts a complete viral video generation:
- Agent Alpha: Finds trending angles
- Agent Beta: Writes script
- Agent Gamma: Creates media
- Agent Delta: Plans monetization

### 3. Brainstorm with Agent
```
POST /brainstorm
Content-Type: application/json

{
  "agent": "Agent Beta",
  "prompt": "How can I make this hook more viral?"
}
```

Chat with individual agents for ideas.

### 4. Get Status
```
GET /status
```

Check progress of current generation.

### 5. Get Recent Results
```
GET /results
```

Retrieve previous generations from `/workspace/review/`.

## Environment Variables

The API uses `.env` configuration:

```env
# Ollama (Local LLM)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# ComfyUI (Image Generation)
COMFYUI_BASE_URL=http://localhost:8188

# Workspace paths
WORKSPACE_DIR=./workspace
```

## Running Both Frontend & Backend

### Terminal 1: Backend API
```bash
cd viral_engine
python api.py
# Runs on http://localhost:8000
```

### Terminal 2: Frontend (React)
```bash
cd viral_engine/frontend
npm install
npm run dev
# Runs on http://localhost:3000
```

### Terminal 3: Ollama (if not already running)
```bash
ollama serve
# Runs on http://localhost:11434
```

---

**Now open http://localhost:3000 in your browser!**

## Troubleshooting

### ModuleNotFoundError
```bash
pip install -r requirements.txt
```

### Port 8000 already in use
```bash
# Use a different port
python -c "import uvicorn; from api import app; uvicorn.run(app, host='127.0.0.1', port=8001)"
```

### CORS errors in frontend
- Make sure `api.py` has CORS middleware enabled ✅ (it does)
- Verify frontend is accessing `http://localhost:8000/api`

### Ollama not found
- Make sure `ollama serve` is running
- Check ollama is at `localhost:11434`

## Full Integration Checklist

- [ ] Ollama running (`ollama serve`)
- [ ] Backend API running (`python api.py`)
- [ ] Frontend running (`npm run dev`)
- [ ] Browser opens http://localhost:3000
- [ ] Health check passes: `curl http://localhost:8000/health`
- [ ] Frontend connects to API
- [ ] Enter topic and generate!

## Next Steps

1. Start the backend: `python api.py`
2. Start the frontend: `npm run dev`
3. Open http://localhost:3000
4. Generate your first viral video!
