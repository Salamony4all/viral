# 📐 VIRAL ENGINE - SYSTEM ARCHITECTURE

## 🏗️ Complete Project Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     VIRAL ENGINE SYSTEM                         │
│              (Zero-API, Local-First, 4-Agent AI)                │
└─────────────────────────────────────────────────────────────────┘

                              MAIN.PY
                           (Orchestrator)
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
        ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
        │ Load Trends  │  │Config/Utils  │  │Infrastructure│
        │    (JSON)    │  │   (Settings) │  │    Check     │
        └──────────────┘  └──────────────┘  └──────────────┘
                │
                ▼
        ┌────────────────────────────────────┐
        │   PHASE 1: AGENT ALPHA - Scraper   │
        │     (Trend Hunter)                 │
        ├────────────────────────────────────┤
        │ Tools:                             │
        │  • Playwright (web scraping)       │
        │  • BeautifulSoup (HTML parsing)    │
        │  • yt-dlp (video download)         │
        │                                    │
        │ Sources:                           │
        │  1. TikTok Creative Center         │
        │  2. YouTube Trending/Shorts        │
        │                                    │
        │ Output:                            │
        │  └─> current_trends.json           │
        │      • Rising hashtags             │
        │      • Hook patterns               │
        │      • SEO keywords                │
        │      • Niche breakouts             │
        └────────────────────────────────────┘
                │
                ▼
        ┌────────────────────────────────────┐
        │ PHASE 2: AGENT BETA - Scriptwriter │
        │   (Narrative Architect)            │
        ├────────────────────────────────────┤
        │ Tools:                             │
        │  • Ollama LLM (Mistral/Llama 3)    │
        │  • CrewAI (agent orchestration)    │
        │  • LangChain (LLM integration)     │
        │                                    │
        │ Processing:                        │
        │  1. Parse trends analysis          │
        │  2. Generate pattern interrupts    │
        │  3. Create 3-column script format  │
        │  4. Integrate SEO keywords         │
        │  5. Generate 2-3 variations        │
        │  6. Auto-generate captions         │
        │                                    │
        │ Output:                            │
        │  ├─> script_*.json                 │
        │  ├─> variations/                   │
        │  └─> captions.json                 │
        └────────────────────────────────────┘
                │
                ▼
        ┌────────────────────────────────────┐
        │  PHASE 3: AGENT GAMMA - Media Forge│
        │    (Content Generator)             │
        ├────────────────────────────────────┤
        │ Tools:                             │
        │  • ComfyUI (image/video gen)       │
        │  • Stable Diffusion/Flux           │
        │  • Coqui TTS (voiceover)           │
        │  • RVC (voice conversion)          │
        │  • FFmpeg (video assembly)         │
        │                                    │
        │ Processing:                        │
        │  1. Extract scene descriptions     │
        │  2. Generate visuals (ComfyUI)     │
        │  3. Generate voiceover (TTS)       │
        │  4. Assemble video (FFmpeg)        │
        │  5. Burn captions (yellow/bold)    │
        │  6. Output TikTok format           │
        │                                    │
        │ Output:                            │
        │  ├─> visual_*.png                  │
        │  ├─> voiceover_*.wav               │
        │  └─> final_render_with_captions.mp4│
        │      (1080x1920, 30 FPS)           │
        └────────────────────────────────────┘
                │
                ▼
        ┌────────────────────────────────────┐
        │  PHASE 4: AGENT DELTA - Monetizer  │
        │      (Profit Oracle)               │
        ├────────────────────────────────────┤
        │ Tools:                             │
        │  • Ollama LLM (context analysis)   │
        │  • Product APIs (affiliate nets)   │
        │  • Revenue calculation engine      │
        │                                    │
        │ Processing:                        │
        │  1. Analyze script context         │
        │  2. Search affiliate products      │
        │  3. Search TikTok Shop products    │
        │  4. Generate organic CTAs          │
        │  5. Calculate earnings potential   │
        │  6. Create comprehensive brief     │
        │                                    │
        │ Output:                            │
        │  ├─> PROFIT_BRIEF.md               │
        │  ├─> affiliate_products.json       │
        │  ├─> cta_strategies.json           │
        │  └─> earnings_projections.json     │
        └────────────────────────────────────┘
                │
                ▼
        ┌────────────────────────────────────┐
        │      👤 HUMAN VALIDATION           │
        │    (YOU REVIEW & APPROVE)          │
        ├────────────────────────────────────┤
        │ Review:                            │
        │  1. Watch final video              │
        │  2. Read profit brief              │
        │  3. Verify script quality          │
        │  4. Check affiliate links          │
        │                                    │
        │ Decision:                          │
        │  ✓ APPROVE → Continue              │
        │  ✗ REJECT  → Regenerate            │
        └────────────────────────────────────┘
                │
                ▼
        ┌────────────────────────────────────┐
        │    🎤 GREEN SCREEN HACK            │
        │  (Algorithm Metadata Reset)        │
        ├────────────────────────────────────┤
        │ Steps:                             │
        │  1. Record 3-sec native intro      │
        │  2. Apply Green Screen effect      │
        │  3. Use AI video as background     │
        │  4. This resets metadata           │
        │  5. Algorithm sees "human made"    │
        │                                    │
        │ Result: +2-5x organic reach! ✨   │
        └────────────────────────────────────┘
                │
                ▼
        ┌────────────────────────────────────┐
        │       📱 MANUAL POST                │
        │      (You Do This)                 │
        ├────────────────────────────────────┤
        │ Actions:                           │
        │  1. Post during peak hours         │
        │  2. Use suggested hashtags         │
        │  3. Pin CTA in comments            │
        │  4. Engage (first 60 min critical!)│
        │                                    │
        │ Result:                            │
        │  • Organic reach (no bot flags)    │
        │  • Higher engagement rate          │
        │  • Better monetization             │
        └────────────────────────────────────┘
```

---

## 📊 Data Flow Architecture

```
INPUT (You)
    ↓
    topic: "productivity hack"
    ↓
┌─────────────────────────────────────────────────────┐
│ TREND HUNTING (Agent Alpha)                         │
│ Process: Scrape → Analyze → Extract Keywords       │
│ Output: trends_manifest.json                        │
│  ├─ Hashtags: [{name, saves, likes, trend_status}] │
│  ├─ Formats: [{title, views, hook_pattern}]        │
│  ├─ Keywords: [keyword1, keyword2, ...]            │
│  └─ Niche breakouts: [{niche, growth_rate}]        │
└─────────────────────────────────────────────────────┘
    ↓
    trends_manifest.json
    ↓
┌─────────────────────────────────────────────────────┐
│ SCRIPT GENERATION (Agent Beta)                      │
│ Process: Analyze trends → Generate hooks → Write    │
│ Output: script_variants.json                        │
│  ├─ Main script                                     │
│  │  ├─ Script columns: [{time, visual, audio}]    │
│  │  ├─ Hook type: pattern_interrupt                │
│  │  └─ Keywords: [integrated into script]          │
│  ├─ Variations: [2-3 alternative scripts]          │
│  └─ Captions: [{time, text, style}]                │
└─────────────────────────────────────────────────────┘
    ↓
    script_variants.json
    ↓
┌─────────────────────────────────────────────────────┐
│ MEDIA GENERATION (Agent Gamma)                      │
│ Process: Generate visuals → Record audio → Assemble │
│ Output: final_render.mp4                            │
│  ├─ Visuals: ComfyUI generated B-roll             │
│  ├─ Audio: Coqui TTS voiceover                     │
│  ├─ Captions: Burned-in text overlays              │
│  └─ Format: 1080x1920 @ 30FPS (TikTok native)      │
└─────────────────────────────────────────────────────┘
    ↓
    final_render.mp4
    ↓
┌─────────────────────────────────────────────────────┐
│ MONETIZATION ANALYSIS (Agent Delta)                 │
│ Process: Analyze context → Search products → Brief  │
│ Output: PROFIT_BRIEF.md                             │
│  ├─ Affiliate products: [{name, link, commission}] │
│  ├─ TikTok Shop products: [{product, price, rate}] │
│  ├─ CTA strategies: [{text, placement, tone}]      │
│  └─ Earnings projection: $1500-60000+              │
└─────────────────────────────────────────────────────┘
    ↓
    PROFIT_BRIEF.md + final_render.mp4 + script
    ↓
┌─────────────────────────────────────────────────────┐
│ REVIEW FOLDER (/workspace/review/)                  │
│  ├─ final_render_with_captions.mp4                 │
│  ├─ script_20240115_143022.md                      │
│  ├─ PROFIT_BRIEF_20240115_143022.md                │
│  └─ ready_20240115_143022.json                     │
└─────────────────────────────────────────────────────┘
    ↓
OUTPUT (You)
    Post to TikTok!
```

---

## 🗂️ File Organization

```
viral_engine/
│
├── 📄 MAIN FILES (Start Here)
│   ├── main.py                    ← RUN THIS
│   ├── GETTING_STARTED.md         ← Read this first
│   ├── STARTUP_GUIDE.md           ← Setup instructions
│   └── README.md                  ← Full reference
│
├── 🤖 AGENTS (AI Brains)
│   ├── agents/
│   │   ├── agent_alpha.py         (Trend Hunter)
│   │   ├── agent_beta.py          (Narrative Architect)
│   │   ├── agent_gamma.py         (Media Forge)
│   │   ├── agent_delta.py         (Profit Oracle)
│   │   └── __init__.py
│   │
│   └── tools/                     (Utilities - expand later)
│       └── [placeholder for custom tools]
│
├── ⚙️ CONFIGURATION
│   └── config/
│       ├── settings.py            (Environment & paths)
│       ├── utils.py               (Logging, notifications)
│       └── __init__.py
│
├── 📁 WORKSPACE (Generated Content)
│   └── workspace/
│       ├── trends/                (Trend analysis JSON)
│       ├── assets/                (Scripts, audio, images)
│       ├── render/                (Video outputs)
│       └── review/                (Ready for human review)
│
├── 📝 CONFIGURATION FILES
│   ├── requirements.txt           (Python dependencies)
│   ├── .env.example              (Environment template)
│   ├── .env                       (Your config - git ignored)
│   └── .gitignore
│
├── 🐳 DOCKER
│   ├── docker-compose.yml         (All services)
│   └── Dockerfile                 (App container)
│
├── 📊 DOCUMENTATION
│   ├── PROJECT_SUMMARY.md         (Quick overview)
│   └── This file (ARCHITECTURE.md)
│
└── 📋 LOGS
    └── logs/
        └── viral_engine.log       (Execution details)
```

---

## 🔄 Execution Flow (Detailed)

### Flow Step 1: Initialization
```python
main.py
├── Load environment variables (.env)
├── Check directories exist
├── Setup logging
├── Verify infrastructure (Ollama, ComfyUI)
└── Initialize async runtime
```

### Flow Step 2: Trend Hunting
```python
Agent Alpha
├── Launch async Playwright
├── Navigate to TikTok Creative Center
├── Scrape rising hashtags
├── Extract engagement metrics
├── Scrape YouTube Shorts
├── Identify format gaps
├── Aggregate into manifest
└── Save: current_trends_*.json
```

### Flow Step 3: Script Generation
```python
Agent Beta
├── Load trends manifest
├── Extract SEO keywords
├── Select hook pattern
├── Build LLM prompt
├── Call Ollama (Mistral)
├── Parse response to 3-column format
├── Generate variations
├── Generate captions
└── Save: script_*.json + captions
```

### Flow Step 4: Media Generation
```python
Agent Gamma
├── Extract scene descriptions
├── Generate visuals (ComfyUI)
│  ├── Call ComfyUI API for each scene
│  ├── Queue image generation
│  └── Poll for completion
├── Generate voiceover (Coqui TTS)
│  ├── Initialize TTS model
│  ├── Generate audio for each line
│  └── Combine with timing
├── Assemble with FFmpeg
│  ├── Create video from images
│  ├── Mix audio
│  ├── Burn captions
│  └── Encode for TikTok
└── Output: final_render_with_captions.mp4
```

### Flow Step 5: Monetization
```python
Agent Delta
├── Analyze script context (LLM)
├── Search affiliate products
├── Search TikTok Shop
├── Generate CTA strategies
├── Calculate earnings
├── Create comprehensive brief
└── Save: PROFIT_BRIEF.md
```

### Flow Step 6: Notification
```python
notify_review_ready()
├── Create review status file
├── Log message
├── Send Telegram (optional)
└── Display actionable next steps
```

---

## 🔧 Service Architecture

### Local Services Required

```
┌─────────────────────────────────────────────────────┐
│ SERVICE INFRASTRUCTURE                              │
└─────────────────────────────────────────────────────┘

1. OLLAMA (LLM Server)
   ├─ Port: 11434
   ├─ Models: Mistral, Llama 2, Neural Chat
   ├─ Used by: Agent Beta (script generation)
   └─ Docker: ollama service

2. COMFYUI (Image/Video Generation)
   ├─ Port: 8188
   ├─ WS Port: 8188/ws (WebSocket)
   ├─ Models: Stable Diffusion, Flux
   ├─ Used by: Agent Gamma (visuals)
   └─ Docker: comfyui service

3. FFMPEG (Media Processing)
   ├─ CLI tool (not a service)
   ├─ Used by: Agent Gamma (assembly)
   └─ Local installation required

4. POSTGRESQL (Optional - Analytics)
   ├─ Port: 5432
   ├─ Purpose: Content tracking, analytics
   └─ Docker: postgres service

5. REDIS (Optional - Caching)
   ├─ Port: 6379
   ├─ Purpose: Cache, task queue
   └─ Docker: redis service
```

### Docker Compose Services

```yaml
Services Defined:
├─ ollama          # LLM inference
├─ comfyui         # Image generation
├─ postgres        # Database
├─ redis           # Cache
└─ viral-engine-app # Main app
```

---

## 📈 Scalability Architecture

### Horizontal Scaling (Multiple Videos)

```
Single Run: 1 video per 12 minutes
├─ Topic 1 → Video 1 (12 min)
├─ Topic 2 → Video 2 (12 min)
└─ Topic 3 → Video 3 (12 min)
  Total: 3 videos in ~40 minutes

Daily Target: 5 videos/day
├─ Morning batch: 2 videos
├─ Afternoon batch: 2 videos
└─ Evening: 1 video
  Time: 60 minutes total
```

### Quality vs Speed Trade-offs

```
Faster (5 min):
├─ Use neural-chat (smaller model)
├─ Skip image generation
├─ Single script variation
└─ Lower quality ⬇️

Balanced (12 min):
├─ Use mistral (recommended)
├─ Generate visuals
├─ 2 script variations
└─ Professional quality ✓

Quality (20+ min):
├─ Use llama2 (larger model)
├─ ComfyUI with multiple passes
├─ 3+ script variations
└─ Premium quality ⬆️
```

---

## 🔐 Security Architecture

### Data Protection

```
Sensitive Data:
├─ .env file          ← NOT in git (use .env.example)
├─ API keys          ← Environment variables only
├─ Generated content ← Stored locally, not uploaded
└─ Logs              ← Masked sensitive info

Privacy:
├─ No data sent to third parties
├─ All processing local
├─ No account login needed
└─ No tracking/telemetry
```

### Access Control

```
Public files:
├─ Source code (agents, config, main.py)
├─ Documentation (README, STARTUP_GUIDE)
└─ Configuration templates (.env.example)

Private/Generated:
├─ .env (environment variables)
├─ workspace/ (generated content)
├─ logs/ (execution logs)
└─ Git ignored files
```

---

## 📊 Performance Characteristics

### Typical Execution Times

```
Phase 1 (Trend Hunting):     2-3 minutes
Phase 2 (Script Gen):         3-5 minutes
Phase 3 (Media Forge):        4-6 minutes
Phase 4 (Monetization):       1-2 minutes
Review & Notification:        <1 minute
─────────────────────────────────────────
TOTAL:                        11-17 minutes
```

### Resource Requirements

```
CPU:
├─ Min: Dual-core
├─ Recommended: 4+ cores
└─ Optimal: 8+ cores

RAM:
├─ Min: 8 GB
├─ Recommended: 16 GB
└─ Optimal: 32 GB (for larger models)

Disk:
├─ Code: 500 MB
├─ Models: 5-20 GB (Ollama, ComfyUI)
├─ Per video: 200-500 MB
└─ Recommended: 100 GB free
```

---

## 🎯 Next Steps to Explore

1. **Read Documentation**
   - GETTING_STARTED.md (2 min)
   - STARTUP_GUIDE.md (15 min)
   - README.md (30 min reference)

2. **Setup System**
   - Install dependencies
   - Start Ollama
   - Run first video

3. **Customize**
   - Edit agent configurations
   - Add custom hooks
   - Optimize for your niche

4. **Scale**
   - Generate multiple videos
   - A/B test variations
   - Build to 5+/week

5. **Integrate**
   - Add custom tools
   - Connect to databases
   - Build web dashboard

---

**Architecture Complete! Time to generate viral content! 🚀**
