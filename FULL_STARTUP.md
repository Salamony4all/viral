# 🚀 VIRAL ENGINE - COMPLETE STARTUP GUIDE

## Overview

The Viral Engine is a **complete system** with:
- ✅ **Backend**: Python agents (Alpha, Beta, Gamma, Delta)
- ✅ **Frontend**: React dashboard with chat interface
- ✅ **Infrastructure**: Ollama (LLM), ComfyUI (images), FFmpeg (video)

This guide walks you through starting everything.

---

## ⚡ 5-Minute Quick Start

### Windows Users
1. Open PowerShell in the `viral_engine` folder
2. Run: `.\start_windows.bat`
3. Open: `http://localhost:3000`

### Mac/Linux Users
1. Open terminal in the `viral_engine` folder
2. Run: `chmod +x start_unix.sh && ./start_unix.sh`
3. Open: `http://localhost:3000`

**That's it!** All services start automatically.

---

## 📋 Step-by-Step Manual Setup

### Step 1: Start Ollama (Local LLM)

Ollama is the **brain** of the system. It powers Agent Beta (script generation).

**Terminal 1:**
```powershell
ollama serve
```

You should see:
```
Listening on 127.0.0.1:11434
```

**Verify it's working:**
```powershell
ollama list
```

Should show `mistral` model.

---

### Step 2: Start Backend API

The FastAPI backend bridges the frontend and agents.

**Terminal 2:**
```bash
cd viral_engine
python api.py
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Test the API:**
```bash
curl http://localhost:8000/health
```

Response:
```json
{"status": "ok", "timestamp": "..."}
```

---

### Step 3: Start Frontend

The React dashboard is where you interact with the system.

**Terminal 3:**
```bash
cd viral_engine/frontend
npm install
npm run dev
```

You should see:
```
  ➜  Local:   http://localhost:3000/
```

**Automatically opens** `http://localhost:3000`

---

### Step 4: Verify Everything

Your terminal layout should look like:

```
Terminal 1 (Ollama)        Terminal 2 (Backend)    Terminal 3 (Frontend)
┌─────────────────────┐   ┌──────────────────┐   ┌────────────────────┐
│ ollama serve        │   │ python api.py    │   │ npm run dev        │
│ Listening 11434     │   │ Running 8000     │   │ Running 3000       │
└─────────────────────┘   └──────────────────┘   └────────────────────┘
```

All three should show "running" or "listening" messages.

---

## 🌐 Access the Dashboard

1. **Open in browser:** `http://localhost:3000`
2. **You should see:**
   - Purple "Viral Engine Dashboard" header
   - Topic input field
   - 4 agent cards (Alpha, Beta, Gamma, Delta)
3. **Test it:**
   - Enter topic: "productivity hack"
   - Click "Generate Campaign"
   - Watch the magic happen!

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                       │
│              (http://localhost:3000)                    │
│                                                         │
│  Dashboard → ChatBox → VideoPreview → Monetization    │
└────────────────────────┬────────────────────────────────┘
                         │
                    HTTP Requests
                         │
┌────────────────────────▼────────────────────────────────┐
│                  FastAPI Backend                        │
│              (http://localhost:8000)                    │
│                                                         │
│  /generate → /brainstorm → /status → /results         │
└────────────┬────────────┬────────────┬────────────────┘
             │            │            │
      ┌──────▼──┐  ┌──────▼──┐  ┌──────▼──────┐
      │ Ollama  │  │ ComfyUI │  │ FFmpeg     │
      │ (11434) │  │ (8188)  │  │ (builtin)  │
      └─────────┘  └─────────┘  └────────────┘
```

---

## 🔧 Troubleshooting

### Problem: "Ollama not found"
**Solution**: Ollama wasn't installed properly
```bash
# Download from: https://ollama.ai
# Run the installer
# Then restart PowerShell and run: ollama serve
```

### Problem: "Port 8000 already in use"
**Solution**: Another app is using port 8000
```bash
# Use different port
python -c "import uvicorn; from api import app; uvicorn.run(app, host='127.0.0.1', port=8001)"
```

### Problem: "Cannot connect to API" (frontend shows error)
**Solution**: Backend not running
```bash
# Make sure Terminal 2 is running: python api.py
# And Terminal 1 has ollama serve running
```

### Problem: "CORS error"
**Solution**: Likely a configuration issue
- Frontend should be at `http://localhost:3000`
- Backend should be at `http://localhost:8000`
- Both are already configured correctly

### Problem: "Cannot find module" (npm error)
**Solution**: Dependencies not installed
```bash
cd viral_engine/frontend
npm install
```

---

## 📊 Dashboard Guide

### Input Section
```
Topic: [Enter your idea here]  [Generate Campaign]
```

**Examples**:
- "Morning routine productivity"
- "Study tips for college"
- "Fitness motivation hack"
- "5-minute recipe"

### Results Tabs

**🎬 Video Tab**
- Watch generated video
- TikTok 9:16 format
- Ready to post

**📝 Script Tab**
- View the script
- See variations (A/B testing)
- Read auto-captions

**💰 Monetization Tab**
- Earnings projection: $X - $Y
- Affiliate products
- Revenue per product

**💭 Brainstorm Tab**
- Chat with Agent Beta
- Get suggestions
- Refine content

---

## 🎯 Full Workflow

### 1. Generate Initial Content
```
User enters topic → All 4 agents run → Results appear
```

### 2. Review Results
```
Video → Script → Monetization strategy → Chat
```

### 3. Brainstorm Improvements
```
Use chat box → Ask Agent Beta → Get suggestions
```

### 4. Refine & Regenerate
```
Modify topic → Generate again → Compare results
```

### 5. Download & Post
```
Save video → Download → Post to TikTok/Instagram
```

---

## 📁 Key Folders

- `agents/` - Agent implementations
- `config/` - Configuration files
- `workspace/` - Generated content
  - `workspace/review/` - Final outputs
  - `workspace/assets/` - Images, audio
  - `workspace/render/` - Video renders
- `frontend/` - React app
- `api.py` - Backend server

---

## 🚀 Next Steps

1. **Start all three terminals** (Ollama, Backend, Frontend)
2. **Open http://localhost:3000**
3. **Enter a topic** (e.g., "productivity hack")
4. **Click "Generate Campaign"**
5. **Watch all 4 agents work:**
   - Alpha: Finds trends
   - Beta: Writes script
   - Gamma: Creates video
   - Delta: Plans monetization
6. **Review results** in the dashboard
7. **Download & post!**

---

## 📚 Additional Resources

- [FRONTEND_SETUP.md](FRONTEND_SETUP.md) - React setup details
- [API_SETUP.md](API_SETUP.md) - Backend configuration
- [OLLAMA_INSTALLATION.md](OLLAMA_INSTALLATION.md) - LLM setup
- [README.md](README.md) - Project overview

---

## ⚙️ System Requirements

- **Python 3.11+** (Backend)
- **Node.js 18+** (Frontend)
- **8+ GB RAM** (Recommended)
- **Ollama** (Local LLM)
- **Windows/Mac/Linux**

---

## 💬 Common Questions

**Q: Do I need Internet?**
A: No! Everything runs locally. Totally private.

**Q: Can I close one terminal?**
A: No. All three need to stay running:
- Ollama (Port 11434)
- Backend (Port 8000)
- Frontend (Port 3000)

**Q: How long does generation take?**
A: ~5-10 minutes depending on your hardware.

**Q: Can I generate multiple videos?**
A: Yes! Just enter different topics.

**Q: Where are the videos saved?**
A: In `workspace/review/` folder.

---

## 🎉 Success Indicators

✅ All three terminals showing "running/listening"
✅ Dashboard opens at http://localhost:3000
✅ Topic input field appears
✅ Can enter text and click "Generate"
✅ Results appear in tabs after generation

---

**You're ready to create viral content! 🎬**

Need help? Check the documentation or troubleshooting guide above.
