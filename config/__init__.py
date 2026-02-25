"""
Viral Engine Configuration Package
"""
from .settings import *
from .utils import *

__all__ = [
    "PROJECT_ROOT",
    "WORKSPACE_DIR",
    "TRENDS_DIR",
    "ASSETS_DIR",
    "RENDER_DIR",
    "REVIEW_DIR",
    "OLLAMA_BASE_URL",
    "COMFYUI_BASE_URL",
    "OLLAMA_MODEL",
    "save_trends_manifest",
    "load_latest_trends",
    "verify_infrastructure",
    "notify_review_ready",
]
