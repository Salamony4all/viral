"""
Configuration settings for the Viral Engine
"""
import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Project Paths
PROJECT_ROOT = Path(__file__).parent.parent
WORKSPACE_DIR = PROJECT_ROOT / "workspace"
TRENDS_DIR = WORKSPACE_DIR / "trends"
ASSETS_DIR = WORKSPACE_DIR / "assets"
RENDER_DIR = WORKSPACE_DIR / "render"
REVIEW_DIR = WORKSPACE_DIR / "review"

# Ensure directories exist
for dir_path in [TRENDS_DIR, ASSETS_DIR, RENDER_DIR, REVIEW_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Local Service URLs
COMFYUI_BASE_URL = os.getenv("COMFYUI_BASE_URL", "http://localhost:8188")
COMFYUI_WEBSOCKET_URL = os.getenv("COMFYUI_WEBSOCKET_URL", "ws://localhost:8188/ws")

# LLM Models
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

# TikTok / Content Config
CONTENT_LENGTH_SECONDS = int(os.getenv("CONTENT_LENGTH_SECONDS", 30))
TARGET_NICHE = os.getenv("TARGET_NICHE", "lifestyle")
MONETIZATION_FOCUS = os.getenv("MONETIZATION_FOCUS", "affiliate")  # affiliate, shop, seo, hybrid

# Scraping Config
PLAYWRIGHT_HEADLESS = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true"
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
SCRAPE_TIMEOUT = int(os.getenv("SCRAPE_TIMEOUT", 30))

# Media Generation Config
VIDEO_RESOLUTION = os.getenv("VIDEO_RESOLUTION", "1080x1920")  # TikTok native
VIDEO_FPS = int(os.getenv("VIDEO_FPS", 30))
AUDIO_BITRATE = os.getenv("AUDIO_BITRATE", "192k")


def _resolve_ffmpeg() -> str:
    """Resolve FFmpeg executable: bundled imageio-ffmpeg -> system PATH."""
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        pass
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg
    raise FileNotFoundError(
        "FFmpeg not found. Install imageio-ffmpeg (`pip install imageio-ffmpeg`) "
        "or add ffmpeg to your system PATH."
    )


FFMPEG_BIN = _resolve_ffmpeg()

# Notification Config
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
USE_LOCAL_NOTIFICATIONS = os.getenv("USE_LOCAL_NOTIFICATIONS", "true").lower() == "true"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = PROJECT_ROOT / "logs" / "viral_engine.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Stock Video APIs (free tiers — get keys at pexels.com/api and pixabay.com/api/docs)
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "")

# API Keys (for fallback cloud services, if needed)
AMAZON_API_KEY = os.getenv("AMAZON_API_KEY", "")
TIKTOK_SHOP_API_KEY = os.getenv("TIKTOK_SHOP_API_KEY", "")

# Baidu AI Studio (Ernie) - for dynamic script generation
BAIDU_AI_API_KEY = os.getenv("BAIDU_AI_API_KEY", "")
BAIDU_AI_BASE_URL = os.getenv("BAIDU_AI_BASE_URL", "https://aistudio.baidu.com/llm/lmapi/v3")
BAIDU_AI_MODEL = os.getenv("BAIDU_AI_MODEL", "ernie-5.0-thinking-preview")
BAIDU_AI_FALLBACK_MODEL = os.getenv("BAIDU_AI_FALLBACK_MODEL", "ernie-4.5-turbo-128k-preview")

# Google Veo 3.1 (text-to-video) - Gemini API, get key at aistudio.google.com
GOOGLE_VEO_API_KEY = os.getenv("GOOGLE_VEO_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
GOOGLE_VEO_MODEL = os.getenv("GOOGLE_VEO_MODEL", "veo-3.1-generate-preview")

# Replicate (text-to-video AI) - get token at replicate.com/account
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")
REPLICATE_VIDEO_MODEL = os.getenv("REPLICATE_VIDEO_MODEL", "minimax/video-01")

# CrewAI Config
CREW_VERBOSE = os.getenv("CREW_VERBOSE", "false").lower() == "true"
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", 10))
