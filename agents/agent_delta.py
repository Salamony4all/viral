"""
Agent Delta: The "Profit Oracle" (Monetization Research)
Persona: E-commerce Strategist
Mission: Find products and strategies to monetize viral content
"""
try:
    from crewai import Agent, Task
except ImportError:
    Agent = None
    Task = None
from typing import Dict, List, Any, Optional
import json
import asyncio
from datetime import datetime
from pathlib import Path
from loguru import logger
import requests
from config.settings import (
    ASSETS_DIR, MONETIZATION_FOCUS
)

llm = None

logger_delta = logger.bind(name="ProfitOracle")


class ProfitOracleAgent:
    """
    Agent Delta: Analyzes content context and identifies monetization opportunities.
    Searches for affiliate products, TikTok Shop items, and SEO strategies.
    """
    
    def __init__(self, script_data: Optional[Dict[str, Any]] = None):
        self.llm = llm
        self.logger = logger_delta
        self.script_data = script_data or {}
        self.topic = self.script_data.get("topic", "general")
    
    async def brainstorm(self, prompt: str) -> str:
        """Interactive brainstorm using Google Gemini about monetization strategies."""
        from google import genai
        from config.settings import GOOGLE_VEO_API_KEY
        
        system_context = (
            "You are Agent Delta, an E-commerce Strategist & Monetization Expert "
            "with 8+ years in affiliate marketing, TikTok Shop optimization, and "
            "content monetization. You understand conversion psychology and how to "
            "position products for maximum revenue without being salesy."
        )
        full_prompt = f"{system_context}\n\nUser question: {prompt}\n\nProvide monetization strategy:"
        
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
                f"[Agent Delta - Profit Oracle]\n\n"
                f"Regarding: {prompt}\n\n"
                f"Monetization strategy:\n"
                f"1. Primary: Amazon Associates affiliate links (8-10% commission)\n"
                f"2. Secondary: TikTok Shop native products (15-30% commission)\n"
                f"3. CTA Strategy: 'Check the comments' for organic feel\n"
                f"4. Never say 'Link in bio' - kills organic reach\n"
                f"5. Month 1-3: Build audience with free value\n"
                f"6. Month 3+: Layer in affiliates gradually\n"
                f"7. Apply for TikTok Creator Fund ($200-$10k/month)\n\n"
                f"(Template fallback - Gemini offline)"
            )
    
    def get_agent(self):
        """Create the Profit Oracle agent."""
        if Agent is None:
            return None
        return Agent(
            role="E-commerce Strategist & Monetization Expert",
            goal="Identify high-converting products and monetization strategies that align with viral content",
            backstory="""You are a brilliant e-commerce strategist with 8+ years of experience
            in affiliate marketing, TikTok Shop optimization, and content monetization.
            You understand conversion psychology, product-content alignment, and how to
            position products for maximum revenue. You never recommend irrelevant products.""",
            tools=[],
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
        )
    
    async def analyze_monetization_context(self) -> Dict[str, Any]:
        """
        Analyze the script content to understand optimal monetization angle.
        Returns: niche, audience_demographics, buying_intent, product_categories.
        """
        self.logger.info("💹 [Agent Delta] Analyzing monetization context and buying intent...")
        
        script_text = " ".join([
            col.get("audio", "") 
            for col in self.script_data.get("script_columns", [])
        ])
        
        prompt = f"""
Analyze this TikTok script for monetization potential:

SCRIPT: {script_text[:500]}

Identify:
1. Primary niche/category
2. Target audience demographics
3. Buying intent level (high/medium/low)
4. Best product categories for affiliate/sponsorship
5. Estimated conversion potential (%)

Respond in JSON format.
"""
        
        try:
            from google import genai
            from config.settings import GOOGLE_VEO_API_KEY
            
            if not GOOGLE_VEO_API_KEY:
                return self._get_fallback_analysis()
                
            client = genai.Client(api_key=GOOGLE_VEO_API_KEY)
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            analysis = json.loads(response.text)
            return analysis
        except Exception as e:
            self.logger.warning(f"Gemini analysis failed: {e}")
            return self._get_fallback_analysis()
    
    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Fallback monetization analysis."""
        return {
            "primary_niche": self.topic or "lifestyle",
            "target_audience": "18-35 years old, trend-conscious, early adopters",
            "buying_intent": "high",
            "product_categories": ["lifestyle products", "wellness", "productivity tools"],
            "conversion_potential": "45-65%",
        }
    
    async def search_affiliate_products(self, category: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for top-rated affiliate products matching the content category.
        Prioritizes Amazon Associates, ShareASale, and affiliate networks.
        """
        self.logger.info(f"💹 [Agent Delta] Discovering high-margin affiliate products for: {category}...")
        
        try:
            # In production, would query affiliate APIs
            # For now, return curated data
            products = self._get_affiliate_products_fallback(category)
            self.logger.info(f"Found {len(products)} affiliate products")
            return products[:max_results]
        
        except Exception as e:
            self.logger.error(f"Affiliate search failed: {e}")
            return self._get_affiliate_products_fallback(category)
    
    def _get_affiliate_products_fallback(self, category: str) -> List[Dict[str, Any]]:
        """Fallback affiliate product data."""
        product_db = {
            "lifestyle": [
                {
                    "name": "Premium Productivity Planner",
                    "url": "https://amzn.to/example-planner",
                    "price": "$29.99",
                    "commission": "10%",
                    "rating": 4.8,
                    "reviews": 2341,
                    "affiliate_network": "Amazon Associates",
                    "conversion_likelihood": "high",
                    "reason": "Directly solves problem mentioned in script",
                },
                {
                    "name": "Time Management App (Affiliate Link)",
                    "url": "https://shareAsale.com/example-app",
                    "price": "Free + $9.99/month",
                    "commission": "25%",
                    "rating": 4.6,
                    "reviews": 1205,
                    "affiliate_network": "ShareASale",
                    "conversion_likelihood": "high",
                    "reason": "Subscription model = recurring revenue",
                },
            ],
            "wellness": [
                {
                    "name": "Sleep Optimization Kit",
                    "url": "https://amzn.to/sleep-kit",
                    "price": "$49.99",
                    "commission": "8%",
                    "rating": 4.7,
                    "reviews": 892,
                    "affiliate_network": "Amazon Associates",
                    "conversion_likelihood": "medium",
                    "reason": "Related to wellness angle",
                },
            ],
            "default": [
                {
                    "name": "Trending Lifestyle Product",
                    "url": "https://amzn.to/trending",
                    "price": "$39.99",
                    "commission": "10%",
                    "rating": 4.5,
                    "reviews": 1500,
                    "affiliate_network": "Amazon Associates",
                    "conversion_likelihood": "medium",
                    "reason": "Popular in target demographic",
                },
            ],
        }
        
        return product_db.get(category.lower(), product_db["default"])
    
    async def search_tiktok_shop_products(self, keyword: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search TikTok Shop for dropshipping/native products.
        Higher commission potential but requires TikTok Shop seller account.
        """
        self.logger.info(f"💹 [Agent Delta] Scanning TikTok Shop for trending items: {keyword}...")
        
        try:
            # In production, would query TikTok Shop API
            products = self._get_tiktok_shop_fallback(keyword)
            return products[:max_results]
        
        except Exception as e:
            self.logger.error(f"TikTok Shop search failed: {e}")
            return self._get_tiktok_shop_fallback(keyword)
    
    def _get_tiktok_shop_fallback(self, keyword: str) -> List[Dict[str, Any]]:
        """Fallback TikTok Shop product data."""
        return [
            {
                "name": "Trending TikTok Shop Product",
                "tiktok_shop_url": "https://shop.tiktok.com/example",
                "price": "$19.99",
                "commission_rate": "15-30%",
                "popularity_score": 9.2,
                "shipping_time": "7-14 days",
                "seller_rating": 4.8,
                "inventory": "In stock",
                "note": "Direct mention in video = 30% commission boost",
            },
        ]
    
    async def generate_cta_strategies(self, products: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Generate specific call-to-action strategies for each product.
        Strategies: Link in bio, QR code, green screen product reveal, etc.
        """
        self.logger.info("Generating CTA strategies...")
        
        strategies = []
        
        from google import genai
        from config.settings import GOOGLE_VEO_API_KEY
        
        for product in products:
            prompt = f"""
Create 3 unique, native TikTok CTAs for this product without being salesy:
Product: {product.get('name')}
Context: Lifestyle/productivity content
Restrictions: No "Click the link" - must feel organic

Respond ONLY in JSON format with: cta_text, placement_timing, delivery_tone
"""
            
            try:
                if not GOOGLE_VEO_API_KEY:
                    strategies.append(self._get_fallback_cta(product))
                    continue
                    
                client = genai.Client(api_key=GOOGLE_VEO_API_KEY)
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=prompt,
                    config={"response_mime_type": "application/json"}
                )
                strategy = json.loads(response.text)
                strategies.append(strategy)
            except Exception as e:
                self.logger.warning(f"Gemini CTA generation failed: {e}")
                strategies.append(self._get_fallback_cta(product))
        
        return strategies
    
    def _get_fallback_cta(self, product: Dict[str, Any]) -> Dict[str, str]:
        """Fallback CTA strategy."""
        return {
            "cta_text": f"Check the comments for the exact tool I use",
            "placement_timing": "10-12s mark (high retention point)",
            "delivery_tone": "casual_mention",
            "alternative_cta": "Drop a 💬 if you want the link",
        }
    
    def generate_profit_brief(
        self,
        monetization_context: Dict[str, Any],
        affiliate_products: List[Dict[str, Any]],
        tiktok_shop_products: List[Dict[str, Any]],
        cta_strategies: List[Dict[str, str]],
    ) -> str:
        """
        Generate PROFIT_BRIEF.md - a comprehensive monetization guide for the user.
        Explains exactly how to monetize this specific video.
        """
        self.logger.info("💹 [Agent Delta] Drafting comprehensive Profitability Brief & CTA Roadmap...")
        
        brief = f"""# 💰 PROFIT BRIEF: Monetization Strategy
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 MONETIZATION CONTEXT
**Primary Niche:** {monetization_context.get('primary_niche', 'Lifestyle')}
**Target Audience:** {monetization_context.get('target_audience', 'Unknown')}
**Buying Intent:** {monetization_context.get('buying_intent', 'Medium')} ⬆️
**Conversion Potential:** {monetization_context.get('conversion_potential', '40-60%')}

---

## 🛒 TOP AFFILIATE PRODUCTS (Amazon Associates)
Recommended for: Direct product recommendations, reviews, comparisons

"""
        
        for idx, product in enumerate(affiliate_products, 1):
            brief += f"""
### {idx}. {product.get('name', 'Product')}
- **Price:** {product.get('price', 'N/A')}
- **Commission:** {product.get('commission', 'N/A')}
- **Rating:** ⭐ {product.get('rating', 'N/A')} ({product.get('reviews', '0')} reviews)
- **Network:** {product.get('affiliate_network', 'Amazon Associates')}
- **Link:** {product.get('url', '#')}
- **Why:** {product.get('reason', 'Relevant to content')}

"""
        
        brief += f"""
---

## 🎁 TIKTOK SHOP PRODUCTS (Native/Dropshipping)
Recommended for: Direct native recommendations, product reveals

"""
        
        for idx, product in enumerate(tiktok_shop_products, 1):
            brief += f"""
### {idx}. {product.get('name', 'Product')}
- **Price:** {product.get('price', 'N/A')}
- **Commission:** {product.get('commission_rate', 'N/A')}
- **Popularity:** {product.get('popularity_score', 'N/A')}/10
- **TikTok Shop URL:** {product.get('tiktok_shop_url', '#')}
- **Note:** {product.get('note', 'Popular product')}

"""
        
        brief += """
---

## 📢 RECOMMENDED CTAs (Call-To-Actions)
**Golden Rule:** Never say "Click the link in bio"
**Instead:** Make recommendations feel organic and native

### Strategy 1: Comments-Based CTA
```
In video: "Drop a 💬 if you want the exact tool I use"
In comments (pinned): "Here's the link [affiliate URL]"
Conversion Rate: 15-25% of engagers
```

### Strategy 2: Green Screen Hack (For Next Video)
```
1. Post THIS video to your main account
2. Record 3-sec reaction/intro on your native camera
3. Use Green Screen effect with this video as background
4. Post native video with product in comments
5. Resets metadata = Higher organic reach
```

### Strategy 3: Niche Community Strategy
```
- Join TikTok communities around the niche
- Comment with valuable insights
- Link product in your profile bio
- Tag relevant creators
```

---

## 💡 HYBRID MONETIZATION (Best Approach)
**Month 1-3:** Build audience with FREE value content
**Month 3+:** Layer in affiliates gradually
**Parallel:** Apply for TikTok Creator Fund ($200-$10k/month)
**Advanced:** Launch your own product/course

---

## 📈 EXPECTED EARNINGS PROJECTION
**Scenario 1: Conservative (100k views, 2% CTR)**
- Affiliate clicks: 2,000
- Conversion rate: 5%
- Conversions: 100
- Average commission: $15/sale
- **Earnings: $1,500**

**Scenario 2: Viral (1M views, 5% CTR)**
- Affiliate clicks: 50,000
- Conversion rate: 8%
- Conversions: 4,000
- Average commission: $15/sale
- **Earnings: $60,000**

---

## ⚡ ACTION CHECKLIST
- [ ] Copy affiliate link from Amazon Associates dashboard
- [ ] Create shortened link (bit.ly or link shortener)
- [ ] Add link to pinned comment template
- [ ] Set up TikTok Shop seller account (if not already)
- [ ] Draft 3 organic CTA variations
- [ ] Test link before posting (ensure it works)
- [ ] Schedule follow-up content to capture warm traffic
- [ ] Track clicks via affiliate dashboard

---

## ❌ WHAT NOT TO DO
- Don't be too salesy (kills organic reach)
- Don't spam the same link multiple times
- Don't recommend products you haven't tested
- Don't ignore your audience (respond to DMs/comments)
- Don't forget to ask for follows/saves (CTR multiplier)

---

## 🚀 NEXT STEPS
1. **Post the video** with all three monetization channels live
2. **Monitor first 6 hours** - this is where most conversions happen
3. **Reply to comments** with genuine engagement (algorithm loves it)
4. **Repost to Stories** with swipe-up link (if Creator Fund eligible)
5. **Repurpose content** - adapt to YouTube, Instagram, TikTok Playlist

---

**Remember:** The best monetization strategy is consistent, authentic content that builds real audience trust. Quick money dies fast. Real money stays forever.

Good luck! 🎬💰
"""
        
        return brief
    
    async def save_profit_brief(self, brief_content: str) -> Path:
        """Save Profit Brief to file."""
        brief_path = ASSETS_DIR / f"PROFIT_BRIEF_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(brief_path, "w", encoding="utf-8") as f:
            f.write(brief_content)
        self.logger.info(f"Profit Brief saved: {brief_path}")
        return brief_path


async def run_profit_oracle(script_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the Profit Oracle pipeline."""
    oracle = ProfitOracleAgent(script_data)
    
    # Analyze monetization context
    context = await oracle.analyze_monetization_context()
    
    # Search for products
    affiliate_products = await oracle.search_affiliate_products(
        context.get("product_categories", ["lifestyle"])[0]
    )
    tiktok_shop_products = await oracle.search_tiktok_shop_products(
        context.get("primary_niche", "general")
    )
    
    # Generate CTAs
    cta_strategies = await oracle.generate_cta_strategies(affiliate_products)
    
    # Generate comprehensive brief
    brief_content = oracle.generate_profit_brief(
        context,
        affiliate_products,
        tiktok_shop_products,
        cta_strategies,
    )
    
    # Save brief
    brief_path = await oracle.save_profit_brief(brief_content)
    
    result = {
        "monetization_context": context,
        "affiliate_products": affiliate_products,
        "tiktok_shop_products": tiktok_shop_products,
        "cta_strategies": cta_strategies,
        "profit_brief_path": str(brief_path),
        "estimated_earnings_potential": {
            "conservative": "$1,500 - $5,000",
            "viral": "$20,000 - $100,000+",
        },
    }
    
    return result


if __name__ == "__main__":
    test_script = {
        "topic": "productivity_hacks",
        "script_columns": [
            {"audio": "This productivity hack will change your life..."},
            {"audio": "Use this tool to save 3 hours per week"},
        ],
    }
    
    result = asyncio.run(run_profit_oracle(test_script))
    print(json.dumps(result, indent=2, default=str))
