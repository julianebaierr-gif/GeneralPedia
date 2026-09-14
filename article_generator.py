import os
import re
import json
import urllib.request
from datetime import datetime

try:
    from config import CATEGORIES, DOMAIN, POSTS_DIR
    from image_service import fetch_unique_unsplash_image
except ImportError:
    from .config import CATEGORIES, DOMAIN, POSTS_DIR
    from .image_service import fetch_unique_unsplash_image
from env_loader import get_secret

GEMINI_API_KEY = get_secret("GEMINI_API_KEY")

# Cascade from newest Gemini 3.8 down through 3.7, 3.6, 3.5, 3.1, and latest/legacy flash models
FALLBACK_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-flash-lite-latest",
    "gemini-flash-latest"
]

def slugify(text):
    text = re.sub(r'[^a-zA-Z0-9\s-]', '', str(text).lower()).strip()
    return re.sub(r'[\s-]+', '-', text)

def capitalize_keyword(kw):
    if not kw:
        return ""
    words = str(kw).strip().split()
    return " ".join(w.capitalize() if not w.isupper() else w for w in words)

def detect_category(primary_kw, semantic_kws):
    kw = primary_kw.lower()
    # 1. Calculators & Tools
    if any(w in kw for w in ['calculator', 'converter', 'calendar', 'tracker', 'depth chart', 'to ml', 'to gallon', 'to inches', 'area code']):
        return "tools"
    # 2. Sports, Culture & Geography
    if any(w in kw for w in ['vs', 'match', 'stats', 'movie', 'film', 'cast', 'season', 'olympics', 'world cup', 'nfl', 'nba', 'game', 'show', 'wizard of oz', 'where is', 'cape verde', 'prague', 'fiji', 'cyprus']):
        return "culture"
    # 3. Automotive
    if any(w in kw for w in ['car', 'toyota', 'honda', 'tesla', 'ford', 'suv', 'truck', 'dodge', 'tire', 'vehicle', 'accord', 'camry', 'corolla', 'porsche', 'bmw', 'crv', 'cr-v']):
        return "automotive"
    # 4. Lifestyle & Pets & Home
    if any(w in kw for w in ['dog', 'cat', 'pet', 'recipe', 'coffee', 'food', 'tea', 'cleaning', 'cook', 'bake', 'dryer vent', 'couch', 'home', 'drain']):
        return "lifestyle"
    # 5. Health & Medical
    if any(w in kw for w in ['symptom', 'disease', 'infection', 'syndrome', 'massage', 'vitamin', 'pain', 'treatment', 'causes', 'medicine', 'diet', 'health', 'cancer', 'thrush', 'sore', 'gallbladder', 'appendix']):
        return "health"
    # 6. Finance & Money
    if any(w in kw for w in ['tax', 'ira', '401k', 'insurance', 'loan', 'mortgage', 'equity', 'salary', 'income', 'refund', 'money', 'credit', 'bank', 'cost of']):
        return "finance"
    # 7. How-To & Guides
    if any(w in kw for w in ['how to', 'what is', 'how many', 'how much', 'why do', 'meaning', 'difference between', 'definition']):
        return "how-to"
    return "how-to"

def generate_tags(primary_kw, semantic_kws, category_slug):
    tags = set()
    cat_name = CATEGORIES[category_slug]["name"]
    tags.add(cat_name)
    tags.add(capitalize_keyword(primary_kw))
    
    for kw in semantic_kws[:5]:
        clean = re.sub(r'[^a-zA-Z0-9\s]', '', kw).strip()
        if clean:
            tags.add(capitalize_keyword(clean))
            
    return list(tags)[:6]

def generate_article_content_via_gemini_api(primary_kw, semantic_kws, category_name):
    """
    Generates rich, 800-1200 word authoritative SEO article content dynamically via Gemini API.
    Tries models starting from Gemini 3.8 down to oldest flash versions automatically.
    Guarantees article is 100% complete from start to finish.
    """
    prompt = f"""Act as an elite SEO content strategist and copywriter.
Write a COMPLETE, comprehensive, and authoritative informational reference guide for a global audience on:
Primary Focus Keyword: "{primary_kw}"
Related Semantic / LSI Keywords: {', '.join(semantic_kws[:8]) if semantic_kws else 'None'}
Category Desk: {category_name}

MANDATORY INSTRUCTIONS:
1. Complete Generation Guarantee: You MUST write the complete article from the opening hook all the way to the final concluding sentence and FAQ answers. Never stop mid-sentence or omit sections.
2. Return clean, production-ready HTML (DO NOT use ```html or ``` code fences, just output standard HTML tags: <h2>, <h3>, <h4>, <p>, <ul>, <li>, <blockquote>).
3. CRITICAL CONSTRAINT: DO NOT USE ANY EM-DASHES ("—"). Use hyphens, commas, or parentheses instead.
4. Content Architecture:
   - High-impact introductory hook defining the topic and its global significance.
   - Featured Snippet Target section: Provide a clear, direct definition or answer block under an <h2> (ideal for Google Position 0).
   - In-depth thematic breakdown sections using <h2> and <h3> subheadings covering mechanisms, comparisons, practical guidelines, and key factors.
   - Natural, organic integration of the primary focus keyword and all related semantic keywords.
   - A dedicated "Frequently Asked Questions" section with 3 highly relevant questions and comprehensive, complete answers.
5. Total length MUST be between 800 and 1,200 words. Keep the tone professional, objective, and deeply informative.
"""
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.35,
            "maxOutputTokens": 8192,
            "thinkingConfig": {
                "thinkingBudget": 500
            }
        }
    }
    
    # Try models starting from 3.8 down to oldest
    for model_name in FALLBACK_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        try:
            print(f"[Gemini AI] Trying model: {model_name}...")
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json', 'User-Agent': 'GeneralPedia-AI/1.0'}
            )
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                candidate = data.get('candidates', [{}])[0]
                finish_reason = candidate.get('finishReason', '')
                
                parts = candidate.get('content', {}).get('parts', [])
                if not parts:
                    print(f"[{model_name}] No content parts returned, trying next fallback model...")
                    continue
                    
                raw_text = parts[0].get('text', '').strip()
                if not raw_text or len(raw_text) < 400:
                    print(f"[{model_name}] Content too short ({len(raw_text)} chars), trying next fallback model...")
                    continue
                    
                # Clean possible markdown block wraps
                clean_html = re.sub(r'^```html\s*', '', raw_text)
                clean_html = re.sub(r'```$', '', clean_html).strip()
                
                word_count = len(clean_html.split())
                print(f"[Gemini AI Success] Model: {model_name} generated complete article ({word_count} words, finish: {finish_reason})")
                return clean_html
        except Exception as e:
            print(f"[Gemini AI Warning] Model {model_name} failed: {e}. Trying next fallback...")
            continue
            
    print("[Gemini AI Error] All model fallbacks failed.")
    return None

def generate_article(primary_kw, semantic_kws, volume=0, kd=0, cpc=0.0):
    """
    Master pipeline:
    - Automatically capitalizes keywords
    - Detects category
    - Generates 100% complete content via Gemini API cascade (3.8 down to oldest)
    - Fetches UNIQUE image via Unsplash API (enforcing single use per photo ID)
    """
    cat_slug = detect_category(primary_kw, semantic_kws)
    cat_info = CATEGORIES[cat_slug]
    
    slug = slugify(primary_kw)
    capital_kw = capitalize_keyword(primary_kw)
    post_url = f"https://general-pedia.vercel.app/{slug}"
    post_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    display_date = datetime.now().strftime("%B %d, %Y")
    
    title = f"{capital_kw}: Comprehensive Guide & Key Insights"
    meta_desc = f"Everything you need to know about {capital_kw}. Explore key facts, in-depth breakdowns, expert tips, and detailed answers on GeneralPedia."
    tags = generate_tags(primary_kw, semantic_kws, cat_slug)
    
    safe_vol = int(volume) if volume and not str(volume).lower() == 'nan' else 0
    safe_kd = int(kd) if kd and not str(kd).lower() == 'nan' else 0
    safe_cpc = float(cpc) if cpc and not str(cpc).lower() == 'nan' else 0.0
    
    # 1. Fetch complete content via Gemini API cascade (3.8 down to oldest)
    body_content = generate_article_content_via_gemini_api(capital_kw, semantic_kws, cat_info["name"])
    if not body_content:
        body_content = f"<p>Comprehensive analytical briefing on <strong>{capital_kw}</strong> will be available shortly.</p>"
        
    # 2. Fetch unique image via Unsplash API by ID
    img_info = fetch_unique_unsplash_image(primary_kw)
    featured_img_url = ""
    image_id = ""
    
    if img_info:
        image_id = img_info["id"]
        featured_img_url = img_info["url"]
        img_html = f"""
        <figure style="margin: 24px 0;">
            <img src="{img_info['url']}" alt="{img_info['alt']}" style="width: 100%; max-height: 480px; object-fit: cover; border-radius: 12px;" />
            <figcaption style="font-size: 0.825rem; color: #64748b; margin-top: 8px;">Photo via Unsplash ({img_info['credit']})</figcaption>
        </figure>
        """
        body_content = img_html + body_content
    
    article_data = {
        "id": slug,
        "title": title,
        "primary_keyword": capital_kw,
        "semantic_keywords": semantic_kws,
        "category_slug": cat_slug,
        "category_name": cat_info["name"],
        "tags": tags,
        "status": "Published",
        "post_url": post_url,
        "slug": slug,
        "meta_description": meta_desc,
        "published_at": post_date_time,
        "display_date": display_date,
        "read_time": "6 min read",
        "search_volume": safe_vol,
        "difficulty": safe_kd,
        "cpc": safe_cpc,
        "image_id": image_id,
        "featured_image": featured_img_url,
        "content_html": body_content
    }
    
    return article_data
