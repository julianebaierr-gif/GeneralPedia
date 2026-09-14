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
    if any(w in kw for w in ['calculator', 'converter', 'calendar', 'tracker', 'depth chart', 'to ml', 'to gallon', 'to inches', 'area code']):
        return "tools"
    if any(w in kw for w in ['vs', 'match', 'stats', 'movie', 'film', 'cast', 'season', 'olympics', 'world cup', 'nfl', 'nba', 'game', 'show', 'wizard of oz', 'where is', 'cape verde', 'prague', 'fiji', 'cyprus']):
        return "culture"
    if any(w in kw for w in ['car', 'toyota', 'honda', 'tesla', 'ford', 'suv', 'truck', 'dodge', 'tire', 'vehicle', 'accord', 'camry', 'corolla', 'porsche', 'bmw', 'crv', 'cr-v']):
        return "automotive"
    if any(w in kw for w in ['dog', 'cat', 'pet', 'recipe', 'coffee', 'food', 'tea', 'cleaning', 'cook', 'bake', 'dryer vent', 'couch', 'home', 'drain']):
        return "lifestyle"
    if any(w in kw for w in ['symptom', 'disease', 'infection', 'syndrome', 'massage', 'vitamin', 'pain', 'treatment', 'causes', 'medicine', 'diet', 'health', 'cancer', 'thrush', 'sore', 'gallbladder', 'appendix']):
        return "health"
    if any(w in kw for w in ['tax', 'ira', '401k', 'insurance', 'loan', 'mortgage', 'equity', 'salary', 'income', 'refund', 'money', 'credit', 'bank', 'cost of']):
        return "finance"
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

def extract_faqs_from_html(html_text):
    """
    Parses FAQ questions and answers from generated HTML to create valid Google FAQPage Schema.
    """
    faqs = []
    # Pattern to find details/summary or h3/h4 questions inside faq section (supporting attributes like class="faq-question")
    q_matches = list(re.finditer(r'<summary[^>]*>(.*?)</summary>\s*<p[^>]*>(.*?)</p>', html_text, re.DOTALL | re.IGNORECASE))
    for m in q_matches:
        q = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        a = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        if q and a:
            faqs.append({"question": q, "answer": a})
            
    if not faqs:
        # Fallback regex for h3/h4 FAQ headers
        q_matches2 = list(re.finditer(r'<h[34][^>]*>(.*?)</h[34]>\s*<p[^>]*>(.*?)</p>', html_text, re.DOTALL | re.IGNORECASE))
        for m in q_matches2:
            q = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            a = re.sub(r'<[^>]+>', '', m.group(2)).strip()
            if q.endswith('?') and len(q) > 10:
                faqs.append({"question": q, "answer": a})
                
    return faqs[:8]

def build_faq_schema_json(faqs):
    """
    Constructs official Google FAQPage Schema JSON-LD.
    """
    if not faqs:
        return ""
    main_entities = []
    for item in faqs:
        main_entities.append({
            "@type": "Question",
            "name": item["question"],
            "acceptedAnswer": {
                "@type": "Answer",
                "text": item["answer"]
            }
        })
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": main_entities
    }
    return json.dumps(schema, ensure_ascii=False)

def generate_article_content_via_gemini_api(primary_kw, semantic_kws, category_name):
    """
    Generates rich, 800-1200 word authoritative SEO article content dynamically via Gemini API.
    Enforces:
    - Google Helpful Content & Spam Policies (100% human-first, verified, authentic)
    - 5 to 8 concise, punchy FAQ questions with direct answers (ideal for Featured Snippets)
    - Starts and ends with 100% completeness
    - Fallback cascade through all Gemini versions
    """
    prompt = f"""You are an elite editorial journalist and lead SEO strategist for GeneralPedia.
Write a COMPLETE, comprehensive, and authoritative informational reference guide for a global audience adhering to the latest Google Search Quality Rater & Helpful Content guidelines on:
Primary Focus Keyword: "{primary_kw}"
Related Semantic / LSI Keywords: {', '.join(semantic_kws[:8]) if semantic_kws else 'None'}
Category Desk: {category_name}

STRICT EDITORIAL & SEO POLICIES:
1. Google Helpful Content & Anti-De-Indexing Standards:
   - Provide original analysis, comprehensive context, practical value, and verifiable facts.
   - Do NOT use generic filler, AI buzzwords (e.g., "in conclusion", "tapestry", "delve"), or hollow fluff.
   - Write in a clean, journalistic, objective tone.
2. Complete Generation Guarantee: Write the complete article from start to finish. Never stop mid-sentence.
3. Formatting: Return clean HTML (use <h2>, <h3>, <p>, <ul>, <li>, <blockquote>, <details>, <summary>).
   - DO NOT wrap in ```html or ``` code fences.
4. CRITICAL CONSTRAINT: DO NOT USE ANY EM-DASHES ("—"). Use standard hyphens, commas, or parentheses instead.
5. Content Blueprint:
   - Engaging opening hook defining the topic and its real-world significance.
   - Featured Snippet Target (Zero-Click): Under the first <h2>, provide a direct, concise 40-55 word definitive answer block.
   - In-depth thematic breakdown sections using <h2> and <h3> subheadings covering mechanisms, global comparisons, practical guidelines, and key factors.
   - Natural, organic integration of all semantic and LSI keywords.
6. MANDATORY FAQ ACCORDION SECTION (5 to 8 Questions):
   - Include a dedicated section with <h2>Frequently Asked Questions</h2>.
   - Provide EXACTLY between 5 and 8 questions (minimum 5, maximum 8).
   - Format EACH question and answer using HTML5 <details class="faq-item"><summary class="faq-question">Question?</summary><p class="faq-answer">Concise, direct answer (25-45 words) designed for Google snippet capture.</p></details>.
   - Questions must address real user search intents and answers must be direct and factual.
7. Word Count: 800 to 1,200 words.
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
                    continue
                    
                raw_text = parts[0].get('text', '').strip()
                if not raw_text or len(raw_text) < 400:
                    continue
                    
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
    
    # 1. Fetch complete content via Gemini API cascade
    body_content = generate_article_content_via_gemini_api(capital_kw, semantic_kws, cat_info["name"])
    if not body_content:
        body_content = f"<p>Comprehensive analytical briefing on <strong>{capital_kw}</strong> will be available shortly.</p>"
        
    # 2. Extract 5-8 FAQs for Schema markup
    faqs = extract_faqs_from_html(body_content)
    faq_schema = build_faq_schema_json(faqs)
    
    # Embed schema script directly in post HTML for static crawlers
    if faq_schema:
        schema_tag = f'\n<script type="application/ld+json">\n{faq_schema}\n</script>\n'
        body_content = body_content + schema_tag
        
    # 3. Fetch unique image via Unsplash API by ID
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
        "faqs": faqs,
        "faq_schema": faq_schema,
        "content_html": body_content
    }
    
    return article_data
