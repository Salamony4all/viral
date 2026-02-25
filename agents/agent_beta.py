"""
Agent Beta: The "Narrative Architect" (Script & Strategy)
Persona: Viral Psychology Expert & Copywriter
Tools: Local LLM via Ollama (Llama 3 / Mistral), topic-aware template engine
"""
from __future__ import annotations

import random
import re
try:
    from crewai import Agent, Task
except ImportError:
    Agent = None
    Task = None
from typing import Dict, List, Any, Optional
import json
from datetime import datetime
from pathlib import Path
from loguru import logger
from config.settings import (
    ASSETS_DIR, CONTENT_LENGTH_SECONDS,
    BAIDU_AI_API_KEY, BAIDU_AI_BASE_URL, BAIDU_AI_MODEL, BAIDU_AI_FALLBACK_MODEL,
    GOOGLE_VEO_API_KEY,
)
from openai import AsyncOpenAI
from google import genai
import asyncio

llm = None


# ======================================================================
# Hook templates — used when LLM is offline to produce topic-aware scripts
# ======================================================================

_HOOK_TEMPLATES = [
    {
        "pattern": "pattern_interrupt",
        "opener": 'Stop scrolling — this changes everything about {topic}',
        "structure": [
            ("0-2s", "Person looking surprised at their phone about {topic}", 'Stop scrolling — this changes everything about {topic}'),
            ("2-4s", "{topic_visual}", '"Most people get {topic} completely wrong"'),
            ("4-7s", "Charts and statistics about {topic} results", '"Here\'s what actually works — and nobody talks about it"'),
            ("7-10s", "Person demonstrating {topic} step by step", '"The secret is surprisingly simple — {tip}"'),
            ("10-13s", "Impressive {topic} transformation and results", '"Once you try this, you\'ll never go back"'),
            ("13-15s", "Motivated person smiling and pointing at camera", '"Save this before it disappears — share with someone who needs it"'),
        ],
    },
    {
        "pattern": "negative_frame",
        "opener": 'Stop doing this with {topic} — seriously',
        "structure": [
            ("0-2s", "Person shaking head in warning about {topic}", '"Stop doing this with {topic} — seriously"'),
            ("2-5s", "Person making a common {topic} mistake", '"Everyone thinks {common_mistake} — but it\'s dead wrong"'),
            ("5-8s", "Person showing the correct {topic} approach", '"Instead, try this — {tip}"'),
            ("8-11s", "Clear {topic} results and proof of improvement", '"The difference is night and day"'),
            ("11-13s", "Side by side comparison of {topic} methods", '"Which side are you on?"'),
            ("13-15s", "Person confidently speaking about {topic} tips", '"Follow for more {topic} secrets you won\'t find anywhere else"'),
        ],
    },
    {
        "pattern": "curiosity_gap",
        "opener": 'I just discovered something about {topic} that blew my mind',
        "structure": [
            ("0-2s", "Person with amazed expression discovering {topic}", '"I just discovered something about {topic} that blew my mind"'),
            ("2-5s", "{topic_visual} from a new perspective", '"I\'ve been doing {topic} for years and NEVER knew this"'),
            ("5-8s", "Detailed view of {topic} with visual proof", '"Turns out — {tip}"'),
            ("8-11s", "Hands-on {topic} demonstration in practice", '"Here\'s exactly how to use it"'),
            ("11-13s", "Happy person showing {topic} success results", '"This alone saved me so much time and effort"'),
            ("13-15s", "Person sharing and bookmarking {topic} content", '"Bookmark this — you\'ll thank me later"'),
        ],
    },
    {
        "pattern": "question_hook",
        "opener": 'Why does nobody talk about this {topic} trick?',
        "structure": [
            ("0-2s", "Confused person thinking about {topic}", '"Why does nobody talk about this {topic} trick?"'),
            ("2-5s", "Person struggling with wrong {topic} approach", '"I tried everything — nothing worked until this"'),
            ("5-8s", "Exciting {topic} discovery revealed on screen", '"The answer was {tip} all along"'),
            ("8-11s", "Clear step by step {topic} tutorial", '"Here\'s exactly what to do — step by step"'),
            ("11-13s", "Successful {topic} transformation moment", '"And just like that — game changer"'),
            ("13-15s", "Person engaging with audience about {topic}", '"Did you know this? Comment below — I\'ll reply"'),
        ],
    },
]

_HOOK_TEMPLATES_AR = [
    {
        "pattern": "pattern_interrupt",
        "opener": "توقف — هذا يغير كل شيء عن {topic}",
        "structure": [
            ("0-2s", "شخص متفاجئ ينظر لهاتفه عن {topic}", '"توقف — هذا يغير كل شيء عن {topic}"'),
            ("2-4s", "{topic_visual}", '"أغلب الناس يفهمون {topic} بشكل خاطئ تماماً"'),
            ("4-7s", "إحصائيات ونتائج عن {topic}", '"هذا اللي فعلاً يشتغل — وما حد يتكلم عنه"'),
            ("7-10s", "شخص يشرح {topic} خطوة بخطوة", '"السر بسيط جداً — {tip}"'),
            ("10-13s", "نتائج مبهرة وتحول في {topic}", '"لما تجرب هالشي، ما راح ترجع للطريقة القديمة"'),
            ("13-15s", "شخص متحمس يتكلم للكاميرا", '"احفظ هالمقطع وشاركه مع أحد يحتاجه"'),
        ],
    },
    {
        "pattern": "negative_frame",
        "opener": "لا تسوي كذا مع {topic} — بجد",
        "structure": [
            ("0-2s", "شخص يحذر عن {topic}", '"لا تسوي كذا مع {topic} — بجد"'),
            ("2-5s", "شخص يسوي خطأ شائع في {topic}", '"الكل يفكر إن {common_mistake} — وهذا غلط"'),
            ("5-8s", "شخص يوضح الطريقة الصحيحة لـ{topic}", '"بدال كذا، جرب هالشي — {tip}"'),
            ("8-11s", "نتائج واضحة وتحسن في {topic}", '"الفرق كبير جداً"'),
            ("11-13s", "مقارنة بين الطريقة الغلط والصح", '"أنت في أي فريق؟"'),
            ("13-15s", "شخص يتكلم بثقة عن نصائح {topic}", '"تابعني لأسرار {topic} ما تلقاها بأي مكان ثاني"'),
        ],
    },
    {
        "pattern": "curiosity_gap",
        "opener": "اكتشفت شي عن {topic} صدمني",
        "structure": [
            ("0-2s", "شخص مندهش يكتشف شي عن {topic}", '"اكتشفت شي عن {topic} صدمني"'),
            ("2-5s", "{topic_visual} من زاوية جديدة", '"أسوي {topic} من سنين وما عمري عرفت هالشي"'),
            ("5-8s", "تفاصيل {topic} مع إثبات واضح", '"طلع إن — {tip}"'),
            ("8-11s", "تطبيق عملي لـ{topic}", '"هذي بالضبط الطريقة"'),
            ("11-13s", "شخص سعيد بنتائج {topic}", '"هالشي الواحد وفر عليّ وقت وجهد كثير"'),
            ("13-15s", "شخص يشارك محتوى {topic}", '"احفظ هالمقطع — بتشكرني بعدين"'),
        ],
    },
    {
        "pattern": "question_hook",
        "opener": "ليش ما أحد يتكلم عن هالحيلة في {topic}؟",
        "structure": [
            ("0-2s", "شخص محتار يفكر في {topic}", '"ليش ما أحد يتكلم عن هالحيلة في {topic}؟"'),
            ("2-5s", "شخص يعاني مع {topic} بطريقة خاطئة", '"جربت كل شي — ما نفع شي إلا هذا"'),
            ("5-8s", "اكتشاف مثير في {topic}", '"الجواب كان {tip} من البداية"'),
            ("8-11s", "شرح خطوة بخطوة لـ{topic}", '"هذي بالضبط الخطوات — وحدة وحدة"'),
            ("11-13s", "لحظة نجاح وتحول في {topic}", '"وكذا — تغير كل شي"'),
            ("13-15s", "شخص يتفاعل مع الجمهور عن {topic}", '"كنت تعرف هالشي؟ علق تحت — بارد عليك"'),
        ],
    },
]

_TOPIC_TIPS_AR: Dict[str, List[str]] = {
    "default": [
        "ركز على الـ20% اللي فعلاً تحرك الأمور",
        "ابني عادة صغيرة كل أسبوع",
        "أتمت الأشياء المملة عشان تركز على المهم",
    ],
    "education": [
        "حول المفاهيم المعقدة لرسومات بسيطة وواضحة",
        "استخدم أمثلة من الواقع عشان الفكرة توصل",
        "تقنية فاينمان — اشرحها ببساطة عشان تفهمها بعمق",
    ],
}

_COMMON_MISTAKES_AR: Dict[str, str] = {
    "default": "تتبع نصائح عامة بدون ما تعدلها على وضعك",
    "education": "الحفظ بدون فهم المفهوم",
}

_TOPIC_TIPS: Dict[str, List[str]] = {
    "default": [
        "focusing on the 20% that actually moves the needle",
        "building one small habit every single week",
        "automating the boring stuff so you can focus on what matters",
    ],
    "productivity": [
        "time-blocking your deep work in 90-minute sprints",
        "the two-minute rule — if it takes less than 2 minutes, do it now",
        "batching similar tasks together to cut context-switching",
    ],
    "fitness": [
        "progressive overload — increase weight by just 2.5% each week",
        "eating protein within 30 minutes of your workout",
        "walking 10,000 steps daily — the most underrated fat-loss hack",
    ],
    "money": [
        "paying yourself first — automate 20% of income to savings",
        "the 50/30/20 budgeting rule that actually sticks",
        "starting a micro side-hustle with zero startup cost",
    ],
    "cooking": [
        "mise en place — prep all ingredients before you start cooking",
        "using high heat for the perfect sear on protein",
        "one-pan meals that taste gourmet but take 15 minutes",
    ],
    "travel": [
        "booking flights on Tuesday at 3 PM for the cheapest prices",
        "using Google Flights price alerts to save hundreds",
        "packing cubes — the travel hack that changes everything",
    ],
    "ai": [
        "using AI to automate repetitive tasks and save 10+ hours per week",
        "prompt engineering — the exact words that get better AI results",
        "stacking free AI tools to replace expensive software",
    ],
    "education": [
        "breaking complex concepts into simple visual diagrams",
        "using real-world examples to make abstract ideas click",
        "the Feynman technique — explaining it simply to understand it deeply",
    ],
    "philosophy": [
        "Stoic journaling for 5 minutes every morning",
        "the circle of control — focus only on what you can change",
        "memento mori — using mortality as motivation, not fear",
    ],
}

_COMMON_MISTAKES: Dict[str, str] = {
    "default": "following generic advice without adapting it",
    "productivity": "multitasking makes you productive",
    "fitness": "more cardio equals more fat loss",
    "money": "saving what's left over instead of paying yourself first",
    "cooking": "cooking on high heat to save time",
    "travel": "booking last minute gets you the best deals",
    "ai": "AI will replace all human creativity",
    "education": "memorizing without understanding the concept",
    "philosophy": "philosophy is just abstract thinking with no real-world use",
}


def _classify_topic(topic: str) -> str:
    """Map a user topic to a category for template selection."""
    topic_lower = topic.lower()

    math_words = [
        "math", "circle", "triangle", "geometry", "algebra", "calculus",
        "equation", "formula", "circumference", "radius", "diameter",
        "angle", "fraction", "pi", "area", "volume", "arithmetic",
        "percentage", "quadratic", "polynomial", "number",
    ]
    if any(w in topic_lower for w in math_words):
        return "education"

    science_words = [
        "physics", "chemistry", "biology", "atom", "molecule",
        "experiment", "gravity", "energy", "cell", "dna",
        "evolution", "quantum", "electron", "force", "science",
    ]
    if any(w in topic_lower for w in science_words):
        return "education"

    for key in _TOPIC_TIPS:
        if key != "default" and key in topic_lower:
            return key

    mapping = {
        "productivity": ["productive", "habit", "routine", "morning", "study", "student", "work", "focus"],
        "fitness": ["gym", "exercise", "workout", "muscle", "weight", "body", "health", "wellness"],
        "money": ["finance", "invest", "saving", "budget", "hustle", "income", "earn", "rich"],
        "cooking": ["recipe", "food", "cook", "meal", "kitchen", "eat", "diet", "nutrition"],
        "travel": ["trip", "flight", "backpack", "adventure", "destination", "vacation", "explore"],
        "ai": ["artificial", "machine", "learning", "chatgpt", "automation", "tools", "tech"],
        "philosophy": ["stoic", "existential", "ethics", "philosophy", "plato", "socrates"],
    }
    for cat, keywords in mapping.items():
        if any(kw in topic_lower for kw in keywords):
            return cat
    return "default"


def _pick_visual(topic: str) -> str:
    """Return a concrete, search-friendly visual description for the topic."""
    cat = _classify_topic(topic)
    visuals = {
        "productivity": "person working productively at organized desk with laptop",
        "fitness": "athlete exercising with dumbbells in modern gym",
        "money": "person counting money and managing finances",
        "cooking": "chef preparing fresh food in a kitchen",
        "travel": "traveler exploring beautiful scenic destination",
        "ai": "person using artificial intelligence technology on computer",
        "education": f"teacher explaining {topic} on whiteboard in classroom",
        "philosophy": "peaceful person meditating in beautiful nature",
        "default": f"person actively engaged in {topic}",
    }
    return visuals.get(cat, visuals["default"])


class NarrativeArchitectAgent:
    """
    Generates viral scripts with pattern interrupts, negative frames,
    and integrated SEO keywords.  When the LLM (Ollama) is unavailable
    the agent falls back to a topic-aware template engine that incorporates
    scraped trends data.
    """

    def __init__(self, trends_data: Optional[Dict[str, Any]] = None):
        self.llm = llm
        self.logger = logger
        self.trends_data = trends_data or {"seo_keywords": [], "hook_patterns": []}
        self.content_duration = CONTENT_LENGTH_SECONDS

    async def brainstorm(self, prompt: str) -> str:
        """Interactive brainstorm using Google Gemini about narrative and strategy."""
        from google import genai
        from config.settings import GOOGLE_VEO_API_KEY

        system_ctx = (
            "You are Agent Beta, a Viral Psychology Expert & Copywriter "
            "with 15+ years in viral marketing. You understand psychological triggers, "
            "pattern recognition, and the neuroscience of attention."
        )
        full_prompt = f"{system_ctx}\n\nUser question: {prompt}\n\nProvide creative direction:"
        
        try:
            if not GOOGLE_VEO_API_KEY:
                raise ValueError("API Key missing")
            
            client = genai.Client(api_key=GOOGLE_VEO_API_KEY)
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=full_prompt
            )
            return response.text
        except Exception as e:
            self.logger.warning(f"Gemini brainstorm failed: {e}")
            return (
                f"[Agent Beta - Narrative Architect]\n\n"
                f"Regarding: {prompt}\n\n"
                f"Script strategy recommendations:\n"
                f"1. Hook first 2 seconds: Use pattern interrupt or negative frame\n"
                f"2. Structure: Hook -> Problem -> Agitate -> Solution -> CTA\n"
                f"3. Keep sentences under 8 words for punch\n"
                f"4. End with curiosity hook\n"
                f"5. Add pacing cues: PAUSE, BEAT, TRANSITION\n\n"
                f"(Template fallback - Gemini offline)"
            )

    def get_agent(self):
        if Agent is None:
            return None
        return Agent(
            role="Viral Psychology Expert & Copywriter",
            goal="Generate compelling, hook-driven scripts with pattern interrupts and SEO keywords",
            backstory=(
                "World-class copywriter with 15+ years in viral marketing. "
                "You understand psychological triggers, pacing, and TikTok algorithm signals."
            ),
            tools=[],
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
        )

    # ------------------------------------------------------------------
    # Script generation
    # ------------------------------------------------------------------

    async def generate_script(
        self, topic: str, hook_type: str = "pattern_interrupt",
        language: str = "en",
    ) -> Dict[str, Any]:
        """
        Premium script generation: Gemini/Baidu -> Template Fallback.
        Ensures high-retention structure and viral hooks.
        """
        self.logger.info(f"✍️ [Agent Beta] Architectural design for campaign: {topic} (lang={language})")

        seo_keywords = self.trends_data.get("seo_keywords", [])
        hook_patterns = self.trends_data.get("hook_patterns", [])
        selected_hook = next(
            (h for h in hook_patterns if h.get("pattern") == hook_type),
            None
        )

        # Multi-stage generation
        prompt = self._build_script_prompt(topic, hook_type, seo_keywords, selected_hook, language)
        script_content, ai_source = await self._call_llm(prompt)
        script_columns = self._parse_script_to_columns(script_content)

        # Fallback if AI fails or output is garbage
        if not script_columns or self._is_generic(script_columns, topic):
            self.logger.info(f"AI source {ai_source} failed/generic — using topic-aware template engine")
            script_columns = self._generate_topic_aware_columns(topic, language)
            ai_source = "template"
        else:
            self.logger.info(f"Using Premium {ai_source.upper()} Scripting ({len(script_columns)} scenes)")

        final_raw = "\n".join(
            f"{c['timecode']} | {c['visual_cue']} | {c['audio']}"
            for c in script_columns
        )

        script_data = {
            "generated_at": datetime.now().isoformat(),
            "topic": topic,
            "language": language,
            "hook_type": hook_type,
            "duration_seconds": self.content_duration,
            "seo_keywords": seo_keywords,
            "script_columns": script_columns,
            "raw_content": final_raw,
            "script_source": ai_source,
        }

        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        script_path = ASSETS_DIR / f"script_{ts}.json"
        with open(script_path, "w", encoding="utf-8") as f:
            json.dump(script_data, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Script finalized and saved to: {script_path}")
        return script_data

        self.logger.info(f"Script saved: {script_path}")
        return script_data

    def _is_generic(self, columns: List[Dict[str, str]], topic: str) -> bool:
        """Detect if the columns are the old hardcoded fallback."""
        if not columns:
            return True
        first_audio = columns[0].get("audio", "").lower()
        if "80/20" in first_audio or "millionaires" in first_audio:
            return True
        has_arabic = bool(re.search(r"[\u0600-\u06FF]", topic))
        if has_arabic:
            return len(columns) < 3 or not any(c.get("audio", "").strip() for c in columns)
        topic_words = set(re.findall(r"[a-zA-Z]{3,}", topic.lower()))
        all_audio = " ".join(c.get("audio", "").lower() for c in columns)
        return not any(w in all_audio for w in topic_words)

    # ------------------------------------------------------------------
    # Topic-aware template engine
    # ------------------------------------------------------------------

    def _generate_topic_aware_columns(
        self, topic: str, language: str = "en",
    ) -> List[Dict[str, str]]:
        """Build a script from templates, trends data, and the topic."""
        cat = _classify_topic(topic)

        if language == "ar":
            tips_pool = _TOPIC_TIPS_AR.get(cat, _TOPIC_TIPS_AR["default"])
            mistakes_pool = _COMMON_MISTAKES_AR
            templates_pool = _HOOK_TEMPLATES_AR
        else:
            tips_pool = _TOPIC_TIPS.get(cat, _TOPIC_TIPS["default"])
            mistakes_pool = _COMMON_MISTAKES
            templates_pool = _HOOK_TEMPLATES

        tip = random.choice(tips_pool)
        mistake = mistakes_pool.get(cat, mistakes_pool["default"])
        visual = _pick_visual(topic)

        seo = self.trends_data.get("seo_keywords", [])
        seo_str = ", ".join(seo[:3]) if seo else ""

        template = random.choice(templates_pool)
        columns: List[Dict[str, str]] = []

        for tc, vis_tpl, aud_tpl in template["structure"]:
            vis = vis_tpl.format(
                topic=topic, topic_visual=visual, tip=tip,
                common_mistake=mistake,
            )
            aud = aud_tpl.format(
                topic=topic, topic_visual=visual, tip=tip,
                common_mistake=mistake,
            )
            columns.append({"timecode": tc, "visual_cue": vis, "audio": aud})

        if seo_str and columns:
            last = columns[-1]
            last["audio"] = last["audio"].rstrip('"') + f' #{seo_str}"'

        return columns

    # ------------------------------------------------------------------
    # LLM interaction
    # ------------------------------------------------------------------

    def _build_script_prompt(
        self, topic: str, hook_type: str, keywords: List[str],
        hook_pattern: Optional[Dict], language: str = "en",
    ) -> str:
        kw = ", ".join(keywords[:5]) if keywords else "viral, trending, must-see"
        hook_ex = hook_pattern.get("example", "") if hook_pattern else ""

        if language == "ar":
            return f"""أنت كاتب سكربتات فيرال محترف. اكتب سكربت تيك توك بالعربية:

الموضوع: {topic}
نوع الهوك: {hook_type}
المدة: {self.content_duration} ثانية
الكلمات المفتاحية (أدخلها بشكل طبيعي): {kw}

أنشئ سكربتاً بثلاث أعمدة بالصيغة:
[TIME CODE] | [وصف المشهد البصري] | [النص المنطوق]

القواعد:
1. ابدأ بـ pattern interrupt في أول ثانيتين
2. جمل قصيرة وقوية
3. اختم بدعوة للتفاعل أو فضول
4. 100% أصلي وطبيعي عن "{topic}"
5. اكتب كل شيء بالعربية الفصحى أو العامية حسب السياق

مثال:
0-2s | شخص متفاجئ ينظر للكاميرا | "توقف — هذا يغير كل شيء"
2-5s | لقطات توضيحية | "أغلب الناس يفهمون الموضوع غلط"

اكتب السكربت الآن:"""

        return f"""
You are a world-class viral script writer. Generate a TikTok script.

TOPIC: {topic}
HOOK TYPE: {hook_type}
HOOK EXAMPLE: {hook_ex}
DURATION: {self.content_duration} seconds
SEO KEYWORDS (integrate naturally): {kw}

OUTPUT FORMAT - Use EXACTLY this format, one scene per line:
[TIME CODE] | [VISUAL CUE] | [SPOKEN AUDIO]

Example:
0-2s | Jump-cut to shocked face | "Wait... this is actually genius..."
2-5s | B-roll footage | "Most people don't know this trick..."
5-8s | Person demonstrating | "Here's exactly what to do"

Rules:
1. Start with a PATTERN INTERRUPT in the first 2 seconds
2. Integrate 2-3 SEO keywords naturally
3. Short punchy sentences (under 8 words each)
4. End with CTA or curiosity hook
5. 100% original about "{topic}" - no generic filler
6. Output ONLY the script lines in the format above, no preamble or explanation

Generate the script now:
"""

    async def _call_baidu_ai(self, prompt: str) -> str:
        """Call Baidu AI Studio (Ernie) for dynamic script generation."""
        if not BAIDU_AI_API_KEY:
            return ""
        
        client = AsyncOpenAI(api_key=BAIDU_AI_API_KEY, base_url=BAIDU_AI_BASE_URL)

        async def _extract_content(completion) -> str:
            if not completion.choices:
                return ""
            msg = completion.choices[0].message
            content = getattr(msg, "content", None) or ""
            if not content and hasattr(msg, "reasoning_content") and msg.reasoning_content:
                content = msg.reasoning_content
            return content or ""

        for model in [BAIDU_AI_MODEL, BAIDU_AI_FALLBACK_MODEL]:
            try:
                self.logger.info(f"Calling Baidu AI ({model})...")
                completion = await client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    stream=False,
                    extra_body={"web_search": {"enable": False}},
                    max_completion_tokens=4096,
                )
                content = await _extract_content(completion)
                if content and len(content) > 20:
                    self.logger.info("Baidu AI script generated successfully")
                    return content
            except Exception as e:
                self.logger.warning(f"Baidu AI ({model}) failed: {e}. Trying fallback.")
        return ""

    async def call_gemini(self, prompt: str) -> Optional[str]:
        """Call Google Gemini 1.5 for premium scripting."""
        try:
            if not GOOGLE_VEO_API_KEY:
                self.logger.warning("GOOGLE_VEO_API_KEY missing - skipping Gemini scripting")
                return None
            
            self.logger.info("Calling Google Gemini 1.5-Flash for script...")
            client = genai.Client(api_key=GOOGLE_VEO_API_KEY)
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )
            if response.text:
                self.logger.success("Gemini script generated successfully")
                return response.text
            return None
        except Exception as e:
            self.logger.warning(f"Gemini scripting failed: {e}")
            return None

    async def _call_llm(self, prompt: str) -> tuple:
        """Returns (content, source) where source is 'gemini|baidu'. Fallback to template."""
        # 1. Try Gemini (Primary per updated request)
        gemini_out = await self.call_gemini(prompt)
        if gemini_out:
            return (gemini_out, "gemini")

        # 2. Try Baidu (Secondary Fallback)
        if BAIDU_AI_API_KEY:
            out = await self._call_baidu_ai(prompt)
            if out:
                return (out, "baidu")

        self.logger.info("Premium LLMs unavailable — using template engine.")
        return ("", "")

    def _parse_script_to_columns(self, content: str) -> List[Dict[str, str]]:
        """Parse script text into columns. Handles markdown, multiple formats."""
        columns = []
        raw = content.strip()
        # Extract from markdown code block if present
        code_match = re.search(r"```[\w]*\n?(.*?)```", raw, re.DOTALL | re.IGNORECASE)
        if code_match:
            raw = code_match.group(1).strip()
        for line in raw.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Format: "0-2s | visual | audio" or "0-2s: visual | audio" or "0-2s - visual - audio"
            parts = None
            if "|" in line:
                parts = [p.strip().strip('"\'') for p in line.split("|")]
            elif " - " in line:
                parts = [p.strip().strip('"\'') for p in line.split(" - ", 2)]
            elif ":" in line and len(line.split(":", 2)) >= 3:
                parts = [p.strip().strip('"\'') for p in line.split(":", 2)]
            if parts and len(parts) >= 3:
                tc = parts[0]
                if re.match(r"^\d+s?-\d+s?$|^\d+-\d+s?$", tc.replace(" ", "")):
                    columns.append({
                        "timecode": tc,
                        "visual_cue": parts[1],
                        "audio": parts[2].strip('"\'') or parts[2],
                    })
                elif re.match(r"^\d", tc):
                    columns.append({
                        "timecode": tc,
                        "visual_cue": parts[1],
                        "audio": parts[2].strip('"\'') or parts[2],
                    })
        return columns

    # ------------------------------------------------------------------
    # Variations
    # ------------------------------------------------------------------

    async def generate_variations(self, base_script: Dict[str, Any], num_variations: int = 2) -> List[Dict[str, Any]]:
        self.logger.info(f"Generating {num_variations} script variations in parallel...")
        topic = base_script.get("topic", "viral content")
        lang = base_script.get("language", "en")
        seo = base_script.get("seo_keywords", [])

        async def _gen_one(i):
            prompt = self._build_script_prompt(topic, "pattern_interrupt", seo, None, lang)
            content, source = await self._call_llm(prompt)
            columns = self._parse_script_to_columns(content)
            if not columns:
                columns = self._generate_topic_aware_columns(topic, lang)
            raw = "\n".join(f"{c['timecode']} | {c['visual_cue']} | {c['audio']}" for c in columns)
            templates = _HOOK_TEMPLATES_AR if lang == "ar" else _HOOK_TEMPLATES
            return {
                "variation_number": i + 1,
                "hook_type": templates[i % len(templates)]["pattern"],
                "script_columns": columns,
                "raw_content": raw,
            }

        tasks = [_gen_one(i) for i in range(num_variations)]
        return await asyncio.gather(*tasks)

    # ------------------------------------------------------------------
    # Captions
    # ------------------------------------------------------------------

    def generate_captions(self, script_columns: List[Dict[str, str]]) -> List[Dict[str, str]]:
        self.logger.info("✍️ [Agent Beta] Extracting high-impact keywords for dynamic captions...")
        captions = []
        for col in script_columns:
            audio = col.get("audio", "")
            words = [w.strip('"\'.,!?') for w in audio.split() if len(w) > 4]
            if words:
                captions.append({
                    "timecode": col.get("timecode", "0-5s"),
                    "text": " ".join(words[:4]).upper(),
                    "position": "center",
                    "style": "bold_yellow",
                })
        return captions or [
            {"timecode": "0-5s", "text": "WATCH THIS", "position": "center", "style": "bold_yellow"},
        ]


async def run_narrative_architect(
    trends_data: Dict[str, Any], topic: str = "lifestyle_hack",
    language: str = "en",
) -> Dict[str, Any]:
    architect = NarrativeArchitectAgent(trends_data)
    
    # Generate single script
    script = await architect.generate_script(topic, hook_type="pattern_interrupt", language=language)
    
    # Generate captions from the script
    captions = await asyncio.to_thread(architect.generate_captions, script.get("script_columns", []))

    return {
        "main_script": script,
        "variations": [],  # Simplified: no variations
        "captions": captions,
        "scripts_ready_for_production": 1,
    }
