import os
import re
import json
from datetime import datetime
try:
    from config import CATEGORIES, DOMAIN, POSTS_DIR
except ImportError:
    from .config import CATEGORIES, DOMAIN, POSTS_DIR

def slugify(text):
    text = re.sub(r'[^a-zA-Z0-9\s-]', '', str(text).lower()).strip()
    return re.sub(r'[\s-]+', '-', text)

def detect_category(primary_kw, semantic_kws):
    # Check primary keyword first, then semantic
    kw = primary_kw.lower()
    full = (primary_kw + " " + " ".join(semantic_kws[:3])).lower()
    
    # 1. Calculators & Tools
    if any(w in kw for w in ['calculator', 'converter', 'calendar', 'tracker', 'depth chart', 'to ml', 'to gallon', 'to inches']):
        return "tools"
    
    # 2. Sports & Entertainment
    if any(w in kw for w in ['vs', 'match', 'stats', 'movie', 'film', 'cast', 'season', 'olympics', 'world cup', 'nfl', 'nba', 'game', 'show', 'wizard of oz']):
        return "culture"
    
    # 3. Automotive
    if any(w in kw for w in ['car', 'toyota', 'honda', 'tesla', 'ford', 'suv', 'truck', 'dodge', 'tire', 'vehicle', 'accord', 'camry', 'corolla', 'porsche', 'bmw']):
        return "automotive"
        
    # 4. Lifestyle & Pets & Home
    if any(w in kw for w in ['dog', 'cat', 'pet', 'recipe', 'coffee', 'food', 'tea', 'cleaning', 'cook', 'bake', 'dryer vent', 'couch', 'home', 'drain']):
        return "lifestyle"
        
    # 5. Health & Medical
    if any(w in kw for w in ['symptom', 'disease', 'infection', 'syndrome', 'massage', 'vitamin', 'pain', 'treatment', 'causes', 'medicine', 'diet', 'health', 'cancer', 'thrush', 'sore']):
        return "health"
        
    # 6. Finance & Money
    if any(w in kw for w in ['tax', 'ira', '401k', 'insurance', 'loan', 'mortgage', 'equity', 'salary', 'income', 'refund', 'money', 'credit', 'bank', 'cost of']):
        return "finance"
        
    # 7. How-To & Guides
    if any(w in kw for w in ['how to', 'what is', 'how many', 'how much', 'why do', 'meaning', 'difference between', 'definition']):
        return "how-to"
        
    # 8. Tech & Digital
    if any(w in kw for w in ['software', 'app', 'malware', 'code', 'phone', 'laptop', 'android', 'tech', 'ai ']):
        return "tech"
        
    return "how-to"

def generate_tags(primary_kw, semantic_kws, category_slug):
    tags = set()
    cat_name = CATEGORIES[category_slug]["name"]
    tags.add(cat_name)
    
    for kw in [primary_kw] + semantic_kws[:5]:
        clean = re.sub(r'[^a-zA-Z0-9\s]', '', kw).strip()
        words = clean.split()
        if 1 <= len(words) <= 3:
            tags.add(clean.title())
        elif len(words) > 3:
            tags.add(" ".join(words[:2]).title())
            
    return list(tags)[:6]

def generate_article(primary_kw, semantic_kws, volume=0, kd=0, cpc=0.0):
    cat_slug = detect_category(primary_kw, semantic_kws)
    cat_info = CATEGORIES[cat_slug]
    
    slug = slugify(primary_kw)
    post_url = f"{DOMAIN}/{cat_slug}/{slug}"
    post_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    display_date = datetime.now().strftime("%B %d, %Y")
    
    title = f"{primary_kw.title()}: Complete Comprehensive Guide & Insights"
    meta_desc = f"Everything you need to know about {primary_kw}. Explore key facts, in-depth breakdowns, expert tips, and detailed answers on GeneralPedia."
    
    tags = generate_tags(primary_kw, semantic_kws, cat_slug)
    
    safe_vol = int(volume) if volume and not str(volume).lower() == 'nan' else 0
    safe_kd = int(kd) if kd and not str(kd).lower() == 'nan' else 0
    safe_cpc = float(cpc) if cpc and not str(cpc).lower() == 'nan' else 0.0
    
    sections = []
    
    sec1 = f"""
    <div class="prose max-w-none text-slate-700 leading-relaxed space-y-4">
        <p class="text-lg font-medium text-slate-800 leading-relaxed">
            Understanding <strong>{primary_kw}</strong> has become increasingly critical for readers seeking practical knowledge, reliable data, and actionable steps. In this authoritative GeneralPedia guide, we break down essential insights, practical strategies, and everything you need to navigate this topic successfully.
        </p>
        <div class="my-6 p-5 bg-emerald-50 border-l-4 border-emerald-500 rounded-r-xl">
            <h4 class="font-semibold text-emerald-900 mb-1 flex items-center gap-2">
                <i class="fa-solid fa-lightbulb text-emerald-600"></i> Key Takeaway
            </h4>
            <p class="text-sm text-emerald-800">
                Whether you are exploring solutions for the first time or optimizing your strategy, mastering <strong>{primary_kw}</strong> provides long-term clarity and significant practical advantages.
            </p>
        </div>
    </div>
    """
    sections.append(sec1)
    
    if semantic_kws:
        sub_sections = ""
        for i, skw in enumerate(semantic_kws[:5]):
            sub_sections += f"""
            <div class="mt-8">
                <h3 class="text-xl font-bold text-slate-800 mb-3 flex items-center gap-2">
                    <span class="w-8 h-8 rounded-lg bg-slate-100 text-slate-700 flex items-center justify-center text-sm font-semibold">{i+1}</span>
                    {skw.title()}
                </h3>
                <p class="text-slate-600 leading-relaxed mb-4">
                    When addressing <em>{primary_kw}</em>, a major consideration is <strong>{skw}</strong>. Experts emphasize looking into relevant criteria, key metrics, and step-by-step best practices to ensure optimal results.
                </p>
                <ul class="list-disc pl-6 space-y-2 text-slate-600">
                    <li>Core factors to evaluate when analyzing <strong>{skw}</strong>.</li>
                    <li>Common pitfalls to avoid and how to streamline the process efficiently.</li>
                    <li>Actionable recommendations tailored for everyday readers and specialists alike.</li>
                </ul>
            </div>
            """
        sections.append(f"""
        <div class="mt-10">
            <h2 class="text-2xl font-bold text-slate-900 mb-4 pb-2 border-b border-slate-200">
                Detailed Analysis & Key Elements
            </h2>
            {sub_sections}
        </div>
        """)
        
    faq_items = [
        {
            "q": f"What is the significance of {primary_kw}?",
            "a": f"{primary_kw.capitalize()} provides essential clarity, helping users make informed decisions backed by verified knowledge and practical application."
        },
        {
            "q": f"How does {semantic_kws[0] if semantic_kws else 'this topic'} relate to the overall picture?",
            "a": f"Understanding related factors such as {semantic_kws[0] if semantic_kws else primary_kw} ensures a comprehensive overview without overlooking vital details."
        },
        {
            "q": f"Where can I find more updates on {primary_kw}?",
            "a": f"Stay bookmarked to GeneralPedia.com for continuously updated references, in-depth breakdowns, and real-time guides."
        }
    ]
    
    faq_html = """<div class="mt-12 bg-slate-50 border border-slate-200 rounded-2xl p-6">
        <h3 class="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
            <i class="fa-solid fa-circle-question text-emerald-600"></i> Frequently Asked Questions
        </h3>
        <div class="space-y-4">
    """
    for item in faq_items:
        faq_html += f"""
            <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
                <h4 class="font-semibold text-slate-800 mb-2">{item['q']}</h4>
                <p class="text-slate-600 text-sm leading-relaxed">{item['a']}</p>
            </div>
        """
    faq_html += "</div></div>"
    sections.append(faq_html)
    
    body_content = "\n".join(sections)
    
    article_data = {
        "id": slug,
        "title": title,
        "primary_keyword": primary_kw,
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
        "read_time": "5 min read",
        "search_volume": safe_vol,
        "difficulty": safe_kd,
        "cpc": safe_cpc,
        "content_html": body_content
    }
    
    return article_data
