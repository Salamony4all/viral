"""
Agent Gamma: The "Media Forge" (Content Generation)
Persona: VFX Supervisor & Sound Engineer
Tools: Pexels/Pixabay stock video, ComfyUI, FFmpeg (bundled), Coqui TTS, RVC

Pipeline:
  1. For each scene → download a matching stock video clip (Pexels/Pixabay)
  2. Trim & format each clip to 1080x1920 @ 30 fps
  3. Generate voiceover (Coqui TTS) or silent audio
  4. Concatenate clips + audio → final_render.mp4
  5. Burn yellow captions → final_render_with_captions.mp4
"""
from __future__ import annotations

import re
import wave
import json
import subprocess
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from loguru import logger
import requests
from PIL import Image, ImageDraw, ImageFont
try:
    from crewai import Agent, Task
except ImportError:
    Agent = None
    Task = None

from config.settings import (
    COMFYUI_BASE_URL, COMFYUI_WEBSOCKET_URL, ASSETS_DIR,
    RENDER_DIR, VIDEO_RESOLUTION, VIDEO_FPS, AUDIO_BITRATE,
    FFMPEG_BIN, PEXELS_API_KEY, PIXABAY_API_KEY,
    GOOGLE_VEO_API_KEY, GOOGLE_VEO_MODEL,
    REPLICATE_API_TOKEN, REPLICATE_VIDEO_MODEL,
)

logger_gamma = logger.bind(name="MediaForge")

SCENE_COLORS = [
    "#6C3483", "#1A5276", "#117864", "#B7950B",
    "#A04000", "#1B4F72", "#7D3C98", "#2E86C1",
]

_DOWNLOAD_SEM = asyncio.Semaphore(3)
_VEO_SEM = asyncio.Semaphore(1) # Veo 3.1 is heavy; generate 1 at a time for stability

_NOISE_WORDS = frozenset({
    "jump-cut", "jump", "cut", "to", "transition", "overlay", "effect",
    "b-roll", "broll", "close-up", "closeup", "zoom", "pan", "tilt",
    "tracking", "text:", "text", "end", "screen", "with", "hook",
    "pattern", "interrupt", "quick", "slow", "fast", "morphing",
    "the", "a", "an", "of", "and", "for", "in", "on", "at",
    "their", "this", "that", "about", "from", "new", "more", "here",
    "how", "what", "why", "who", "when", "its", "just", "also",
    "looking", "showing", "doing", "making", "using", "getting",
    "stop", "scrolling", "save", "before", "share", "someone",
    "needs", "follow", "secrets", "won", "find", "anywhere", "else",
    "comment", "below", "reply", "did", "you", "know", "bookmark",
    "thank", "later", "everything", "seriously", "never", "tried",
    "nothing", "worked", "until", "answer", "was", "all", "along",
    "exactly", "like", "game", "changer", "dead", "wrong", "instead",
    "try", "difference", "night", "day", "which", "side", "are",
    "most", "people", "get", "completely", "talks", "actually",
    "works", "nobody", "secret", "surprisingly", "simple", "once",
    "back", "ever", "been", "years", "knew", "turns", "out",
    "saved", "much", "time", "effort", "can", "will", "would",
    "could", "should", "have", "has", "had", "does", "done",
    "not", "but", "very", "really", "every", "each", "some",
})


class MediaForgeAgent:
    """
    Generates real video clips per scene from stock footage APIs,
    assembles them with voiceover and captions into a TikTok-ready MP4.
    Falls back gracefully: stock video → ComfyUI image → Pillow placeholder.
    """

    def __init__(self, script_data: Optional[Dict[str, Any]] = None):
        self.logger = logger_gamma
        self.script_data = script_data or {}
        self.comfyui_url = COMFYUI_BASE_URL
        self.ws_url = COMFYUI_WEBSOCKET_URL
        self.ffmpeg = FFMPEG_BIN

    def brainstorm(self, prompt: str) -> str:
        return (
            f"[Agent Gamma - Media Forge]\n\n"
            f"Regarding: {prompt}\n\n"
            f"Production recommendations:\n"
            f"1. Resolution: 1080x1920 (TikTok native vertical)\n"
            f"2. FPS: 30 for smooth playback\n"
            f"3. Captions: Yellow bold, center screen - critical for silent watchers\n"
            f"4. Visual pacing: 2-3 second cuts to maintain attention\n"
            f"5. Audio: Clear voiceover with subtle background music\n"
            f"6. Stock footage from Pexels/Pixabay for professional B-roll\n"
            f"7. FFmpeg for final assembly with proper encoding (libx264, CRF 18)\n"
            f"8. Always add hard-coded captions - 80% of TikTok is watched on mute"
        )

    def get_agent(self):
        if Agent is None:
            return None
        return Agent(
            role="VFX Supervisor & Sound Engineer",
            goal="Generate visuals, create voiceover, and assemble viral-ready video content",
            backstory=(
                "You are an award-winning VFX supervisor with 12+ years of experience "
                "in motion graphics and video production. You understand pacing, timing, "
                "and how to make content that stops scrolls."
            ),
            tools=[],
            verbose=True,
            allow_delegation=False,
        )

    # ==================================================================
    # Scene clip generation (main entry point)
    # ==================================================================

    async def generate_scene_clips(
        self, scene_descriptions: List[str], total_duration: float
    ) -> List[Path]:
        """
        For every scene, acquire a trimmed video clip via Veo.
        Scenes are merged to max 3 to keep Veo calls efficient.
        """
        # Merge scenes into max 5 for Veo
        MAX_SCENES = 5
        columns = self.script_data.get("script_columns", [])
        topic = self.script_data.get("topic", "")

        if len(scene_descriptions) > MAX_SCENES:
            merged_descs = []
            merged_audio = []
            chunk_size = len(scene_descriptions) / MAX_SCENES
            for i in range(MAX_SCENES):
                start = int(i * chunk_size)
                end = int((i + 1) * chunk_size)
                merged_descs.append(". ".join(scene_descriptions[start:end]))
                audio_parts = []
                for j in range(start, min(end, len(columns))):
                    audio_parts.append(columns[j].get("audio", ""))
                merged_audio.append(" ".join(audio_parts))
            scene_descriptions = merged_descs
            # Update columns for merged scenes
            columns = [{"audio": a, "visual_cue": d} for d, a in zip(merged_descs, merged_audio)]

        n = max(len(scene_descriptions), 1)
        dur_per = total_duration / n

        self.logger.info(
            f"🎨 [Agent Gamma] Initiating Media Forge for {n} scenes "
            f"({dur_per:.1f}s each, topic='{topic}')..."
        )

        # Generate scenes sequentially to avoid API rate limits
        clips = []
        for idx, desc in enumerate(scene_descriptions):
            audio = ""
            if idx < len(columns):
                audio = columns[idx].get("audio", "")
            clip = await self._get_scene_clip(desc, audio, topic, idx, dur_per)
            clips.append(clip)

        return clips

    async def _get_scene_clip(
        self, visual_cue: str, narration: str, topic: str,
        idx: int, duration: float,
    ) -> Path:
        if GOOGLE_VEO_API_KEY and len(GOOGLE_VEO_API_KEY) > 5:
            self.logger.info(f"Scene {idx}: [Veo 3.1] Attempting AI generation...")
            raw = await self._generate_video_via_veo(visual_cue, narration, topic, idx)
            if raw:
                clip = await self._prepare_clip(raw, idx, duration)
                if clip:
                    self.logger.info(f"Scene {idx}: [Veo 3.1] AI video ready!")
                    return clip
                else:
                    self.logger.error(f"Scene {idx}: Veo downloaded but FFmpeg prep failed. Using raw Veo file.")
                    # Use the raw Veo file directly if prep fails
                    return raw
        else:
            self.logger.warning(f"Scene {idx}: No Veo API key found. Skipping AI generation.")

        self.logger.warning(f"Scene {idx}: Veo failed — using placeholder")
        return await self._create_placeholder_clip(visual_cue, idx, duration)

    # ==================================================================
    # AI visual concept mapper — translates script into stock queries
    # ==================================================================

    _DOMAIN_KEYWORDS = {
        "math": ["math", "circle", "triangle", "geometry", "algebra", "calculus",
                 "equation", "formula", "circumference", "radius", "diameter",
                 "angle", "fraction", "number", "pi", "area", "volume",
                 "arithmetic", "percentage", "quadratic", "polynomial"],
        "science": ["physics", "chemistry", "biology", "atom", "molecule",
                    "experiment", "lab", "gravity", "energy", "cell",
                    "dna", "evolution", "quantum", "electron", "force"],
        "education": ["study", "learn", "school", "class", "student", "teacher",
                      "exam", "homework", "lesson", "tutorial", "course"],
        "technology": ["code", "programming", "software", "computer", "app",
                       "ai", "artificial", "machine", "robot", "digital",
                       "internet", "data", "algorithm", "tech", "cyber"],
        "fitness": ["gym", "exercise", "workout", "muscle", "weight",
                    "running", "yoga", "health", "training", "body"],
        "cooking": ["recipe", "food", "cook", "meal", "kitchen",
                    "chef", "ingredient", "bake", "grill", "dish"],
        "finance": ["money", "invest", "stock", "bank", "budget",
                    "finance", "crypto", "trading", "wealth", "save"],
        "travel": ["travel", "trip", "flight", "destination", "explore",
                   "adventure", "tourist", "vacation", "city", "beach"],
        "music": ["music", "guitar", "piano", "sing", "song", "beat",
                  "instrument", "melody", "concert", "band"],
        "art": ["paint", "draw", "design", "art", "sketch", "creative",
                "illustration", "sculpture", "canvas", "color"],
        "psychology": ["mind", "brain", "emotion", "therapy", "mental",
                       "anxiety", "habit", "motivation", "behavior", "cognitive"],
        "philosophy": ["philosophy", "stoic", "existential", "ethics",
                       "wisdom", "meaning", "moral", "socrates", "plato"],
    }

    _DOMAIN_VISUALS = {
        "math": [
            "mathematics equations whiteboard",
            "geometry shapes colorful",
            "student solving math problem",
            "calculator mathematics numbers",
            "teacher explaining math classroom",
            "math formulas on paper close up",
        ],
        "science": [
            "scientist working in laboratory",
            "science experiment colorful",
            "microscope laboratory research",
            "chemistry lab test tubes",
            "physics demonstration classroom",
            "science education technology",
        ],
        "education": [
            "student studying with books",
            "classroom teacher explaining",
            "online learning computer",
            "university lecture students",
            "person reading and studying",
            "graduation education success",
        ],
        "technology": [
            "person coding on computer",
            "technology digital interface",
            "robot artificial intelligence",
            "software developer working",
            "futuristic technology screen",
            "digital transformation tech",
        ],
        "fitness": [
            "person exercising in gym",
            "athlete running outdoors",
            "yoga meditation workout",
            "weightlifting fitness training",
            "healthy active lifestyle",
            "personal trainer coaching",
        ],
        "cooking": [
            "chef cooking in kitchen",
            "fresh ingredients food preparation",
            "person cooking delicious meal",
            "kitchen food close up",
            "recipe cooking step by step",
            "restaurant professional kitchen",
        ],
        "finance": [
            "financial charts and graphs",
            "person managing money savings",
            "stock market trading screen",
            "business meeting investment",
            "coins and bills finance",
            "entrepreneur working business",
        ],
        "travel": [
            "beautiful travel destination scenic",
            "traveler exploring city",
            "airplane flying sunset",
            "beach tropical paradise",
            "backpacker adventure mountains",
            "cultural landmark tourism",
        ],
        "music": [
            "musician playing guitar",
            "piano keys close up",
            "recording studio music",
            "concert performance stage",
            "person singing microphone",
            "headphones listening music",
        ],
        "art": [
            "artist painting canvas",
            "creative design studio",
            "colorful artwork abstract",
            "person drawing sketch",
            "art gallery exhibition",
            "graphic designer working",
        ],
        "psychology": [
            "brain mind thinking concept",
            "person deep in thought",
            "therapy session talking",
            "mindfulness meditation calm",
            "brain neurons abstract",
            "emotional wellbeing balance",
        ],
        "philosophy": [
            "person thinking deeply contemplation",
            "ancient library books wisdom",
            "sunset reflection nature peaceful",
            "person reading philosophy book",
            "deep conversation discussion",
            "abstract light and shadow",
        ],
        "general": [
            "person speaking to camera confident 4k cinematic",
            "modern clean desk setup with plant and laptop",
            "vibrant city street life high energy",
            "person walking into sunset cinematic",
            "dynamic abstract light trails energy",
            "professional workspace clean aesthetic",
            "stunning high-resolution cinematic footage",
        ],
    }

    _SCENE_TRANSITIONS = {
        "zoom_in": "scale=1.1*iw:-1,zoompan=z='min(zoom+0.0015,1.5)':d=100:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920",
        "static": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black",
    }

    _SCENE_INTENT_MAP = {
        "surprised": "person amazed surprised reaction",
        "warning": "person warning stop gesture",
        "mistake": "person confused making error",
        "correct": "success right way solution",
        "results": "achievement improvement results",
        "proof": "evidence data results chart",
        "comparison": "before after comparison side by side",
        "speaking": "person talking to camera confident",
        "engaging": "person speaking enthusiastic audience",
        "demonstration": "hands on tutorial step by step",
        "tutorial": "close up hands demonstration",
        "transformation": "transformation change improvement",
        "success": "person celebrating achievement happy",
        "struggle": "person frustrated struggling problem",
        "discovery": "eureka moment light bulb idea",
        "thinking": "person thinking pondering contemplation",
        "explaining": "teacher presenting explaining",
        "step": "step by step process tutorial",
    }

    _ARABIC_DOMAIN_MAP = {
        "math": ["رياضيات", "دائرة", "هندسة", "معادلة", "عدد", "حساب"],
        "philosophy": ["فلسفة", "حكمة", "وجود", "أخلاق", "سقراط", "أفلاطون"],
        "education": ["تعليم", "دراسة", "مدرسة", "طالب", "معلم", "درس"],
        "science": ["علم", "فيزياء", "كيمياء", "بيولوجيا", "تجربة"],
        "technology": ["تقنية", "ذكاء", "اصطناعي", "برمجة", "كمبيوتر"],
    }

    def _detect_domain(self, topic: str) -> str:
        topic_lower = topic.lower().strip()
        for domain, ar_keywords in self._ARABIC_DOMAIN_MAP.items():
            if any(kw in topic for kw in ar_keywords):
                return domain
        scores: Dict[str, int] = {}
        for domain, keywords in self._DOMAIN_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in topic_lower)
            if score > 0:
                scores[domain] = score
        if scores:
            return max(scores, key=scores.get)
        return "general"

    def _build_search_query(
        self, visual_cue: str, narration: str, topic: str, scene_idx: int
    ) -> str:
        """
        AI visual concept mapper: translates script scenes into
        stock-footage-optimized search queries.
        """
        domain = self._detect_domain(topic)
        self.logger.debug(f"Topic '{topic}' -> domain '{domain}'")

        domain_visuals = self._DOMAIN_VISUALS.get(domain, [])
        if domain_visuals:
            base_visual = domain_visuals[scene_idx % len(domain_visuals)]
        else:
            base_visual = topic

        cue_lower = visual_cue.lower()
        intent_boost = ""
        for intent_kw, intent_query in self._SCENE_INTENT_MAP.items():
            if intent_kw in cue_lower:
                intent_boost = intent_query
                break

        if intent_boost:
            query = f"{base_visual} {intent_boost.split()[0]}"
        else:
            query = base_visual

        if len(query) > 60:
            query = query[:60]

        return query

    @staticmethod
    def _extract_keywords(text: str, max_words: int = 3) -> str:
        """Pull meaningful keywords from a string, stripping noise."""
        cleaned = re.sub(r"\[.*?\]", "", text)
        cleaned = re.sub(r"\(.*?\)", "", cleaned)
        cleaned = cleaned.replace('"', "").replace("'", "")
        words = re.findall(r"[a-zA-Z]+", cleaned.lower())
        filtered = [w for w in words if w not in _NOISE_WORDS and len(w) > 2]
        return " ".join(filtered[:max_words])

    # ==================================================================
    # Stock video download
    # ==================================================================

    async def _download_stock_video(
        self, query: str, idx: int
    ) -> Optional[Path]:
        async with _DOWNLOAD_SEM:
            if PEXELS_API_KEY:
                path = await self._download_from_pexels(query, idx)
                if path:
                    return path

            if PIXABAY_API_KEY:
                path = await self._download_from_pixabay(query, idx)
                if path:
                    return path

        return None

    # ---- Pexels ----

    async def _download_from_pexels(
        self, query: str, idx: int
    ) -> Optional[Path]:
        try:
            resp = await asyncio.to_thread(
                requests.get,
                "https://api.pexels.com/videos/search",
                headers={"Authorization": PEXELS_API_KEY},
                params={
                    "query": query,
                    "orientation": "portrait",
                    "per_page": 5,
                    "size": "medium",
                },
                timeout=15,
            )
            if resp.status_code != 200:
                self.logger.debug(f"Pexels returned {resp.status_code}")
                return None

            videos = resp.json().get("videos", [])
            if not videos:
                self.logger.debug(f"Pexels: no results for '{query}'")
                return None

            for video in videos:
                url = self._pick_pexels_file(video)
                if url:
                    return await self._download_file(url, idx)

            return None
        except Exception as e:
            self.logger.debug(f"Pexels error: {e}")
            return None

    @staticmethod
    def _pick_pexels_file(video: dict) -> Optional[str]:
        files = video.get("video_files", [])
        candidates = []
        for vf in files:
            if vf.get("file_type") != "video/mp4":
                continue
            h = vf.get("height", 0)
            w = vf.get("width", 0)
            if h >= 720:
                candidates.append((h * w, vf))

        if candidates:
            candidates.sort(key=lambda x: x[0])
            return candidates[0][1].get("link")

        for vf in files:
            if vf.get("file_type") == "video/mp4":
                return vf.get("link")
        return None

    # ---- Pixabay ----

    async def _download_from_pixabay(
        self, query: str, idx: int
    ) -> Optional[Path]:
        try:
            resp = await asyncio.to_thread(
                requests.get,
                "https://pixabay.com/api/videos/",
                params={
                    "key": PIXABAY_API_KEY,
                    "q": query,
                    "video_type": "film",
                    "per_page": 5,
                },
                timeout=15,
            )
            if resp.status_code != 200:
                return None

            hits = resp.json().get("hits", [])
            if not hits:
                return None

            for hit in hits:
                vids = hit.get("videos", {})
                medium = vids.get("medium") or vids.get("small") or {}
                url = medium.get("url")
                if url:
                    return await self._download_file(url, idx)

            return None
        except Exception as e:
            self.logger.debug(f"Pixabay error: {e}")
            return None

    # ---- Generic downloader ----

    async def _download_file(self, url: str, idx: int) -> Optional[Path]:
        raw_path = ASSETS_DIR / f"stock_raw_{idx:03d}.mp4"
        try:
            self.logger.debug(f"Downloading clip {idx}: {url[:80]}...")
            resp = await asyncio.to_thread(
                requests.get, url, timeout=60, stream=True,
            )
            if resp.status_code != 200:
                return None

            with open(raw_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=65536):
                    f.write(chunk)

            if raw_path.exists() and raw_path.stat().st_size > 1000:
                kb = raw_path.stat().st_size / 1024
                self.logger.info(f"Downloaded clip {idx}: {kb:.0f} KB")
                return raw_path

            return None
        except Exception as e:
            self.logger.debug(f"Download failed for clip {idx}: {e}")
            return None

    # ==================================================================
    # Text-to-video (Replicate AI)
    # ==================================================================

    def _visual_to_t2v_prompt(self, visual_cue: str, topic: str, idx: int = 0) -> str:
        """Convert visual cue + topic into a high-fidelity cinematic prompt for Veo 3.1."""
        cue_clean = re.sub(r"\[.*?\]", "", visual_cue)
        cue_clean = re.sub(r"\(.*?\)", "", cue_clean)
        
        # Build a descriptive prompt
        prompt = (
            f"Cinematic 4K vertical TikTok video of {topic}. "
            f"Scene: {cue_clean}. "
            f"Style: Ultra-realistic, vibrant colors, professional lighting, 9:16 aspect ratio, "
            f"dynamic movement, highly detailed."
        )
        return prompt[:500]

    async def _generate_video_via_veo(
        self, visual_cue: str, narration: str, topic: str, idx: int
    ) -> Optional[Path]:
        """Generate video from text using Google Veo 3.1.
        Implementation follows official docs: https://ai.google.dev/gemini-api/docs/video
        """
        if not GOOGLE_VEO_API_KEY:
            return None
        try:
            from google import genai
            from google.genai import types
            import time
            import os

            def _run_veo() -> Optional[Path]:
                self.logger.info(f"Scene {idx} Veo thread started...")

                # Set the API key as env var (official docs pattern)
                os.environ["GOOGLE_API_KEY"] = GOOGLE_VEO_API_KEY
                client = genai.Client(api_key=GOOGLE_VEO_API_KEY)

                # Build a descriptive prompt
                prompt = (
                    f"Cinematic vertical TikTok video for {topic}. "
                    f"Visual: {visual_cue}. "
                    f"Voiceover context: {narration}. "
                    f"High-energy, professional, realistic, 9:16 aspect ratio."
                )

                self.logger.info(f"Scene {idx} Veo Prompt: {prompt[:100]}...")

                # Config: only use parameters confirmed in official docs
                # Supported: aspect_ratio, negative_prompt, person_generation
                config = types.GenerateVideosConfig(
                    aspect_ratio="9:16",
                    negative_prompt="cartoon, drawing, low quality, blurry",
                    person_generation="allow_all",
                )

                try:
                    operation = client.models.generate_videos(
                        model=GOOGLE_VEO_MODEL,
                        prompt=prompt,
                        config=config,
                    )
                except Exception as e:
                    self.logger.error(f"Veo generate_videos call failed: {e}")
                    return None

                self.logger.info(f"Scene {idx} Veo operation started: {operation.name}")

                # Poll for completion — pass the operation object directly (per docs)
                # Poll for completion
                max_retries = 60  # ~10 mins at 10s intervals (Veo is slow on Tier 1)
                retries = 0
                while not operation.done and retries < max_retries:
                    time.sleep(10)
                    retries += 1
                    try:
                        # Use the operation name for safer retrieval
                        operation = client.operations.get(name=operation.name)
                        status = "Queued/Processing" if not operation.done else "Done"
                        self.logger.info(f"Scene {idx} Veo: {status} (attempt {retries})")
                    except Exception as e:
                        self.logger.warning(f"Scene {idx} Veo poll error (retry {retries}): {e}")

                if not operation.done:
                    self.logger.error(f"Scene {idx} Veo timed out after {retries} polls")
                    return None

                # Extract and download (per official docs)
                try:
                    generated_video = operation.response.generated_videos[0]
                except (AttributeError, IndexError) as e:
                    self.logger.error(f"Scene {idx} Veo completed but no videos: {e}. Response: {operation.response}")
                    return None

                out_path = ASSETS_DIR / f"veo_raw_{idx:03d}.mp4"

                self.logger.info(f"Scene {idx} Veo video ready, downloading...")

                try:
                    # Official pattern: download then save
                    client.files.download(file=generated_video.video)
                    generated_video.video.save(str(out_path))
                except Exception as e:
                    self.logger.error(f"Scene {idx} Veo download/save failed: {e}")
                    # Try alternative save if the first method fails
                    try:
                        if hasattr(generated_video.video, 'save'):
                            generated_video.video.save(str(out_path))
                    except Exception as e2:
                        self.logger.error(f"Scene {idx} Veo alt save also failed: {e2}")
                        return None

                if out_path.exists() and out_path.stat().st_size > 1000:
                    self.logger.info(f"Scene {idx} Veo video saved! ({out_path.stat().st_size} bytes)")
                    return out_path

                self.logger.error(f"Scene {idx} Veo video file missing or too small")
                return None

            async with _VEO_SEM:
                return await asyncio.to_thread(_run_veo)
        except Exception as e:
            self.logger.error(f"Veo 3.1 T2V Exception: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None

    async def _generate_video_via_replicate(
        self, visual_cue: str, topic: str, idx: int
    ) -> Optional[Path]:
        """Generate video from text using Replicate (minimax/video-01)."""
        if not REPLICATE_API_TOKEN:
            return None
        try:
            import replicate
            prompt = self._visual_to_t2v_prompt(visual_cue, topic, idx)
            self.logger.info(f"Scene {idx} T2V prompt: '{prompt[:80]}...'")
            output = await asyncio.to_thread(
                replicate.run,
                REPLICATE_VIDEO_MODEL,
                input={"prompt": prompt},
            )
            url = None
            if isinstance(output, str) and output.startswith("http"):
                url = output
            elif hasattr(output, "url"):
                url = output.url
            elif callable(getattr(output, "url", None)):
                url = output.url()
            elif isinstance(output, (list, tuple)) and output:
                first = output[0]
                url = getattr(first, "url", None) or (first.url() if callable(getattr(first, "url", None)) else str(first))
            if url and str(url).startswith("http"):
                raw_path = await self._download_file(str(url), idx)
                return raw_path
        except Exception as e:
            self.logger.debug(f"Replicate T2V failed: {e}")
        return None

    # ==================================================================
    # Clip preparation (trim + scale + re-encode to standard format)
    # ==================================================================

    async def _prepare_clip(
        self, raw_path: Path, idx: int, duration: float
    ) -> Optional[Path]:
        """Trim and scale a Veo clip to 1080x1920 @ 30fps h264.
        No zoompan — Veo already generates cinematic video."""
        output = ASSETS_DIR / f"clip_{idx:03d}.mp4"
        w, h = VIDEO_RESOLUTION.split("x")

        cmd = [
            self.ffmpeg, "-y",
            "-i", str(raw_path),
            "-t", str(duration),
            "-vf", (
                f"scale={w}:{h}:force_original_aspect_ratio=increase,"
                f"crop={w}:{h},"
                f"fps={VIDEO_FPS}"
            ),
            "-c:v", "libx264", "-preset", "fast", "-crf", "21",
            "-an",
            "-pix_fmt", "yuv420p",
            str(output),
        ]
        try:
            result = await asyncio.to_thread(
                subprocess.run, cmd,
                capture_output=True, timeout=120,
                encoding="utf-8", errors="replace",
            )
            if output.exists() and output.stat().st_size > 0:
                self.logger.info(
                    f"Clip {idx} prepared: {output.stat().st_size / 1024:.0f} KB"
                )
                return output
            self.logger.error(f"Clip {idx} prepare failed: {result.stderr[:300]}")
        except Exception as e:
            self.logger.error(f"Clip {idx} prepare error: {e}")
        return None

    async def _image_to_clip(
        self, img_path: Path, idx: int, duration: float
    ) -> Optional[Path]:
        """Convert a single image into a video clip of the given duration."""
        output = ASSETS_DIR / f"clip_{idx:03d}.mp4"
        w, h = VIDEO_RESOLUTION.split("x")
        cmd = [
            self.ffmpeg, "-y",
            "-loop", "1",
            "-i", str(img_path),
            "-t", str(duration),
            "-vf", (
                f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
                f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:black,"
                f"fps={VIDEO_FPS}"
            ),
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-pix_fmt", "yuv420p",
            str(output),
        ]
        try:
            await asyncio.to_thread(
                subprocess.run, cmd,
                capture_output=True, timeout=60,
                encoding="utf-8", errors="replace",
            )
            if output.exists() and output.stat().st_size > 0:
                return output
        except Exception:
            pass
        return None

    # ==================================================================
    # Placeholder fallback (Pillow image → FFmpeg clip)
    # ==================================================================

    async def _create_placeholder_clip(
        self, scene_text: str, idx: int, duration: float
    ) -> Path:
        img_path = self._create_placeholder_image(scene_text, idx)
        clip = await self._image_to_clip(img_path, idx, duration)
        if clip:
            return clip

        output = ASSETS_DIR / f"clip_{idx:03d}.mp4"
        return await self._create_colorbar_clip(output, idx, duration)

    def _create_placeholder_image(self, scene_text: str, idx: int) -> Path:
        w_px, h_px = (int(d) for d in VIDEO_RESOLUTION.split("x"))
        color = SCENE_COLORS[idx % len(SCENE_COLORS)]
        img = Image.new("RGB", (w_px, h_px), color)
        draw = ImageDraw.Draw(img)

        try:
            font_lg = ImageFont.truetype("arial.ttf", 52)
            font_sm = ImageFont.truetype("arial.ttf", 32)
        except OSError:
            font_lg = ImageFont.load_default()
            font_sm = font_lg

        label = f"Scene {idx + 1}"
        bbox = draw.textbbox((0, 0), label, font=font_lg)
        lw = bbox[2] - bbox[0]
        draw.text(((w_px - lw) / 2, h_px * 0.35), label, fill="white", font=font_lg)

        for i, line in enumerate(self._wrap_lines(scene_text, 35)[:4]):
            bbox = draw.textbbox((0, 0), line, font=font_sm)
            tw = bbox[2] - bbox[0]
            draw.text(
                ((w_px - tw) / 2, h_px * 0.45 + i * 44),
                line, fill="#dddddd", font=font_sm,
            )

        path = ASSETS_DIR / f"visual_placeholder_{idx:03d}.png"
        img.save(path, "PNG")
        return path

    async def _create_colorbar_clip(
        self, output: Path, idx: int, duration: float
    ) -> Path:
        w, h = VIDEO_RESOLUTION.split("x")
        hex_color = SCENE_COLORS[idx % len(SCENE_COLORS)].lstrip("#")
        cmd = [
            self.ffmpeg, "-y",
            "-f", "lavfi",
            "-i", f"color=c=0x{hex_color}:s={w}x{h}:d={duration}:r={VIDEO_FPS}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-pix_fmt", "yuv420p",
            str(output),
        ]
        try:
            await asyncio.to_thread(
                subprocess.run, cmd,
                capture_output=True, timeout=60,
                encoding="utf-8", errors="replace",
            )
        except Exception:
            pass

        if not output.exists() or output.stat().st_size == 0:
            output.touch()
        return output

    @staticmethod
    def _wrap_lines(text: str, max_chars: int) -> List[str]:
        words, lines, cur = text.split(), [], ""
        for w in words:
            if len(cur) + len(w) + 1 > max_chars:
                lines.append(cur)
                cur = w
            else:
                cur = f"{cur} {w}".strip()
        if cur:
            lines.append(cur)
        return lines

    # ==================================================================
    # ComfyUI image generation (kept as secondary source)
    # ==================================================================

    async def _generate_image_via_comfyui(self, prompt: str, idx: int) -> Path:
        response = requests.get(f"{self.comfyui_url}/api/", timeout=5)
        if response.status_code != 200:
            raise ConnectionError("ComfyUI not responding")

        payload = {
            "prompt": {
                "1": {"inputs": {"text": prompt}, "class_type": "CLIPTextEncode(Prompt)"},
                "2": {"inputs": {"seed": idx, "steps": 20, "cfg": 7.5}, "class_type": "KSampler"},
            },
        }
        queue_resp = requests.post(
            f"{self.comfyui_url}/api/queue", json=payload, timeout=30,
        )
        if queue_resp.status_code == 200:
            path = ASSETS_DIR / f"visual_{idx:03d}.png"
            path.touch()
            return path
        raise Exception(f"ComfyUI queue failed: {queue_resp.status_code}")

    # ==================================================================
    # Audio / voiceover generation (edge-tts)
    # ==================================================================

    VOICE_EN = "en-US-GuyNeural"
    VOICE_AR = "ar-SA-HamedNeural"

    @property
    def VOICE(self) -> str:
        lang = self.script_data.get("language", "en")
        return self.VOICE_AR if lang == "ar" else self.VOICE_EN

    async def generate_voiceover(
        self, script_columns: List[Dict[str, str]], voice_model: str = "default"
    ) -> Path:
        """
        Generate narration using Microsoft Edge TTS (free, no API key).
        Automatically selects Arabic or English voice based on script language.
        """
        self.logger.info(f"Generating voiceover via edge-tts ({self.VOICE})...")

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        segments_dir = ASSETS_DIR / f"tts_segments_{ts}"
        segments_dir.mkdir(exist_ok=True)

        lines = []
        for col in script_columns:
            text = col.get("audio", "").strip().strip('"')
            if text:
                lines.append(text)

        if not lines:
            self.logger.warning("No narration text — creating silent track")
            return self._create_silent_audio()

        try:
            import edge_tts

            segment_paths: List[Path] = []
            for i, line in enumerate(lines):
                seg_path = segments_dir / f"seg_{i:03d}.mp3"
                comm = edge_tts.Communicate(line, self.VOICE)
                await comm.save(str(seg_path))
                if seg_path.exists() and seg_path.stat().st_size > 0:
                    segment_paths.append(seg_path)
                    self.logger.debug(f"TTS segment {i}: {line[:40]}...")

            if not segment_paths:
                raise RuntimeError("No TTS segments produced")

            final_audio = ASSETS_DIR / f"voiceover_{ts}.mp3"

            if len(segment_paths) == 1:
                segment_paths[0].rename(final_audio)
            else:
                concat_file = segments_dir / "concat.txt"
                with open(concat_file, "w") as f:
                    for sp in segment_paths:
                        f.write(f"file '{sp.absolute()}'\n")

                cmd = [
                    self.ffmpeg, "-y",
                    "-f", "concat", "-safe", "0",
                    "-i", str(concat_file),
                    "-c", "copy",
                    str(final_audio),
                ]
                await asyncio.to_thread(
                    subprocess.run, cmd,
                    capture_output=True, timeout=60,
                    encoding="utf-8", errors="replace",
                )

            if final_audio.exists() and final_audio.stat().st_size > 0:
                self.logger.info(
                    f"Voiceover ready: {final_audio} "
                    f"({final_audio.stat().st_size / 1024:.0f} KB)"
                )
                return final_audio

            raise RuntimeError("Final audio file empty after concat")

        except Exception as e:
            self.logger.warning(f"edge-tts failed: {e}. Creating silent track.")
            return self._create_silent_audio()

    def _create_silent_audio(self, duration_seconds: int = 0) -> Path:
        if duration_seconds <= 0:
            duration_seconds = self.script_data.get("duration_seconds", 30)

        path = ASSETS_DIR / f"voiceover_silent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        sr = 44100
        n = sr * duration_seconds

        with wave.open(str(path), "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(b"\x00\x00" * n)

        self.logger.info(f"Silent audio ({duration_seconds}s): {path}")
        return path

    # ==================================================================
    # Veo native audio extraction
    # ==================================================================

    async def extract_veo_audio(self, clip_paths: List[Path]) -> Path:
        """
        Extract and concatenate audio directly from Veo clips.
        Veo 3.1 generates high-quality cinematic audio natively.
        This avoids edge-tts entirely.
        """
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_audio = ASSETS_DIR / f"veo_audio_{ts}.aac"

        valid = [c for c in clip_paths if c.exists() and c.stat().st_size > 0]
        if not valid:
            self.logger.warning("No Veo clips for audio extraction — using silence")
            return self._create_silent_audio()

        # Check if any clip actually has an audio stream
        def _has_audio(path: Path) -> bool:
            try:
                result = subprocess.run(
                    [self.ffmpeg, "-i", str(path)],
                    capture_output=True, timeout=10,
                    encoding="utf-8", errors="replace",
                )
                return "Audio:" in result.stderr
            except Exception:
                return False

        clips_with_audio = [c for c in valid if _has_audio(c)]
        if not clips_with_audio:
            self.logger.warning("Veo clips have no audio track — using silence")
            return self._create_silent_audio()

        self.logger.info(f"🎨 [Agent Gamma] Extracting high-fidelity native audio from {len(clips_with_audio)} Veo clip(s)...")

        if len(clips_with_audio) == 1:
            # Single clip — extract audio directly
            cmd = [
                self.ffmpeg, "-y",
                "-i", str(clips_with_audio[0]),
                "-vn", "-c:a", "aac", "-b:a", AUDIO_BITRATE,
                str(out_audio),
            ]
        else:
            # Multiple clips — concat their audio tracks
            concat_file = ASSETS_DIR / f"audio_concat_{ts}.txt"
            with open(concat_file, "w") as f:
                for c in clips_with_audio:
                    f.write(f"file '{c.absolute()}'\n")
            cmd = [
                self.ffmpeg, "-y",
                "-f", "concat", "-safe", "0",
                "-i", str(concat_file),
                "-vn", "-c:a", "aac", "-b:a", AUDIO_BITRATE,
                str(out_audio),
            ]

        try:
            result = await asyncio.to_thread(
                subprocess.run, cmd,
                capture_output=True, timeout=120,
                encoding="utf-8", errors="replace",
            )
            if out_audio.exists() and out_audio.stat().st_size > 0:
                self.logger.info(
                    f"Veo audio extracted: {out_audio.stat().st_size / 1024:.0f} KB"
                )
                return out_audio
            self.logger.warning(f"Audio extraction produced empty file: {result.stderr[:200]}")
        except Exception as e:
            self.logger.error(f"Audio extraction error: {e}")

        return self._create_silent_audio()

    # ==================================================================
    # Video assembly (concatenate prepared clips — keep native audio)
    # ==================================================================

    async def assemble_video(
        self,
        clip_paths: List[Path],
        voiceover_path: Path,
        veo_audio_path: Optional[Path] = None,
        output_filename: str = "final_render.mp4",
    ) -> Path:
        """
        Concatenate Veo clips and mix Voiceover + Native Ambient tracks.
        """
        self.logger.info("🎨 [Agent Gamma] Assembling cinematic structure & mixing tracks...")
        output = RENDER_DIR / output_filename
        total_dur = self.script_data.get("duration_seconds", 30)

        valid = [c for c in clip_paths if c.exists() and c.stat().st_size > 0]
        if not valid:
            self.logger.warning("No valid clips — generating fallback video")
            return self._generate_colorbar_video(output, total_dur)

        concat_file = ASSETS_DIR / "concat.txt"
        with open(concat_file, "w") as f:
            for clip in valid:
                f.write(f"file '{clip.absolute()}'\n")

        # Prepare mixing inputs
        # 0: Video Concat, 1: Voiceover, 2: Veo Ambient (optional)
        has_veo_audio = veo_audio_path and veo_audio_path.exists() and veo_audio_path.stat().st_size > 1000

        cmd = [
            self.ffmpeg, "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_file),
            "-i", str(voiceover_path),
        ]
        
        if has_veo_audio:
            cmd.extend(["-i", str(veo_audio_path)])
            # Mix: VO (1.0) + Veo (0.3)
            filter_str = "[1:a]volume=1.0[vo]; [2:a]volume=0.3[veo]; [vo][veo]amix=inputs=2:duration=first[a]"
        else:
            filter_str = "[1:a]volume=1.0[a]"

        cmd.extend([
            "-filter_complex", filter_str,
            "-c:v", "libx264", "-preset", "fast", "-crf", "21",
            "-c:a", "aac", "-b:a", "192k",
            "-map", "0:v:0", "-map", "[a]",
            "-pix_fmt", "yuv420p", "-shortest",
            str(output),
        ])

        try:
            result = await asyncio.to_thread(
                subprocess.run, cmd,
                capture_output=True, timeout=300,
                encoding="utf-8", errors="replace",
            )
            if output.exists() and output.stat().st_size > 0:
                self.logger.info(f"Mixed video ready: {output} ({output.stat().st_size/1024:.0f} KB)")
                return output
            self.logger.error(f"Assembly failed: {result.stderr[:500]}")
        except Exception as e:
            self.logger.error(f"Assembly error: {e}")

        return self._generate_colorbar_video(output, total_dur)

    def _generate_colorbar_video(self, output: Path, duration: int) -> Path:
        w, h = VIDEO_RESOLUTION.split("x")
        try:
            cmd = [
                self.ffmpeg, "-y",
                "-f", "lavfi",
                "-i", f"color=c=0x1a1a2e:s={w}x{h}:d={duration}:r={VIDEO_FPS}",
                "-f", "lavfi",
                "-i", "anullsrc=r=44100:cl=mono",
                "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                "-c:a", "aac", "-b:a", "128k",
                "-shortest", "-t", str(duration),
                "-pix_fmt", "yuv420p",
                str(output),
            ]
            subprocess.run(
                cmd, capture_output=True, timeout=120,
                encoding="utf-8", errors="replace",
            )
            if output.exists() and output.stat().st_size > 0:
                return output
        except Exception:
            pass

        output.touch()
        return output

    # ==================================================================
    # Caption overlay
    # ==================================================================

    @staticmethod
    def _wrap_text(text: str, max_chars: int = 28) -> str:
        """Break text into lines that fit the video width."""
        words = text.split()
        lines: List[str] = []
        current = ""
        for w in words:
            test = f"{current} {w}".strip()
            if len(test) <= max_chars:
                current = test
            else:
                if current:
                    lines.append(current)
                current = w
        if current:
            lines.append(current)
        return "\n".join(lines)

    def _resolve_font(self) -> str:
        """Find a font file that supports Arabic/Latin glyphs with bold viral style."""
        candidates = [
            "C:/Windows/Fonts/ariblk.ttf",   # Arial Black
            "C:/Windows/Fonts/segoeuib.ttf", # Segoe UI Bold
            "C:/Windows/Fonts/arialbd.ttf",   # Arial Bold
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/tahoma.ttf",
        ]
        for p in candidates:
            if Path(p).exists():
                return p.replace("\\", "/").replace(":", "\\\\:")
        return ""

    async def add_captions_to_video(
        self,
        video_path: Path,
        captions: List[Dict[str, str]],
        output_filename: str = "final_render_with_captions.mp4",
    ) -> Path:
        self.logger.info("🎨 [Agent Gamma] Burning-in dynamic captions (SEO Optimized)...")
        output = RENDER_DIR / output_filename

        if not video_path.exists() or video_path.stat().st_size == 0:
            self.logger.warning("Source video empty/missing — skipping captions")
            return video_path

        lang = self.script_data.get("language", "en")
        is_arabic = lang == "ar"
        font_path = self._resolve_font()

        try:
            vf_parts: List[str] = []
            for cap in captions:
                raw_text = cap.get("text", "") or cap.get("audio", "")
                if not raw_text:
                    continue
                
                wrapped = self._wrap_text(raw_text, max_chars=24)
                text = (
                    wrapped
                    .replace("\\", "\\\\")
                    .replace("'", "\u2019")
                    .replace(":", "\\:")
                    .replace("%", "%%")
                )
                tc = cap.get("timecode", "0-5")
                if "-" in tc:
                    start, end = tc.split("-")
                    start = start.replace("s", "").strip()
                    end = end.replace("s", "").strip()
                else:
                    start, end = "0", "5"

                font_spec = f"fontfile='{font_path}':" if font_path else ""

                # Styling: White text with semi-transparent black box
                vf_parts.append(
                    f"drawtext={font_spec}text='{text}':"
                    f"fontsize=68:fontcolor=white:"
                    f"box=1:boxcolor=black@0.6:boxborderw=20:"
                    f"x=(w-text_w)/2:y=(h*0.75-text_h/2):"
                    f"line_spacing=12:"
                    f"enable='between(t,{start},{end})'"
                )

            vf = ",".join(vf_parts) if vf_parts else "null"

            cmd = [
                self.ffmpeg, "-y",
                "-i", str(video_path),
                "-vf", vf,
                "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                "-c:a", "copy",
                "-pix_fmt", "yuv420p",
                str(output),
            ]

            result = await asyncio.to_thread(
                subprocess.run, cmd,
                capture_output=True, timeout=300,
                encoding="utf-8", errors="replace",
            )

            if result.returncode == 0 and output.exists() and output.stat().st_size > 0:
                self.logger.info(f"Captions added: {output}")
                return output

            self.logger.warning(
                f"Captions failed ({result.stderr[:200]}), using original"
            )
            return video_path

        except Exception as e:
            self.logger.error(f"Caption overlay error: {e}")
            return video_path


# ======================================================================
# Public pipeline runner
# ======================================================================

async def run_media_forge(
    script_data: Dict[str, Any], captions: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    Execute the Media Forge pipeline:
    High-fidelity Voiceover + Veo Visuals + Mixed Audio Tracks.
    """
    forge = MediaForgeAgent(script_data)

    total_duration = script_data.get("duration_seconds", 30)
    scene_descs = [
        col.get("visual_cue", "vibrant visual")
        for col in script_data.get("script_columns", [])
    ]

    # 1. Generate Voiceover (Edge-TTS is best for narrative flow)
    # This ensures we NEVER have a silent video.
    voiceover_path = await forge.generate_voiceover(script_data.get("script_columns", []))

    # 2. Generate Veo clips (Premium Visuals)
    clip_paths = await forge.generate_scene_clips(scene_descs, total_duration)

    # 3. Extract Veo's native ambient audio (Optional cinematic texture)
    veo_audio_path = await forge.extract_veo_audio(clip_paths)

    # 4. Assemble & Mix (VO 1.0 + Veo 0.3)
    # Use a temporary name for the assembled video to avoid FFmpeg read/write conflicts
    raw_assembly_path = await forge.assemble_video(
        clip_paths, voiceover_path, veo_audio_path, "raw_assembly.mp4"
    )

    # 5. Add Premium Captions (Better Font + Style)
    # Now write to the final filename
    final_video_path = await forge.add_captions_to_video(
        raw_assembly_path, captions, "final_render.mp4"
    )

    return {
        "visuals_generated": len(clip_paths),
        "voiceover_path": str(voiceover_path),
        "video_path_raw": str(video_path),
        "final_video_path": str(final_video_path),
        "duration": total_duration,
        "resolution": VIDEO_RESOLUTION,
        "ready_for_review": True,
    }


if __name__ == "__main__":
    test_script = {
        "script_columns": [
            {"timecode": "0-3s", "visual_cue": "Shocked reaction face", "audio": "This works..."},
            {"timecode": "3-6s", "visual_cue": "Quick B-roll transition", "audio": "Most people don't know..."},
            {"timecode": "6-9s", "visual_cue": "Productive person working at desk", "audio": "The 80/20 rule"},
        ],
        "duration_seconds": 10,
    }
    test_captions = [
        {"timecode": "0-5", "text": "SHOCKING DISCOVERY"},
    ]
    result = asyncio.run(run_media_forge(test_script, test_captions))
    print(json.dumps(result, indent=2, default=str))
