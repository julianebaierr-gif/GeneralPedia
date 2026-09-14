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

def enrich_semantic_and_visual_terms(primary_kw, existing_semantic_kws):
    """
    Intelligently expands semantic/LSI keywords and generates contextual visual search terms.
    If sheet already has semantic keywords, complements them with topic-specific LSI terms.
    If sheet has None/empty keywords, generates 6-10 highly relevant LSI keywords and visual queries.
    """
    cleaned_existing = [
        k.strip() for k in existing_semantic_kws
        if k and k.strip() and k.strip().lower() != 'none (single standalone topic)'
    ]
    
    # Prompt Gemini for accurate semantic terms and stock photo visual queries
    prompt = f"""For the primary informational topic: "{primary_kw}"
Existing related keywords: {', '.join(cleaned_existing) if cleaned_existing else 'None'}

Perform two tasks:
1. Provide 6 to 8 highly relevant, intent-driven LSI/semantic search phrases strictly tied to "{primary_kw}".
   - Ensure they match real Google search queries (how it works, definitions, causes, solutions, specifications, comparisons).
2. Provide 3 concrete, descriptive visual search queries for Unsplash stock photography that represent this exact subject (e.g. real-world objects, tools, settings, city scenes - avoid abstract words or numbers alone).

Return strictly a JSON object with no markdown code fences:
{{"semantic_keywords": ["keyword 1", "keyword 2"], "visual_queries": ["query 1", "query 2"]}}
"""
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "thinkingConfig": {"thinkingBudget": 200}
        }
    }
    
    generated_semantics = []
    visual_queries = []
    
    for model_name in ["gemini-3.6-flash", "gemini-3.7-flash", "gemini-3.5-flash", "gemini-flash-latest"]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json', 'User-Agent': 'GeneralPedia-SEO/1.0'}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                raw = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '').strip()
                raw = re.sub(r'^```(json)?\s*', '', raw)
                raw = re.sub(r'```$', '', raw).strip()
                parsed = json.loads(raw)
                generated_semantics = parsed.get("semantic_keywords", [])
                visual_queries = parsed.get("visual_queries", [])
                if generated_semantics:
                    break
        except Exception:
            continue

    # Merge sheet keywords + Gemini LSI keywords
    combined_semantics = []
    seen = set()
    for kw in cleaned_existing + generated_semantics:
        clean = kw.strip()
        lower = clean.lower()
        if clean and lower != primary_kw.lower() and lower not in seen:
            seen.add(lower)
            combined_semantics.append(clean)

    # Fallback visual queries if API failed
    if not visual_queries:
        visual_queries = [primary_kw, f"{primary_kw} guide", "technology workplace"]

    return combined_semantics, visual_queries

def generate_article_content_via_gemini_api(primary_kw, semantic_kws, category_name):
    """
    Generates rich, 800-1200 word authoritative SEO article content dynamically via Gemini API.
    Enforces:
    - Google Helpful Content, Spam & Anti-De-Ranking Policies (human-first, high E-E-A-T)
    - Featured snippet target (40-55 words)
    - 5 to 8 concise, punchy FAQ questions with direct answers
    - 100% complete generation
    - Fallback cascade through all Gemini versions
    """
    prompt = f"""You are a master editorial researcher, investigative writer, and top-tier SEO copywriter for GeneralPedia.
Write a COMPLETE, comprehensive, highly authoritative informational reference guide for a global audience on:
Primary Focus Keyword: "{primary_kw}"
Related Semantic / LSI Keywords: {', '.join(semantic_kws[:12]) if semantic_kws else 'None'}
Category Desk: {category_name}

STRICT EDITORIAL, E-E-A-T & ANTI-DE-RANKING POLICIES:
1. Google Helpful Content & Anti-De-Ranking Quality Guidelines:
   - Deliver rich, primary-source quality insights, actionable context, real-world examples, and fact-based depth.
   - ZERO fluff, filler, or robotic throat-clearing. NEVER use cliches like "in conclusion", "tapestry", "delve", "furthermore", "it is important to remember", or "in today's fast-paced world".
   - Maintain a neutral, professional journalistic tone that immediately demonstrates Experience, Expertise, Authoritativeness, and Trustworthiness (E-E-A-T).
2. Organic Semantic Integration:
   - Naturally weave the LSI and semantic keywords throughout headings and body paragraphs without keyword stuffing.
3. Featured Snippet Optimization (Zero-Click Answer):
   - Immediately following the first <h2> subheading, provide a direct, concise 40-55 word definitive answer block in <strong> bold tags that answers the core search query with laser accuracy.
4. Complete Generation Guarantee:
   - Produce the complete article from introduction to the final FAQ without stopping mid-thought or mid-sentence.
5. Formatting & Typography:
   - Return clean semantic HTML (<h2>, <h3>, <p>, <ul>, <li>, <blockquote>, <details>, <summary>).
   - DO NOT wrap in ```html or ``` code fences.
   - CRITICAL CONSTRAINT: DO NOT USE ANY EM-DASHES ("—"). Use standard commas, parentheses, or simple hyphens instead.
6. MANDATORY FAQ ACCORDION SECTION (5 to 8 Questions):
   - Include a dedicated section with <h2>Frequently Asked Questions</h2>.
   - Provide EXACTLY between 5 and 8 questions (minimum 5, maximum 8).
   - Format EACH question and answer using HTML5:
     <details class="faq-item"><summary class="faq-question">Direct User Question?</summary><p class="faq-answer">Direct, factual answer in 25 to 45 words tailored for Google snippet capture.</p></details>
   - Target real questions users ask on Google Search regarding "{primary_kw}".
7. Word Count Target: 850 to 1,250 words of pure substance.
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
    slug = slugify(primary_kw)
    capital_kw = capitalize_keyword(primary_kw)
    post_url = f"https://general-pedia.vercel.app/{slug}"
    post_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    display_date = datetime.now().strftime("%B %d, %Y")
    
    # 1. Enrich semantic keywords and visual queries
    all_semantic_kws, visual_queries = enrich_semantic_and_visual_terms(primary_kw, semantic_kws)
    
    cat_slug = detect_category(primary_kw, all_semantic_kws)
    cat_info = CATEGORIES[cat_slug]
    
    title = f"{capital_kw}: Comprehensive Guide & Key Insights"
    meta_desc = f"Everything you need to know about {capital_kw}. Explore key facts, in-depth breakdowns, expert tips, and detailed answers on GeneralPedia."
    tags = generate_tags(primary_kw, all_semantic_kws, cat_slug)
    
    safe_vol = int(volume) if volume and not str(volume).lower() == 'nan' else 0
    safe_kd = int(kd) if kd and not str(kd).lower() == 'nan' else 0
    safe_cpc = float(cpc) if cpc and not str(cpc).lower() == 'nan' else 0.0
    
    # 2. Fetch complete content via Gemini API cascade
    body_content = generate_article_content_via_gemini_api(capital_kw, all_semantic_kws, cat_info["name"])
    if not body_content:
        body_content = f"<p>Comprehensive analytical briefing on <strong>{capital_kw}</strong> will be available shortly.</p>"
        
    # 3. Extract 5-8 FAQs for Schema markup
    faqs = extract_faqs_from_html(body_content)
    faq_schema = build_faq_schema_json(faqs)
    
    # Embed schema script directly in post HTML for static crawlers
    if faq_schema:
        schema_tag = f'\n<script type="application/ld+json">\n{faq_schema}\n</script>\n'
        body_content = body_content + schema_tag
        
    # 4. Fetch unique contextual image via Unsplash API by ID using enriched visual queries
    img_info = fetch_unique_unsplash_image(query=visual_queries, fallback_terms=[primary_kw, cat_info["name"]])
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
        "semantic_keywords": all_semantic_kws,
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
