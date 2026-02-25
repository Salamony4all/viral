"""
MAIN.PY: Viral Engine Orchestrator
Initializes and runs the complete Hunt -> Script -> Forge -> Brief pipeline
with human-in-the-loop validation before posting.
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime
from loguru import logger

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import (
    PROJECT_ROOT, REVIEW_DIR, RENDER_DIR, ASSETS_DIR, LOG_FILE
)
from config.utils import verify_infrastructure, notify_review_ready, load_latest_trends

# Import agents
from agents.agent_alpha import run_trend_hunter, TrendHunterAgent
from agents.agent_beta import run_narrative_architect, NarrativeArchitectAgent
from agents.agent_gamma import run_media_forge, MediaForgeAgent
from agents.agent_delta import run_profit_oracle, ProfitOracleAgent


logger.info("=" * 80)
logger.info("🚀 VIRAL ENGINE - ZERO API LOCAL-FIRST CONTENT AUTOMATION")
logger.info("=" * 80)
logger.info(f"Project Root: {PROJECT_ROOT}")
logger.info(f"Logs: {LOG_FILE}")


async def main(topic: str = "lifestyle_hack", auto_post: bool = False):
    """
    Main orchestration function.
    Runs complete pipeline: Hunt -> Script -> Forge -> Brief
    """
    
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 1: INFRASTRUCTURE CHECK")
    logger.info("=" * 80)
    
    # Verify local services
    infrastructure = await verify_infrastructure()
    
    if not any(infrastructure.values()):
        logger.error("⚠️  No services running. Starting degraded mode...")
        logger.info("To enable full features, start services:")
        logger.info("  - Ollama: ollama serve")
        logger.info("  - ComfyUI: python main.py (in ComfyUI directory)")
    
    # =========================================================================
    # PHASE 2: TREND HUNTING (Agent Alpha)
    # =========================================================================
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 2: TREND HUNTING 🔥")
    logger.info("=" * 80)
    logger.info("Agent Alpha is scouting TikTok & YouTube for viral opportunities...")
    
    try:
        trends_manifest = await run_trend_hunter()
        logger.success("✓ Trend Hunter complete")
        logger.info(f"  - Rising hashtags found: {len(trends_manifest.get('tiktok_trends', []))}")
        logger.info(f"  - YouTube formats analyzed: {len(trends_manifest.get('youtube_formats', []))}")
        logger.info(f"  - Niche breakouts identified: {len(trends_manifest.get('niche_breakouts', []))}")
    except Exception as e:
        logger.error(f"Trend Hunter failed: {e}")
        trends_manifest = load_latest_trends() or {
            "seo_keywords": ["viral", "trending"],
            "hook_patterns": [],
            "niche_breakouts": [],
        }
    
    # =========================================================================
    # PHASE 3: SCRIPT GENERATION (Agent Beta)
    # =========================================================================
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 3: NARRATIVE ARCHITECTURE 📝")
    logger.info("=" * 80)
    logger.info(f"Agent Beta is crafting viral hooks for: {topic}")
    
    try:
        script_result = await run_narrative_architect(trends_manifest, topic)
        main_script = script_result.get("main_script", {})
        variations = script_result.get("variations", [])
        captions = script_result.get("captions", [])
        
        logger.success("✓ Narrative Architect complete")
        logger.info(f"  - Main script generated: {len(main_script.get('script_columns', []))} scenes")
        logger.info(f"  - Script variations: {len(variations)}")
        logger.info(f"  - Captions auto-generated: {len(captions)}")
        
        # Show main script preview
        logger.info("\n📋 MAIN SCRIPT PREVIEW:")
        for col in main_script.get("script_columns", [])[:3]:
            logger.info(f"  [{col.get('timecode')}] {col.get('visual_cue')} → {col.get('audio')[:40]}...")
    
    except Exception as e:
        logger.error(f"Narrative Architect failed: {e}")
        main_script = {}
        variations = []
        captions = []
    
    # =========================================================================
    # PHASE 4: MEDIA GENERATION (Agent Gamma)
    # =========================================================================
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 4: MEDIA FORGE 🎬")
    logger.info("=" * 80)
    logger.info("Agent Gamma is generating visuals, audio, and assembling video...")
    
    try:
        media_result = await run_media_forge(main_script, captions)
        
        logger.success("✓ Media Forge complete")
        logger.info(f"  - Visuals generated: {media_result.get('visuals_generated', 0)} scenes")
        logger.info(f"  - Voiceover created: {media_result.get('voiceover_path', 'N/A')}")
        logger.info(f"  - Final video: {media_result.get('final_video_path', 'N/A')}")
        
        final_video_path = Path(media_result.get("final_video_path", RENDER_DIR / "final_render.mp4"))
    
    except Exception as e:
        logger.error(f"Media Forge failed: {e}")
        final_video_path = RENDER_DIR / "final_render.mp4"
        media_result = {}
    
    # =========================================================================
    # PHASE 5: MONETIZATION STRATEGY (Agent Delta)
    # =========================================================================
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 5: PROFIT ORACLE 💰")
    logger.info("=" * 80)
    logger.info("Agent Delta is identifying monetization opportunities...")
    
    try:
        profit_result = await run_profit_oracle(main_script)
        
        logger.success("✓ Profit Oracle complete")
        logger.info(f"  - Affiliate products found: {len(profit_result.get('affiliate_products', []))}")
        logger.info(f"  - TikTok Shop products: {len(profit_result.get('tiktok_shop_products', []))}")
        logger.info(f"  - CTAs generated: {len(profit_result.get('cta_strategies', []))}")
        logger.info(f"  - Profit Brief: {profit_result.get('profit_brief_path', 'N/A')}")
        
        brief_path = Path(profit_result.get("profit_brief_path", ASSETS_DIR / "PROFIT_BRIEF.md"))
        
        # Show earnings potential
        earnings = profit_result.get("estimated_earnings_potential", {})
        logger.info(f"\n💵 EARNING POTENTIAL:")
        logger.info(f"  Conservative: {earnings.get('conservative', 'N/A')}")
        logger.info(f"  Viral scenario: {earnings.get('viral', 'N/A')}")
    
    except Exception as e:
        logger.error(f"Profit Oracle failed: {e}")
        brief_path = ASSETS_DIR / "PROFIT_BRIEF.md"
        profit_result = {}
    
    # =========================================================================
    # PHASE 6: HUMAN-IN-THE-LOOP REVIEW
    # =========================================================================
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 6: READY FOR REVIEW 👤")
    logger.info("=" * 80)
    
    script_path = ASSETS_DIR / f"script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    if not script_path.exists():
        with open(script_path, "w", encoding="utf-8") as f:
            f.write("# 📝 GENERATED SCRIPT\n\n")
            for col in main_script.get("script_columns", []):
                f.write(f"**[{col.get('timecode')}]** {col.get('visual_cue')}\n")
                f.write(f"> {col.get('audio')}\n\n")
    
    notify_review_ready(final_video_path, script_path, brief_path)
    
    seo_tags = ', '.join(trends_manifest.get('seo_keywords', ['viral', 'trending'])[:3])
    logger.info(f"""
📂 REVIEW FOLDER: {REVIEW_DIR}

🎬 GENERATED ASSETS:
  1. VIDEO:        {final_video_path}
  2. SCRIPT:       {script_path}
  3. PROFIT BRIEF: {brief_path}

⚡ NEXT STEPS:
  1. Review content  →  Watch video, read brief, check script
  2. Record native 3s intro on TikTok camera
  3. Apply Green Screen effect (resets metadata, signals human creator)
  4. Compose caption  →  Hook + CTA + Hashtags: {seo_tags}
  5. Post manually during peak hours (6-10 PM), engage first 60 min
""")
    
    if auto_post:
        logger.warning("Auto-posting DISABLED by design (organic > automation)")

    # Build structured script text
    script_text = ""
    for col in main_script.get("script_columns", []):
        script_text += f"[{col.get('timecode')}]  {col.get('visual_cue')}  |  {col.get('audio')}\n"
    if not script_text:
        script_text = main_script.get("raw_content", "")

    # Read brief content from file
    brief_content = ""
    if brief_path.exists():
        brief_content = brief_path.read_text(encoding="utf-8")

    # Collect products
    products = []
    for p in profit_result.get("affiliate_products", []):
        products.append({
            "name": p.get("name", ""),
            "price": p.get("price", ""),
            "commission": p.get("commission", ""),
            "rating": p.get("rating", 0),
            "url": p.get("url", ""),
            "affiliate_network": p.get("affiliate_network", ""),
            "reason": p.get("reason", ""),
        })
    for p in profit_result.get("tiktok_shop_products", []):
        products.append({
            "name": p.get("name", ""),
            "price": p.get("price", ""),
            "commission": p.get("commission_rate", ""),
            "url": p.get("tiktok_shop_url", ""),
            "affiliate_network": "TikTok Shop",
            "reason": p.get("note", ""),
        })

    earnings = profit_result.get("estimated_earnings_potential", {})

    return {
        "status": "completed",
        "topic": topic,
        "script": script_text,
        "variations": [v.get("raw_content", "") for v in variations],
        "captions": [c.get("text", "") for c in captions],
        "video_path": str(final_video_path),
        "script_path": str(script_path),
        "brief_path": str(brief_path),
        "monetization_brief": brief_content,
        "products": products,
        "earnings_projection": {
            "conservative": earnings.get("conservative", "$1,500 - $5,000"),
            "viral": earnings.get("viral", "$20,000 - $100,000+"),
        },
        "agents_completed": {
            "alpha_trend_hunter": bool(trends_manifest),
            "beta_narrative_architect": bool(main_script),
            "gamma_media_forge": final_video_path.exists(),
            "delta_profit_oracle": brief_path.exists(),
        },
    }


def display_help():
    """Display usage information."""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                    VIRAL ENGINE - ZERO-API LOCAL FIRST                     ║
║              Automated Multi-Agent TikTok Content Generation                ║
╚════════════════════════════════════════════════════════════════════════════╝

USAGE:
    python main.py [topic] [--auto]

EXAMPLES:
    # Generate content for a lifestyle hack
    python main.py "productivity hack"
    
    # Generate content for fitness niche
    python main.py "fitness transformation"
    
    # Use default topic
    python main.py

ARGUMENTS:
    topic           Content topic (default: "lifestyle_hack")
    --auto          Skip human-in-the-loop (NOT RECOMMENDED - use 'no' for safety)

REQUIRED SERVICES (optional but recommended):
    1. Ollama LLM Server
       Download: https://ollama.ai
       Run: ollama serve
       Models: ollama pull mistral
    
    2. ComfyUI for Image Generation
       Download: https://github.com/comfyorg/ComfyUI
       Run: python main.py (in ComfyUI directory)
    
    3. FFmpeg for Video Assembly
       Windows: choco install ffmpeg
       Mac: brew install ffmpeg
       Linux: sudo apt install ffmpeg

WORKFLOW:
    Phase 1: Infrastructure Check (verify services)
    Phase 2: Trend Hunting (Agent Alpha) - scrapes TikTok & YouTube
    Phase 3: Script Generation (Agent Beta) - creates viral hooks
    Phase 4: Media Forge (Agent Gamma) - generates visuals & audio
    Phase 5: Profit Oracle (Agent Delta) - finds monetization
    Phase 6: Human Review - content ready for posting

OUTPUT:
    /workspace/review/           - Final assets ready for review
    /workspace/trends/           - Trend data (JSON)
    /workspace/assets/           - Generated media files
    /workspace/render/           - Final video output
    logs/viral_engine.log        - Detailed execution logs

ENVIRONMENT VARIABLES (.env):
    OLLAMA_BASE_URL=http://localhost:11434
    COMFYUI_BASE_URL=http://localhost:8188
    OLLAMA_MODEL=mistral
    MONETIZATION_FOCUS=affiliate  # or: shop, seo, hybrid
    TELEGRAM_BOT_TOKEN=          # optional: for notifications
    TELEGRAM_CHAT_ID=            # optional: for notifications

KEY FEATURES:
    ✓ 100% local-first (no expensive APIs)
    ✓ Human-in-the-loop validation (prevents bot detection)
    ✓ 4 specialized AI agents (Trend, Script, Media, Monetization)
    ✓ Green screen hack for organic reach (algorithm trick)
    ✓ Multi-product monetization strategy
    ✓ Automated profit brief generation
    ✓ SEO keyword integration

MONETIZATION:
    - Affiliate links (Amazon Associates, ShareASale)
    - TikTok Shop native products
    - Creator Fund eligibility tracking
    - Subscription model recommendations

SUPPORT:
    Documentation: See README.md
    Issues: Check logs/viral_engine.log
    
═══════════════════════════════════════════════════════════════════════════════
""")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Viral Engine - Local-First TikTok Content Automation",
        add_help=False  # Disable default help to use our custom one
    )
    parser.add_argument("topic", nargs="?", default="lifestyle_hack", help="Content topic")
    parser.add_argument("--auto", action="store_true", help="Auto-post (NOT recommended)")
    parser.add_argument("-h", "--help", action="store_true", help="Show help")
    
    args = parser.parse_args()
    
    if args.help or "--help" in sys.argv or "-h" in sys.argv:
        display_help()
        sys.exit(0)
    
    # Run main pipeline
    result = asyncio.run(main(topic=args.topic, auto_post=args.auto))
    
    logger.info("\n" + "=" * 80)
    logger.info("✨ Viral Engine Execution Complete")
    logger.info("=" * 80)
    logger.debug(f"Result: {result}")
