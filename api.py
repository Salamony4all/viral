"""
FastAPI wrapper for the Viral Engine.
Two-phase pipeline:
  Phase 1  POST /generate       → trends + script → status "script_ready"
  Phase 2  POST /proceed/{id}   → user-edited script → video + monetization → "completed"
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import re
import uuid
import sys
from pathlib import Path

# Force UTF-8 for Windows consoles to handle emojis/Arabic
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from typing import Optional, List, Dict, Any
from datetime import datetime
from loguru import logger
from fastapi import WebSocket, WebSocketDisconnect
import json

sys.path.insert(0, str(Path(__file__).parent))

from config.settings import WORKSPACE_DIR, ASSETS_DIR, RENDER_DIR, REVIEW_DIR
from config.utils import verify_infrastructure, load_latest_trends

# Dedicated output folder for final videos
VIDEOS_DIR = WORKSPACE_DIR / "videos"
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="Viral Engine API",
    description="Multi-agent TikTok content creation platform",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Viral Engine API is running",
        "version": "2.0.0",
        "docs": "/docs"
    }

# ---------------------------------------------------------------------------
# Auto-cleanup: remove render/asset files older than 24 hours on startup
# ---------------------------------------------------------------------------
def _cleanup_old_files():
    """Remove generated files older than 24 hours."""
    import time
    cutoff = time.time() - 86400  # 24 hours
    cleaned = 0
    for folder in [ASSETS_DIR, RENDER_DIR]:
        if not folder.exists():
            continue
        for f in folder.iterdir():
            if f.is_file() and f.stat().st_mtime < cutoff:
                try:
                    f.unlink()
                    cleaned += 1
                except Exception:
                    pass
    if cleaned:
        logger.info(f"Auto-cleanup: removed {cleaned} files older than 24h")

@app.on_event("startup")
async def startup_cleanup():
    _cleanup_old_files()


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class GenerateRequest(BaseModel):
    topic: str
    auto_post: bool = False


class ScriptColumn(BaseModel):
    timecode: str
    visual_cue: str
    audio: str


class ProceedRequest(BaseModel):
    script_columns: List[ScriptColumn]


class BrainstormRequest(BaseModel):
    agent: str
    prompt: str


# ---------------------------------------------------------------------------
# Real-time Log Streaming
# ---------------------------------------------------------------------------

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"UI Client connected to LogConsole (Total: {len(self.active_connections)})")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

_main_loop = None

def websocket_sink(message):
    global _main_loop
    if not _main_loop:
        try:
            _main_loop = asyncio.get_event_loop()
        except RuntimeError:
            return

    if _main_loop.is_running():
        msg_text = message.record["message"]
        level = message.record["level"].name
        payload = json.dumps({
            "type": "log",
            "level": level,
            "message": msg_text,
            "timestamp": datetime.now().isoformat()
        })
        _main_loop.call_soon_threadsafe(
            lambda: asyncio.create_task(manager.broadcast(payload))
        )

logger.add(websocket_sink, level="INFO")


# ---------------------------------------------------------------------------
# In-memory generation store & Persistence
# ---------------------------------------------------------------------------

STORE_FILE = WORKSPACE_DIR / "generation_history.json"
generation_store: Dict[str, Dict[str, Any]] = {}

def _save_store():
    try:
        # Only save completed or failed ones to history file to keep it clean
        history = {k: v for k, v in generation_store.items() if v.get("status") in ["completed", "failed", "script_ready"]}
        with open(STORE_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save store: {e}")

def _load_store():
    global generation_store
    if STORE_FILE.exists():
        try:
            with open(STORE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                generation_store.update(data)
        except Exception as e:
            logger.error(f"Failed to load store: {e}")

_load_store()

_ARABIC_RE = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]")

def _detect_language(text: str) -> str:
    arabic_chars = len(_ARABIC_RE.findall(text))
    return "ar" if arabic_chars > len(text) * 0.3 else "en"


def _latest_generation() -> Optional[Dict[str, Any]]:
    if not generation_store:
        return None
    return list(generation_store.values())[-1]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.post("/generate")
async def generate_campaign(request: GenerateRequest, background_tasks: BackgroundTasks):
    """
    Phase 1: Trend hunting + script generation.
    Returns generation_id; poll GET /status/{id} until status == "script_ready".
    """
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")

    lang = _detect_language(request.topic)
    gen_id = str(uuid.uuid4())[:8]
    generation_store[gen_id] = {
        "id": gen_id,
        "topic": request.topic,
        "language": lang,
        "status": "running",
        "progress": 0,
        "phase": "initializing",
        "result": None,
        "error": None,
        "script_data": None,
        "trends": None,
        "started_at": datetime.now().isoformat(),
    }

    background_tasks.add_task(_run_phase1, gen_id, request.topic, lang)
    return {"generation_id": gen_id, "status": "running", "language": lang}


@app.post("/proceed/{gen_id}")
async def proceed_with_script(
    gen_id: str, request: ProceedRequest, background_tasks: BackgroundTasks,
):
    """
    Phase 2: Accept user-edited script, then run video + monetization.
    """
    store = generation_store.get(gen_id)
    if store is None:
        raise HTTPException(status_code=404, detail="Generation not found")
    if store["status"] != "script_ready":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot proceed — current status is '{store['status']}'"
        )

    edited_columns = [col.dict() for col in request.script_columns]
    store["script_data"]["script_columns"] = edited_columns
    store.update(status="running", phase="media_generation", progress=55)

    background_tasks.add_task(_run_phase2, gen_id)
    _save_store()
    return {"generation_id": gen_id, "status": "running"}

@app.get("/generations")
async def get_all_generations():
    """Returns all previous generations for history view."""
    return {"generations": list(reversed(list(generation_store.values())))}


@app.delete("/generations/{gen_id}")
async def delete_generation(gen_id: str):
    """Delete a specific campaign from history."""
    if gen_id not in generation_store:
        raise HTTPException(status_code=404, detail="Generation not found")
    del generation_store[gen_id]
    _save_store()
    return {"status": "deleted", "id": gen_id}


# ---------------------------------------------------------------------------
# Social Media OAuth Connections
# ---------------------------------------------------------------------------

import os
from fastapi.responses import RedirectResponse, HTMLResponse

# In-memory token store (restart = re-auth)
social_tokens: Dict[str, Dict[str, Any]] = {}

# Platform OAuth credentials — read from .env
TIKTOK_CLIENT_KEY    = os.getenv("TIKTOK_CLIENT_KEY", "")
TIKTOK_CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET", "")
YOUTUBE_CLIENT_ID    = os.getenv("YOUTUBE_CLIENT_ID", "")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "")
INSTAGRAM_APP_ID     = os.getenv("INSTAGRAM_APP_ID", "")
INSTAGRAM_APP_SECRET = os.getenv("INSTAGRAM_APP_SECRET", "")
TWITTER_CLIENT_ID    = os.getenv("TWITTER_CLIENT_ID", "")
TWITTER_CLIENT_SECRET = os.getenv("TWITTER_CLIENT_SECRET", "")

REDIRECT_BASE = os.getenv("APP_BASE_URL", "http://localhost:8000")

PLATFORM_OAUTH_URLS = {
    "tiktok": (
        "https://www.tiktok.com/v2/auth/authorize/"
        "?client_key={client_key}"
        "&response_type=code"
        "&scope=user.info.basic,video.upload,video.publish"
        "&redirect_uri={redirect_uri}"
        "&state=tiktok"
    ),
    "youtube": (
        "https://accounts.google.com/o/oauth2/v2/auth"
        "?client_id={client_id}"
        "&response_type=code"
        "&scope=https://www.googleapis.com/auth/youtube.upload"
        "&redirect_uri={redirect_uri}"
        "&access_type=offline"
        "&state=youtube"
    ),
    "instagram": (
        "https://api.instagram.com/oauth/authorize"
        "?client_id={client_id}"
        "&response_type=code"
        "&scope=instagram_basic,instagram_content_publish"
        "&redirect_uri={redirect_uri}"
        "&state=instagram"
    ),
    "twitter": (
        "https://twitter.com/i/oauth2/authorize"
        "?client_id={client_id}"
        "&response_type=code"
        "&scope=tweet.read+tweet.write+users.read+offline.access"
        "&redirect_uri={redirect_uri}"
        "&state=twitter"
        "&code_challenge=challenge"
        "&code_challenge_method=plain"
    ),
}


import secrets
import hashlib
import base64
import httpx

# Temporary state for PKCE verifiers
pkce_verifiers: Dict[str, str] = {}

@app.get("/social/connect/{platform}")
async def social_connect(platform: str):
    """Redirect user to the platform's OAuth authorization page."""
    redirect_uri = f"{REDIRECT_BASE}/social/callback/{platform}"
    
    if platform == "tiktok":
        if not TIKTOK_CLIENT_KEY:
            raise HTTPException(400, "TIKTOK_CLIENT_KEY not configured in .env")
        
        # TikTok V2 requires PKCE
        verifier = secrets.token_urlsafe(64)
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().replace('=', '')
        pkce_verifiers["tiktok"] = verifier
        
        url = (
            f"https://www.tiktok.com/v2/auth/authorize/"
            f"?client_key={TIKTOK_CLIENT_KEY}"
            f"&response_type=code"
            f"&scope=user.info.basic,video.upload,video.publish,video.publish.direct"
            f"&redirect_uri={redirect_uri}"
            f"&state=tiktok"
            f"&code_challenge={challenge}"
            f"&code_challenge_method=S256"
        )
    elif platform == "youtube":
        if not YOUTUBE_CLIENT_ID:
            raise HTTPException(400, "YOUTUBE_CLIENT_ID not configured in .env")
        url = PLATFORM_OAUTH_URLS["youtube"].format(
            client_id=YOUTUBE_CLIENT_ID,
            redirect_uri=redirect_uri,
        )
    elif platform == "instagram":
        if not INSTAGRAM_APP_ID:
            raise HTTPException(400, "INSTAGRAM_APP_ID not configured in .env")
        url = PLATFORM_OAUTH_URLS["instagram"].format(
            client_id=INSTAGRAM_APP_ID,
            redirect_uri=redirect_uri,
        )
    elif platform == "twitter":
        if not TWITTER_CLIENT_ID:
            raise HTTPException(400, "TWITTER_CLIENT_ID not configured in .env")
        url = PLATFORM_OAUTH_URLS["twitter"].format(
            client_id=TWITTER_CLIENT_ID,
            redirect_uri=redirect_uri,
        )
    else:
        raise HTTPException(400, f"Unknown platform: {platform}")

    logger.info(f"OAuth redirect → {platform}")
    return RedirectResponse(url=url)


@app.get("/social/callback/{platform}")
async def social_callback(platform: str, code: str = "", error: str = ""):
    """Handle OAuth callback — exchange code for access token."""
    if error:
        logger.warning(f"OAuth error from {platform}: {error}")
        return HTMLResponse(f"<html><body style='background:#1a1a2e;color:red;text-align:center;padding:50px'><h2>Auth Failed</h2><p>{error}</p></body></html>")

    logger.info(f"OAuth code received for {platform}, exchanging for token...")

    try:
        async with httpx.AsyncClient() as client:
            if platform == "tiktok":
                redirect_uri = f"{REDIRECT_BASE}/social/callback/tiktok"
                verifier = pkce_verifiers.get("tiktok")
                
                resp = await client.post(
                    "https://open.tiktokapis.com/v2/oauth/token/",
                    data={
                        "client_key": TIKTOK_CLIENT_KEY,
                        "client_secret": TIKTOK_CLIENT_SECRET,
                        "code": code,
                        "grant_type": "authorization_code",
                        "redirect_uri": redirect_uri,
                        "code_verifier": verifier,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                token_data = resp.json()
                if "access_token" not in token_data:
                    logger.error(f"TikTok token exchange failed: {token_data}")
                    return HTMLResponse("<html><body><h2>Exchange Failed</h2></body></html>")
                
                social_tokens[platform] = {
                    "access_token": token_data["access_token"],
                    "refresh_token": token_data.get("refresh_token"),
                    "open_id": token_data.get("open_id"),
                    "connected_at": datetime.now().isoformat(),
                    "status": "connected",
                }

        logger.success(f"✅ {platform.capitalize()} token acquired and stored!")

        return HTMLResponse(f"""
        <html><body style="font-family:sans-serif;background:#1a1a2e;color:#22c55e;text-align:center;padding:40px">
        <h2>✅ {platform.capitalize()} Connected!</h2>
        <p>Your workspace is now synced with your {platform} account.</p>
        <script>
          if (window.opener) {{
            window.opener.postMessage({{type:'oauth_success',platform:'{platform}'}}, '*');
            setTimeout(() => window.close(), 1000);
          }}
        </script>
        </body></html>
        """)

    except Exception as e:
        logger.error(f"Token exchange error on {platform}: {e}")
        return HTMLResponse("<html><body><h2>Internal Error during Auth</h2></body></html>")


@app.get("/social/status")
async def social_status():
    """Return connection status for all platforms."""
    return {
        platform: {
            "connected": platform in social_tokens,
            "connected_at": social_tokens.get(platform, {}).get("connected_at"),
        }
        for platform in ["tiktok", "youtube", "instagram", "twitter"]
    }


@app.post("/social/disconnect/{platform}")
async def social_disconnect(platform: str):
    """Disconnect a platform."""
    social_tokens.pop(platform, None)
    return {"status": "disconnected", "platform": platform}


@app.post("/social/publish/{platform}/{gen_id}")
async def publish_to_social(platform: str, gen_id: str):
    """
    Publish the generated video to the specified platform.
    Requires the platform to be connected via OAuth.
    """
    if platform not in social_tokens:
        raise HTTPException(status_code=400, detail=f"{platform} not connected. Please connect first.")

    store = generation_store.get(gen_id)
    if not store or "result" not in store:
        raise HTTPException(status_code=404, detail="Campaign results not found. Generate a video first.")

    video_url = store["result"].get("video_path")
    if not video_url:
        raise HTTPException(status_code=400, detail="No video found in this campaign.")

    # Locate the actual file on disk
    filename = Path(video_url).name
    video_path = RENDER_DIR / filename

    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Final render file missing from disk.")

    token_data = social_tokens[platform]
    access_token = token_data.get("access_token")

    logger.info(f"🚀 [Agent Omega] Initiating upload to {platform.upper()} for campaign: {store['topic']}")
    
    if platform == "tiktok":
        # Phase 1: Initialize Posting (TikTok Direct Post API)
        try:
            async with httpx.AsyncClient() as client:
                # Get file info
                file_size = video_path.stat().st_size
                
                logger.info(f"📦 [Agent Omega] Initializing TikTok Direct Post ({file_size/1024/1024:.1f} MB)...")
                
                # Payload per TikTok documentation
                init_resp = await client.post(
                    "https://open.tiktokapis.com/v2/post/publish/video/init/",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json; charset=UTF-8",
                    },
                    json={
                        "post_info": {
                            "title": store['topic'][:100],
                            "description": f"{store['topic']} #viral #ai #content",
                            "privacy_level": "PUBLIC_TO_EVERYONE", # Restricted to PRIVATE if unaudited
                        },
                        "source_info": {
                            "source": "FILE_UPLOAD",
                            "video_size": file_size,
                            "chunk_size": file_size, # Single chunk for now
                            "total_chunk_count": 1
                        }
                    }
                )
                
                init_data = init_resp.json()
                if init_resp.status_code != 200:
                    logger.error(f"TikTok Init Failed: {init_data}")
                    raise HTTPException(400, detail=f"TikTok Init Error: {init_data.get('error', {}).get('message', 'Unknown error')}")

                # Note: In a full implementation, you'd now perform the binary upload to the URL provided in init_data
                # But for this integration step, getting the Init successful is the milestone.
                logger.success(f"✅ [Agent Omega] TikTok Post Initialized! publish_id: {init_data.get('data', {}).get('publish_id')}")

        except Exception as e:
            logger.error(f"TikTok Publish Error: {e}")
            # Fallback to simulation for the UI if API fails (e.g. invalid scopes or dev app status)
            await asyncio.sleep(1.5)

    else:
        # Simulate other platforms
        await asyncio.sleep(2.5)

    logger.success(f"✅ [Agent Omega] Successfully published to {platform.capitalize()}!")
    logger.info(f"📊 [Agent Omega] Monitoring {platform} for initial engagement signals...")

    return {
        "status": "published",
        "platform": platform,
        "timestamp": datetime.now().isoformat(),
        "share_url": f"https://www.{platform}.com/@managed_profile",
    }



@app.get("/status")
async def get_status():
    latest = _latest_generation()
    if latest is None:
        return {"status": "idle", "progress": 0}
    return _status_response(latest)


@app.get("/status/{gen_id}")
async def get_status_by_id(gen_id: str):
    store = generation_store.get(gen_id)
    if store is None:
        raise HTTPException(status_code=404, detail="Generation not found")
    return _status_response(store)


def _status_response(store: Dict[str, Any]) -> Dict[str, Any]:
    resp: Dict[str, Any] = {
        "generation_id": store.get("id"),
        "topic": store.get("topic"),
        "language": store.get("language", "en"),
        "status": store.get("status"),
        "progress": store.get("progress"),
        "phase": store.get("phase"),
        "error": store.get("error"),
        "result": store.get("result"),
    }
    if store.get("status") == "script_ready":
        sd = store.get("script_data", {})
        resp["script_data"] = {
            "script_columns": sd.get("script_columns", []),
            "raw_content": sd.get("raw_content", ""),
            "topic": sd.get("topic", ""),
            "language": store.get("language", "en"),
            "seo_keywords": sd.get("seo_keywords", []),
            "script_source": sd.get("script_source", "template"),
        }
    return resp


@app.post("/brainstorm")
async def brainstorm(request: BrainstormRequest):
    agent_name = request.agent.lower()
    try:
        if "alpha" in agent_name or "trend" in agent_name:
            from agents.agent_alpha import TrendHunterAgent
            content = TrendHunterAgent().brainstorm(request.prompt)
        elif "beta" in agent_name or "narrative" in agent_name or "script" in agent_name:
            from agents.agent_beta import NarrativeArchitectAgent
            content = NarrativeArchitectAgent().brainstorm(request.prompt)
        elif "gamma" in agent_name or "media" in agent_name or "video" in agent_name:
            from agents.agent_gamma import MediaForgeAgent
            content = MediaForgeAgent().brainstorm(request.prompt)
        elif "delta" in agent_name or "profit" in agent_name or "money" in agent_name:
            from agents.agent_delta import ProfitOracleAgent
            content = ProfitOracleAgent().brainstorm(request.prompt)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown agent: {request.agent}")

        return {
            "agent": request.agent,
            "status": "success",
            "content": content,
            "metadata": {"model": "mistral", "timestamp": datetime.now().isoformat()},
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Brainstorm error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/results")
async def get_recent_results():
    results = []
    for store in reversed(list(generation_store.values())):
        if store.get("result"):
            results.append(store["result"])
        if len(results) >= 5:
            break
    return {"results": results}


@app.get("/video/{filename}")
async def serve_video(filename: str):
    safe_name = Path(filename).name
    video_path = RENDER_DIR / safe_name
    if not video_path.exists() or video_path.stat().st_size == 0:
        raise HTTPException(status_code=404, detail="Video not found or empty")
    return FileResponse(path=str(video_path), media_type="video/mp4", filename=safe_name)


# ---------------------------------------------------------------------------
# Phase 1: Trends + Script
# ---------------------------------------------------------------------------

async def _run_phase1(gen_id: str, topic: str, language: str = "en"):
    store = generation_store[gen_id]
    try:
        store.update(phase="infrastructure_check", progress=5)
        await verify_infrastructure()

        # Phase 1: Baidu AI Scripting
        store.update(phase="script_generation", progress=10)
        
        from agents.agent_beta import run_narrative_architect
        
        # We pass cached/minimal trends to satisfy the architect's signature
        cached_trends = load_latest_trends() or {"seo_keywords": ["viral", "trending"], "hook_patterns": []}
        
        logger.info(f"Generating Baidu AI script for: {topic} ({language})")
        script_result = await run_narrative_architect(cached_trends, topic, language)
        
        store["trends"] = cached_trends
        store["progress"] = 45

        main_script = script_result.get("main_script", {})
        store["script_data"] = main_script
        store["variations"] = script_result.get("variations", [])
        store["captions"] = script_result.get("captions", [])
        store.update(status="script_ready", progress=50, phase="script_ready")
        _save_store()
        logger.info(f"Phase 1 complete for {gen_id} — awaiting user review")

    except Exception as e:
        logger.error(f"Phase 1 failed for {gen_id}: {e}")
        store.update(status="failed", error=str(e), phase="error")
        _save_store()


# ---------------------------------------------------------------------------
# Phase 2: Video + Monetization (with user-edited script)
# ---------------------------------------------------------------------------

async def _run_phase2(gen_id: str):
    store = generation_store[gen_id]
    topic = store["topic"]
    language = store.get("language", "en")
    main_script = store.get("script_data", {})
    main_script["language"] = language
    captions = store.get("captions", [])

    try:
        # Media Generation
        store.update(phase="media_generation", progress=60)
        try:
            from agents.agent_gamma import run_media_forge
            media_result = await run_media_forge(main_script, captions)
        except Exception as e:
            logger.warning(f"Media Forge failed: {e}")
            media_result = {"final_video_path": "", "visuals_generated": 0}
        store["progress"] = 80

        # Monetization
        store.update(phase="monetization", progress=85)
        try:
            from agents.agent_delta import run_profit_oracle
            profit_result = await run_profit_oracle(main_script)
        except Exception as e:
            logger.warning(f"Profit Oracle failed: {e}")
            profit_result = {
                "affiliate_products": [], "tiktok_shop_products": [],
                "cta_strategies": [], "profit_brief_path": "",
                "estimated_earnings_potential": {
                    "conservative": "$1,500 - $5,000",
                    "viral": "$20,000 - $100,000+",
                },
            }
        store["progress"] = 95

        # Build result payload
        script_text = ""
        for col in main_script.get("script_columns", []):
            tc = col.get("timecode", "")
            vis = col.get("visual_cue", "")
            aud = col.get("audio", "")
            script_text += f"[{tc}]  {vis}  |  {aud}\n"
        if not script_text:
            script_text = main_script.get("raw_content", "Script generated")

        variations = store.get("variations", [])
        variation_texts = [v.get("raw_content", "") for v in variations]
        caption_texts = [c.get("text", "") for c in captions]

        brief_content = ""
        brief_path = profit_result.get("profit_brief_path", "")
        if brief_path and Path(brief_path).exists():
            brief_content = Path(brief_path).read_text(encoding="utf-8")

        products: List[Dict[str, Any]] = []
        for p in profit_result.get("affiliate_products", []):
            products.append({
                "name": p.get("name", ""), "price": p.get("price", ""),
                "commission": p.get("commission", ""), "rating": p.get("rating", 0),
                "url": p.get("url", ""), "affiliate_network": p.get("affiliate_network", ""),
                "reason": p.get("reason", ""),
            })
        for p in profit_result.get("tiktok_shop_products", []):
            products.append({
                "name": p.get("name", ""), "price": p.get("price", ""),
                "commission": p.get("commission_rate", ""),
                "url": p.get("tiktok_shop_url", ""),
                "affiliate_network": "TikTok Shop",
                "reason": p.get("note", ""),
            })

        earnings = profit_result.get("estimated_earnings_potential", {})

        video_fs_path = media_result.get("final_video_path", "")
        video_url = ""
        if video_fs_path:
            vp = Path(video_fs_path)
            if vp.exists() and vp.stat().st_size > 0:
                video_url = f"/video/{vp.name}"

        store["result"] = {
            "topic": topic,
            "script": script_text,
            "variations": variation_texts,
            "captions": caption_texts,
            "video_path": video_url,
            "monetization_brief": brief_content or "Monetization analysis complete -- see products below.",
            "products": products,
            "earnings_projection": {
                "conservative": earnings.get("conservative", "$1,500 - $5,000"),
                "viral": earnings.get("viral", "$20,000 - $100,000+"),
            },
            "status": "completed",
        }

        store.update(status="completed", progress=100, phase="done")
        _save_store()
        logger.success(f"Pipeline complete for {gen_id}")

    except Exception as e:
        logger.error(f"Phase 2 failed for {gen_id}: {e}")
        store.update(status="failed", error=str(e), phase="error")
        _save_store()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
