# 🚀 VIRAL ENGINE - STARTUP GUIDE

## Quick Start (5 minutes)

### Step 1: Install Dependencies

```bash
# Navigate to project
cd c:\Users\Mohamad60025\Desktop\App\TIK\viral_engine

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install all packages
pip install -r requirements.txt
```

### Step 2: Start Ollama LLM

**Option A: Direct Installation**
```bash
# Download Ollama from https://ollama.ai
# After installation, run:
ollama serve

# In another terminal, pull model:
ollama pull mistral
```

**Option B: Docker (Recommended)**
```bash
# From viral_engine directory:
docker-compose up -d ollama

# Wait for health check to pass
docker-compose logs ollama

# Pull model (one-time)
docker-compose exec ollama ollama pull mistral
```

### Step 3: Configure Environment

```bash
# Copy template to .env
cp .env.example .env

# Edit .env with your values (most defaults are fine)
# Key settings:
# - OLLAMA_MODEL=mistral
# - MONETIZATION_FOCUS=hybrid
# - TELEGRAM_BOT_TOKEN= (optional, for notifications)
```

### Step 4: Run the Engine

```bash
# Basic usage
python main.py "productivity hack"

# Watch the magic happen!
# Output goes to: /workspace/review/
```

---

## 📋 Complete Setup Guide

### For Windows Users

#### Prerequisites Check
```powershell
# Check Python
python --version  # Should be 3.11+

# Check Git
git --version

# Install Chocolatey if needed:
# https://chocolatey.org/install

# Install FFmpeg (needed for video assembly)
choco install ffmpeg

# Verify FFmpeg
ffmpeg -version
```

#### Local Setup (No Docker)
```powershell
# Navigate to project
cd c:\Users\Mohamad60025\Desktop\App\TIK\viral_engine

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download Ollama
# Visit: https://ollama.ai
# Run installer and follow steps

# In one PowerShell window, start Ollama
ollama serve

# In another window, pull model
ollama pull mistral

# Test Ollama is working
curl http://localhost:11434/api/tags

# In third window, run engine
python main.py "weight loss tips"
```

#### Docker Setup (Recommended)
```powershell
# Install Docker Desktop
# https://www.docker.com/products/docker-desktop

# Navigate to project
cd c:\Users\Mohamad60025\Desktop\App\TIK\viral_engine

# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Check services are running
docker-compose ps

# Initialize Ollama model (run once)
docker-compose exec ollama ollama pull mistral

# Run engine
python main.py "your topic here"

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### For Mac Users

```bash
# Install Homebrew if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11+
brew install python@3.11

# Install FFmpeg
brew install ffmpeg

# Install Docker Desktop
brew install --cask docker

# Follow same Docker setup as Windows above
```

### For Linux Users

```bash
# Install Python
sudo apt update
sudo apt install python3.11 python3.11-venv

# Install FFmpeg
sudo apt install ffmpeg

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Follow same Docker setup as Windows above
```

---

## 🔍 Service Health Checks

### Verify Ollama is Running

```bash
# Should return list of available models
curl http://localhost:11434/api/tags

# Should return "Ollama is running"
curl http://localhost:11434/
```

### Verify ComfyUI (if using)

```bash
# Should return API info
curl http://localhost:8188/api/

# Check WebSocket connection
# ws://localhost:8188/ws should be accessible
```

### Verify FFmpeg

```bash
# Should show version info
ffmpeg -version

# Quick test: create silent video
ffmpeg -f lavfi -i color=c=black:s=1080x1920:d=1 -f lavfi -i anullsrc=r=44100:cl=mono -c:v libx264 -c:a aac -t 1 test.mp4
```

---

## 🎬 Running Your First Viral Campaign

### Example 1: Productivity Hacks

```bash
python main.py "5 productivity hacks that save 3 hours"
```

Expected output:
```
PHASE 2: TREND HUNTING 🔥
  ✓ Rising hashtags found: 5
  ✓ YouTube formats analyzed: 4
  
PHASE 3: NARRATIVE ARCHITECTURE 📝
  ✓ Main script generated: 8 scenes
  ✓ Script variations: 2
  
PHASE 4: MEDIA FORGE 🎬
  ✓ Visuals generated: 8 scenes
  ✓ Voiceover created
  ✓ Final video: final_render.mp4
  
PHASE 5: PROFIT ORACLE 💰
  ✓ Affiliate products found: 5
  ✓ Profit Brief: PROFIT_BRIEF.md
```

### Example 2: Weight Loss Transformation

```bash
python main.py "beginner weight loss transformation 30 days"
```

### Example 3: Making Money Online

```bash
python main.py "passive income ideas 2024"
```

---

## 📂 Understanding the Output

### After Running the Engine

Check `/workspace/review/` folder:

```
/workspace/
├── trends/
│   └── current_trends_20240115_143022.json    # Trend data
├── assets/
│   ├── script_20240115_143022.md              # Script breakdown
│   ├── PROFIT_BRIEF_20240115_143022.md        # Monetization guide
│   ├── voiceover_20240115_143022.wav          # Generated audio
│   └── visual_000.png, visual_001.png, etc.   # Generated images
├── render/
│   ├── final_render.mp4                       # Base video
│   └── final_render_with_captions.mp4         # With captions
└── review/
    └── ready_20240115_143022.json             # Status notification
```

### Key Files Explained

1. **current_trends.json** - Trend analysis from TikTok & YouTube
   - Rising hashtags with engagement metrics
   - Hook patterns that work
   - Niche breakout opportunities
   - SEO keywords for TikTok Search

2. **script_*.md** - Your generated script
   - 3-column format: Time | Visual | Audio
   - Hook pattern used
   - SEO keywords integrated
   - Camera cues and transitions

3. **PROFIT_BRIEF.md** - Your monetization playbook
   - Affiliate product recommendations (with links!)
   - TikTok Shop product suggestions
   - CTA strategies that feel organic
   - Earnings projections
   - Action checklist

4. **final_render_with_captions.mp4** - Ready-to-post video
   - 1080x1920 (TikTok native)
   - Yellow captions burnt-in
   - High-quality audio
   - 30 seconds (customizable)

---

## 💡 Next Steps (How to Post for Maximum Reach)

### The "Green Screen Hack" Posting Strategy

1. **Review the Content** (5 min)
   - Watch video quality
   - Read profit brief
   - Verify affiliate links work

2. **Record Native Intro** (3-5 min)
   - Open TikTok on your phone
   - Tap "Create" → "Record"
   - **IMPORTANT**: Use the NATIVE camera, NOT effects yet
   - Record 3-second intro: "Wait, you need to see this..."
   - Keep it authentic, no edits

3. **Apply Green Screen Effect** (2 min)
   - In TikTok editor after recording intro
   - Effects → Search "Green Screen"
   - Apply Green Screen effect
   - Select our generated video as background
   - Adjust positioning so your face + video both visible

4. **Add Captions & CTAs** (3 min)
   - Caption: Hook from profit brief
   - Example: "Save this productivity hack →"
   - Add hashtags: #FYP #viral #productivity
   - Add music: Pick trending sound from trends manifest

5. **Post & Engage** (ongoing)
   - Post during peak hours (6-10 PM)
   - Spend 30 min engaging with comments (CRITICAL)
   - Reply to first 20 comments
   - Respond to DMs
   - Repost to Stories if eligible

### Example Caption + Hashtags

```
🚀 Productivity hack that saves 3 hours per day (most people don't know this)

Save this 👇 (link in comment)

#FYP #viral #productivity #entrepreneur #timemanagement #moneytips #sidehustle
```

### Example Pinned Comment (Monetization)

```
🔗 The exact tool I use: [AFFILIATE LINK]
💬 Questions? Ask in replies!
📌 Save this for later
```

---

## 🛠️ Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'crewai'"

**Solution**: Install missing packages
```bash
pip install -r requirements.txt --upgrade
```

### Problem: "Ollama connection refused"

**Solution**: Start Ollama service
```bash
# Windows: Run Ollama from Start Menu
# Or: ollama serve

# Docker:
docker-compose up -d ollama
docker-compose exec ollama ollama pull mistral
```

### Problem: "FFmpeg not found"

**Solution**: Install FFmpeg
```bash
# Windows
choco install ffmpeg

# Mac
brew install ffmpeg

# Linux
sudo apt install ffmpeg
```

### Problem: Out of memory errors

**Solution**: Use smaller LLM model
```bash
# Edit .env
OLLAMA_MODEL=neural-chat  # Smaller than mistral
```

### Problem: Very slow script generation

**Solution**: Check LLM model size
```bash
# See available models
ollama list

# Use smaller models if needed
ollama pull neural-chat
```

### Problem: "ComfyUI not responding"

**Solution**: Disable image generation (use placeholders)
```bash
# Edit agent_gamma.py:
# Comment out: visuals = await forge.generate_visuals(...)
# Use: visuals = []  # Skip visual generation
```

---

## 📊 Performance Tips

### To Speed Up Generation

1. **Use smaller LLM model**
   - `neural-chat` or `orca-mini` instead of `mistral`
   - Set: `OLLAMA_MODEL=neural-chat`

2. **Disable image generation**
   - Keep script/audio only
   - Skip ComfyUI processing

3. **Reduce script variations**
   - Change: `architect.generate_variations(script, num_variations=1)`
   - Reduces processing by 50%

4. **Use SSD for workspace**
   - FFmpeg is disk-intensive
   - SSD makes 3-5x faster

### To Improve Quality

1. **Use larger LLM model**
   - `llama2` or `mistral` for better scripts
   - Takes 2-3x longer but worth it

2. **Generate more variations**
   - Test 5 scripts, pick the best
   - A/B test on actual TikTok

3. **Use GPU acceleration**
   - GPU speeds up Ollama by 10-50x
   - Requires NVIDIA CUDA or AMD ROCm
   - Set in docker-compose.yml

4. **Higher video bitrate**
   - Set: `AUDIO_BITRATE=320k` in .env
   - Better quality, larger file

---

## 🎯 Success Metrics

### Track These Numbers

1. **Video Quality Score** (subjective, 1-10)
   - Hook effectiveness
   - Visual appeal
   - Audio clarity

2. **Monetization Score**
   - Number of affiliate products identified
   - Conversion likelihood ratings
   - Earnings potential

3. **Content Score**
   - Script originality
   - Hook effectiveness
   - SEO keyword integration

### Target Benchmarks

```
Week 1: 1 video/day
  - Learn what works
  - Refine posting strategy
  - A/B test hooks

Week 2-4: 3-4 videos/week
  - Maintain quality
  - Engage with audience
  - Optimize CTAs

Month 2+: Scale to multiple topics
  - Target: $500-2000/month
  - Viral videos worth $5000-50000 each
```

---

## 🆘 Getting Help

### Check Logs

```bash
# Real-time logs
tail -f logs/viral_engine.log

# Search for errors
grep "ERROR" logs/viral_engine.log

# Or from Docker
docker-compose logs viral-engine-app
```

### Test Individual Agents

```python
# Test Trend Hunter
python -c "import asyncio; from agents.agent_alpha import run_trend_hunter; asyncio.run(run_trend_hunter())"

# Test Script generation
python -c "import asyncio; from agents.agent_beta import run_narrative_architect; asyncio.run(run_narrative_architect({}, 'test'))"
```

---

## ✅ Verification Checklist

Before running main.py:

- [ ] Python 3.11+ installed
- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] .env file configured
- [ ] FFmpeg installed: `ffmpeg -version`
- [ ] Ollama running: `curl http://localhost:11434/api/tags`
- [ ] Ollama model available: `ollama list` (should show mistral)
- [ ] Workspace directories exist
- [ ] Sufficient disk space (5GB+ recommended)
- [ ] 8GB+ RAM available

---

## 🎉 You're Ready!

Run your first campaign:

```bash
python main.py "your awesome topic here"
```

Then follow the output instructions to post for maximum organic reach!

Good luck! 🚀💰
