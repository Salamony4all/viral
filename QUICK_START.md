# 🎯 QUICK REFERENCE - VIRAL ENGINE FRONTEND

## 🚀 Start the Entire System (1 Command)

### Windows
```batch
cd c:\Users\Mohamad60025\Desktop\App\TIK\viral_engine
start_windows.bat
```

### Mac/Linux
```bash
cd ~/Desktop/App/TIK/viral_engine
chmod +x start_unix.sh && ./start_unix.sh
```

---

## 🔧 Manual Startup (3 Terminals)

### Terminal 1: Start Ollama LLM
```powershell
ollama serve
# Output: Listening on 127.0.0.1:11434
```

### Terminal 2: Start Backend API
```bash
cd viral_engine
python api.py
# Output: Uvicorn running on http://127.0.0.1:8000
```

### Terminal 3: Start React Frontend
```bash
cd viral_engine/frontend
npm install  # First time only
npm run dev
# Output: ➜ Local: http://localhost:3000
```

---

## 🌐 Access the Dashboard

**URL**: `http://localhost:3000`

**You should see**:
1. Purple gradient header with "Viral Engine Dashboard"
2. Topic input field
3. "Generate Campaign" button
4. 4 agent cards below

---

## 💡 How to Use

### Generate Content
1. Enter a topic: `"productivity hack for students"`
2. Click `[Generate Campaign]`
3. Wait for all 4 agents to finish (~5-10 min)

### View Results
- **🎬 Video Tab**: Watch generated TikTok
- **📝 Script Tab**: Read script + variations
- **💰 Monetization Tab**: See earnings & products
- **💭 Chat Tab**: Brainstorm with Agent Beta

### Brainstorm Improvements
1. Click the **Chat Tab**
2. Type a question: `"How can I make the hook catchier?"`
3. Agent Beta responds with suggestions

---

## 📁 Important Files

### Frontend
```
viral_engine/frontend/
├── src/
│   ├── components/ChatBox.tsx      ← Chat interface
│   ├── components/VideoPreview.tsx ← Video player
│   ├── components/ScriptDisplay.tsx ← Script viewer
│   ├── pages/Dashboard.tsx         ← Main page
│   └── services/agentService.ts    ← API calls
├── package.json                    ← Dependencies
└── README.md                       ← Frontend docs
```

### Backend
```
viral_engine/
├── api.py                          ← FastAPI server
├── frontend/                       ← React app
├── agents/                         ← AI agents
├── FULL_STARTUP.md                 ← Setup guide
├── FRONTEND_SETUP.md               ← Frontend docs
└── API_SETUP.md                    ← Backend docs
```

---

## 🔌 API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Generate Campaign
```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "productivity hack"}'
```

### Brainstorm
```bash
curl -X POST http://localhost:8000/api/brainstorm \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "Agent Beta",
    "prompt": "Make this hook more viral"
  }'
```

### Check Status
```bash
curl http://localhost:8000/api/status
```

---

## 🐛 Troubleshooting Quick Fixes

### "Cannot connect to API"
```bash
# Make sure all 3 terminals are running:
ollama serve        # Terminal 1
python api.py       # Terminal 2
npm run dev         # Terminal 3
```

### "Port 8000 already in use"
```bash
# Use a different port
python -c "import uvicorn; from api import app; uvicorn.run(app, port=8001)"
```

### "npm: command not found"
```bash
# Install Node.js from nodejs.org
# Then verify:
node --version
npm --version
```

### "ollama: command not found"
```bash
# Install from https://ollama.ai
# Download and run the installer
# Then restart your terminal
```

### "Module not found" errors
```bash
cd viral_engine/frontend
npm install
```

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────┐
│         Browser (Port 3000)                │
│  React Dashboard + Components              │
└─────────────┬───────────────────────────────┘
              │ HTTP
              ↓
┌─────────────────────────────────────────────┐
│      FastAPI Backend (Port 8000)            │
│  Orchestrates 4 Agents                      │
└──────┬─────────────────┬──────────────────┬─┘
       ↓                 ↓                  ↓
   Ollama         ComfyUI            FFmpeg
  (Port 11434)    (Port 8188)        (Built-in)
   LLM Models    Image Generation    Video Assembly
```

---

## 🎯 Component Quick Guide

### ChatBox
- **Purpose**: Chat with AI agents
- **Features**: Message history, agent selection, real-time response
- **Used in**: Chat tab of dashboard

### VideoPreview
- **Purpose**: Display generated video
- **Features**: 9:16 TikTok aspect ratio, play/pause controls
- **Used in**: Video tab of dashboard

### ScriptDisplay
- **Purpose**: Show viral script
- **Features**: Main script, variations, captions
- **Used in**: Script tab of dashboard

### MonetizationBrief
- **Purpose**: Show earnings strategy
- **Features**: Earnings range, products, affiliate links
- **Used in**: Monetization tab of dashboard

### Dashboard
- **Purpose**: Main orchestrator
- **Features**: Input, tabbed results, empty state
- **Used in**: Main page (http://localhost:3000)

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| [FULL_STARTUP.md](FULL_STARTUP.md) | Complete setup guide |
| [FRONTEND_SETUP.md](FRONTEND_SETUP.md) | React development |
| [API_SETUP.md](API_SETUP.md) | Backend configuration |
| [frontend/README.md](frontend/README.md) | React app reference |
| [FRONTEND_BUILD_COMPLETE.md](FRONTEND_BUILD_COMPLETE.md) | Build summary |

---

## 🔑 Environment Variables

Create `frontend/.env`:
```env
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_ENV=development
```

Create `viral_engine/.env`:
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
COMFYUI_BASE_URL=http://localhost:8188
```

---

## 💾 Output Locations

Generated content saved to:
```
viral_engine/
├── workspace/
│   ├── review/           ← Final outputs
│   │   ├── script.md
│   │   ├── PROFIT_BRIEF.md
│   │   └── final_render_with_captions.mp4
│   ├── assets/           ← Images/audio
│   ├── render/           ← Video renders
│   └── trends/           ← Trend analysis
```

---

## ⚡ Performance Tips

1. **First generation slower**: Models loading into memory
2. **Use CPU mode**: Faster on machines without NVIDIA GPU
3. **Reduce video length**: In `config/settings.py` → `CONTENT_LENGTH_SECONDS`
4. **Close other apps**: Free up RAM for agent processing

---

## 🎬 Example Workflow

```
1. Start system
   → 3 terminals running
   → Browser at localhost:3000

2. Enter topic
   → "Morning routine productivity hack"
   → Click "Generate"

3. Wait for agents
   → Agent Alpha finds trends (~2 min)
   → Agent Beta writes script (~3 min)
   → Agent Gamma creates video (~4 min)
   → Agent Delta plans monetization (~1 min)

4. Review results
   → Watch video (Video tab)
   → Read script (Script tab)
   → Check earnings (Monetization tab)
   → Chat for ideas (Chat tab)

5. Download & post
   → Save video from workspace/review/
   → Post to TikTok/Instagram

6. Generate next
   → Enter new topic
   → Repeat!
```

---

## ✅ Success Indicators

- ✅ All 3 terminals showing "running/listening"
- ✅ Dashboard loads at localhost:3000
- ✅ Topic input field visible
- ✅ Can enter text
- ✅ "Generate Campaign" button clickable
- ✅ After generation: Results appear in tabs
- ✅ Chat tab: Can type messages

---

## 🆘 Get Help

1. **Check logs**: Look at terminal output for errors
2. **Read docs**: FULL_STARTUP.md has detailed troubleshooting
3. **Verify setup**: Run health check with curl
4. **Restart**: Stop all terminals and start fresh

---

## 🎉 You're All Set!

Your Viral Engine dashboard is ready to create viral content!

**Next Step**: Open http://localhost:3000 and generate your first video! 🚀
