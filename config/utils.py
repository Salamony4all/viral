"""
Utility functions for the Viral Engine
"""
import json
import os
import asyncio
import aiohttp
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from loguru import logger
from config.settings import (
    COMFYUI_BASE_URL, TRENDS_DIR, 
    RENDER_DIR, REVIEW_DIR, LOG_FILE, LOG_LEVEL
)

# Configure logging
logger.remove()  # Remove default handler
logger.add(
    LOG_FILE,
    level=LOG_LEVEL,
    format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    rotation="500 MB",
)
def _safe_print(msg):
    try:
        print(msg, end="")
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="replace").decode("ascii"), end="")

logger.add(
    _safe_print,
    level=LOG_LEVEL,
    format="<level>[{level}]</level> {message}",
    colorize=True,
)


def save_trends_manifest(trends_data: Dict[str, Any]) -> Path:
    """Save trends data to JSON manifest."""
    manifest_path = TRENDS_DIR / f"current_trends_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(trends_data, f, indent=2)
    logger.info(f"Trends manifest saved: {manifest_path}")
    return manifest_path


def load_latest_trends() -> Optional[Dict[str, Any]]:
    """Load the latest trends manifest."""
    json_files = sorted(TRENDS_DIR.glob("current_trends_*.json"), reverse=True)
    if not json_files:
        logger.warning("No trends manifest found")
        return None
    
    with open(json_files[0], "r", encoding="utf-8") as f:
        data = json.load(f)
    logger.info(f"Loaded trends from: {json_files[0]}")
    return data


async def check_service_health(service_name: str, url: str) -> bool:
    """Check if a local service is running."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                is_healthy = resp.status == 200
                status = "[OK] Online" if is_healthy else "[X] Offline"
                logger.info(f"{service_name}: {status}")
                return is_healthy
    except Exception as e:
        logger.warning(f"{service_name}: [X] Offline - {str(e)}")
        return False


async def verify_infrastructure() -> Dict[str, bool]:
    """Verify all required services are running."""
    logger.info("Verifying infrastructure...")
    
    checks = {
        "ComfyUI API": await check_service_health("ComfyUI", f"{COMFYUI_BASE_URL}/api/"),
    }
    
    all_healthy = all(checks.values())
    if not all_healthy:
        logger.warning("Some services are offline. Running in degraded mode.")
    
    return checks


def notify_review_ready(video_path: Path, script_path: Path, brief_path: Path):
    """Notify user that content is ready for review."""
    review_data = {
        "timestamp": datetime.now().isoformat(),
        "video": str(video_path),
        "script": str(script_path),
        "profit_brief": str(brief_path),
    }
    
    notification_path = REVIEW_DIR / f"ready_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(notification_path, "w", encoding="utf-8") as f:
        json.dump(review_data, f, indent=2)
    
    message = f"""
🎬 VIRAL CANDIDATE READY FOR REVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📹 Video: {video_path.name}
📝 Script: {script_path.name}
💰 Profit Brief: {brief_path.name}

📂 Review Folder: {REVIEW_DIR}

⚡ NEXT STEP:
1. Review the generated content
2. Record a 3-sec intro/reaction using TikTok's native camera
3. Apply Green Screen effect with our video as background
4. Post manually with suggested hashtags and music

This signals "Human Creator" to the algorithm!
"""
    
    logger.info(message)
    
    # Try Telegram notification if configured
    try:
        from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            import requests
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={"chat_id": TELEGRAM_CHAT_ID, "text": message},
                timeout=5,
            )
    except Exception as e:
        logger.debug(f"Telegram notification skipped: {e}")


def load_config_from_env(env_file: str = ".env"):
    """Load configuration from .env file."""
    env_path = Path(env_file)
    if env_path.exists():
        logger.info(f"Loaded environment from: {env_path}")
    else:
        logger.warning(f"No .env file found at {env_path}")


class JoinedOutput:
    """Wrapper for CrewAI agent output aggregation."""
    
    def __init__(self):
        self.results = {}
    
    def add_agent_output(self, agent_name: str, output: str):
        """Add output from an agent."""
        self.results[agent_name] = output
    
    def to_dict(self) -> Dict[str, Any]:
        """Export results as dictionary."""
        return self.results
    
    def to_json(self, output_file: Optional[Path] = None) -> str:
        """Export results as JSON."""
        json_str = json.dumps(self.results, indent=2)
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(json_str)
        return json_str
