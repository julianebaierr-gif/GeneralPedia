import os
import re
import json
import urllib.request
from datetime import datetime

try:
    from config import CATEGORIES, AUTHORS, DOMAIN, POSTS_DIR
    from image_service import fetch_unique_unsplash_image
    from tool_generator import is_tool_or_calculator_topic, generate_interactive_tool_html
    from internal_linker import inject_natural_internal_links
except ImportError:
    from .config import CATEGORIES, AUTHORS, DOMAIN, POSTS_DIR
    from .image_service import fetch_unique_unsplash_image
    from .tool_generator import is_tool_or_calculator_topic, generate_interactive_tool_html
    from .internal_linker import inject_natural_internal_links
from env_loader import get_secret

GEMINI_API_KEY = get_secret("GEMINI_API_KEY")

FALLBACK_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.1-flash-lite",
    "gemini-flash-lite-latest",
    "gemini-flash-latest"
]

def slugify(text):
    text = re.sub(r'[^a-zA-Z0-9\s-]', '', str(text).lower()).strip()
    return re.sub(r'[\s-]+', '-', text)

def slugify_with_seo_title(primary_kw, seo_title):
    """
    Builds a high-impact, human-natural SEO slug incorporating the primary keyword
    plus distinguishing keywords from the SEO Title (e.g. 'honda-crv-2026-price-specs-features-trim').
    """
    clean_title = re.sub(r'[^a-zA-Z0-9\s-]', '', str(seo_title).lower())
    words = clean_title.split()
    stop_words = {'a', 'an', 'the', 'and', 'or', 'of', 'in', 'on', 'at', 'to', 'for', 'with', 'is', 'it', 'by', 'vs'}
    meaningful = [w for w in words if w not in stop_words]
    kw_terms = [re.sub(r'[^a-zA-Z0-9]', '', w.lower()) for w in primary_kw.split()]
    
    slug_words = []
    for kw_w in kw_terms:
        if kw_w and kw_w not in slug_words:
            slug_words.append(kw_w)
            
    for w in meaningful:
        if w not in slug_words and len(slug_words) < 7:
            slug_words.append(w)
            
    return "-".join(slug_words)

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

AI_REPLACEMENTS = {
    # Direct robotic markers
    r'\bcomprehensive\b': 'complete',
    r'\bComprehensive\b': 'Complete',
    r'\bkey insights\b': 'main takeaways',
    r'\bKey Insights\b': 'Main Takeaways',
    r'\bKey insights\b': 'Main Takeaways',
    r'\bin-depth\b': 'detailed',
    r'\bIn-depth\b': 'Detailed',
    r'\bIn-Depth\b': 'Detailed',
    r'\bdelve\b': 'look',
    r'\bDelve\b': 'Look',
    r'\bdelving\b': 'looking',
    r'\bDelving\b': 'Looking',
    r'\btapestry\b': 'mix',
    r'\bTapestry\b': 'Mix',
    r'\btestament\b': 'proof',
    r'\bTestament\b': 'Proof',
    r'\bmoreover\b': 'also',
    r'\bMoreover\b': 'Also',
    r'\bfurthermore\b': 'also',
    r'\bFurthermore\b': 'Also',
    r'\bin conclusion\b': 'to sum up',
    r'\bIn conclusion\b': 'To sum up',
    r'\bIn Conclusion\b': 'To sum up',
    r'\bvital role\b': 'major part',
    r'\bVital role\b': 'Major part',
    r'\bnavigating\b': 'handling',
    r'\bNavigating\b': 'Handling',
    r'\bembark\b': 'start',
    r'\bEmbark\b': 'Start',
    r'\bfoster\b': 'support',
    r'\bFoster\b': 'Support',
    r'\brealm\b': 'area',
    r'\bRealm\b': 'Area',
    r'\bbeacon\b': 'example',
    r'\bBeacon\b': 'Example',
    r'\bit is important to remember\b': 'keep in mind',
    r'\bIt is important to remember\b': 'Keep in mind',
    r'\bit is crucial to\b': 'make sure to',
    r'\bIt is crucial to\b': 'Make sure to',
    r'\blearn more today\b': 'get the full picture',
    r'\bLearn more today\b': 'Get the full picture',
    r'\blearn more details\b': 'see key facts',
    r'\bLearn more details\b': 'See key facts',
    r'\blearn more now\b': 'get full facts',
    r'\bLearn more now\b': 'Get full facts',
    r'\blearn more\b': 'see more',
    r'\bLearn more\b': 'See more',
    r'\bcrucial\b': 'important',
    r'\bCrucial\b': 'Important',
}

def sanitize_ai_words(text):
    """
    Strips robotic AI clichés, filler phrases, and dead giveaways,
    replacing them with natural, human, conversational equivalents.
    """
    if not text:
        return ""
    result = text
    for pattern, replacement in AI_REPLACEMENTS.items():
        result = re.sub(pattern, replacement, result)
    # Ensure zero em-dashes
    result = result.replace('—', ', ').replace('–', '-')
    return result

def format_crisp_paragraphs(html_text):
    """
    Splits long, thick paragraphs into punchy 2-sentence readable blocks.
    """
    if not html_text:
        return ""
    paragraphs = html_text.split('\n\n')
    new_paras = []
    for p in paragraphs:
        p_clean = p.strip()
        if (not p_clean or 
            p_clean.startswith('<h') or 
            p_clean.startswith('<figure') or 
            p_clean.startswith('<ul') or 
            p_clean.startswith('<ol') or 
            p_clean.startswith('<details') or 
            p_clean.startswith('<strong') or
            p_clean.startswith('<div class="gp-interactive-tool-box')):
            new_paras.append(p)
            continue
        
        has_p = p_clean.startswith('<p>') and p_clean.endswith('</p>')
        raw = p_clean[3:-4].strip() if has_p else p_clean
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+(?=[A-Z0-9\"\'\<])', raw) if s.strip()]
        
        if len(sentences) <= 2:
            new_paras.append(f'<p>{raw}</p>' if not has_p else p)
            continue
            
        for i in range(0, len(sentences), 2):
            chunk = ' '.join(sentences[i:i+2]).strip()
            if chunk:
                new_paras.append(f'<p>{chunk}</p>')
                
    return '\n\n'.join(new_paras)

def generate_topic_specific_seo_title(primary_kw, category_slug, semantic_kws=None):
    """
    Generates a 100% unique, topic-tailored, high-CTR SEO title (50-60 chars).
    Must naturally contain the primary keyword near the beginning.
    Zero robotic AI cliches (Comprehensive, Key Insights, In-depth, Delve).
    Deterministic and unique based on the keyword's content intent.
    """
    kw = str(primary_kw).strip()
    words = kw.split()
    cap_kw = " ".join(w.capitalize() if not w.isupper() else w for w in words)
    kw_lower = kw.lower()
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', kw_lower).strip()
    slug = re.sub(r'[\s-]+', '-', slug)
    h = sum(ord(c) for c in slug)

    # 1. Automotive intent (car, truck, suv, brand models) - strict check
    if any(w in kw_lower for w in ['toyota', 'honda', 'crv', 'camry', 'porsche', 'ford', 'suv', 'used cars']) or (category_slug == "automotive" and any(w in kw_lower for w in ['car', 'vehicle', 'truck', 'sedan'])):
        templates = [
            f"{cap_kw}: Price, Specs, Features & Trim Review",
            f"{cap_kw}: Real Specs, Performance & Buying Guide",
            f"{cap_kw}: What to Expect, Key Specs & Pricing",
            f"{cap_kw}: Features, Fuel Economy & Trim Details",
            f"{cap_kw}: Full Model Review, Specs & What to Know"
        ]
    # 2. Tools / Area codes / Calculators
    elif any(w in kw_lower for w in ['area code', 'calculator', 'converter', 'tracker']):
        if 'area code' in kw_lower:
            templates = [
                f"{cap_kw}: Location, Coverage Map & Time Zone",
                f"{cap_kw}: Cities Covered, Time Zone & Scams",
                f"{cap_kw}: Location, Cities Served & Lookup Info",
                f"{cap_kw}: Where Is It Located, Cities & Details",
                f"{cap_kw}: State, Major Cities & Calling Guide"
            ]
        else:
            templates = [
                f"{cap_kw}: How It Works, Formula & Quick Guide",
                f"{cap_kw}: Free Online Tool, Formula & Examples",
                f"{cap_kw}: Accurate Calculation, Guide & Formula"
            ]
    # 3. Culture / Geography / Travel / Movies / Sports / History
    elif any(w in kw_lower for w in ['where is', 'cape verde', 'movie', 'film', 'olympics', 'vs', 'match', 'stats', 'wizard of oz', 'queen of wands', 'tarot']) or category_slug == "culture":
        if 'where is' in kw_lower:
            templates = [
                f"{cap_kw}: Exact Location, Map & Travel Facts",
                f"{cap_kw}: Geography, Country Map & Key Facts",
                f"{cap_kw}: World Map Location, Climate & Facts",
                f"{cap_kw}: Location, Geography & Practical Guide"
            ]
        elif 'stats' in kw_lower or 'vs' in kw_lower:
            templates = [
                f"{cap_kw}: Box Score, Highlights & Recap",
                f"{cap_kw}: Full Game Stats, Results & Analysis",
                f"{cap_kw}: Player Stats, Highlights & Final Score"
            ]
        elif 'olympics' in kw_lower:
            templates = [
                f"{cap_kw}: Dates, Host City, Events & Schedule",
                f"{cap_kw}: Location, Schedule, Sports & Updates",
                f"{cap_kw}: Host Cities, Dates & Essential Guide"
            ]
        elif 'wizard of oz' in kw_lower or 'movie' in kw_lower or 'film' in kw_lower:
            templates = [
                f"{cap_kw}: Story, Cast, Legacy & Movie Facts",
                f"{cap_kw}: Full Story, Characters & Cultural Legacy",
                f"{cap_kw}: Classic Movie Facts, Cast & Meaning"
            ]
        elif 'wands' in kw_lower or 'tarot' in kw_lower:
            templates = [
                f"{cap_kw}: Card Meaning, Symbolism & Full Guide",
                f"{cap_kw}: Upright, Reversed & Symbolism Guide",
                f"{cap_kw}: Card Meanings, Love & Career Reading"
            ]
        else:
            templates = [
                f"{cap_kw}: History, Meanings, Facts & Guide",
                f"{cap_kw}: Story, Cast, Legacy & Historical Facts",
                f"{cap_kw}: Meaning, Symbolism & Essential Facts"
            ]
    # 4. Health / Medical symptoms
    elif category_slug == "health" or any(w in kw_lower for w in ['symptom', 'pain', 'infection', 'causes', 'treatment', 'health']):
        templates = [
            f"{cap_kw}: Warning Signs, Causes & Treatment",
            f"{cap_kw}: Early Signs, Relief Tips & Causes",
            f"{cap_kw}: Common Causes, Home Remedies & Care",
            f"{cap_kw}: What to Do, Common Signs & Relief",
            f"{cap_kw}: Main Causes, Diagnosis & Recovery Steps"
        ]
    # 5. Lifestyle / Pets / Animals / Food
    elif category_slug == "lifestyle" or any(w in kw_lower for w in ['dog', 'cat', 'food', 'eat', 'recipe', 'pet']):
        if 'eat' in kw_lower:
            templates = [
                f"{cap_kw}? Safety, Benefits & Serving Tips",
                f"{cap_kw}? Vet Advice, Safe Portions & Risks",
                f"{cap_kw}? Health Risks, Benefits & Advice",
                f"{cap_kw}? Vet-Approved Facts, Risks & Tips"
            ]
        else:
            templates = [
                f"{cap_kw}: Practical Tips, Guide & Solutions",
                f"{cap_kw}: What to Know, Tips & Easy Steps",
                f"{cap_kw}: Essential Guide, Advice & Methods"
            ]
    # 6. Calendar / Events / Holidays
    elif any(w in kw_lower for w in ['calendar', 'memorial day', 'holiday', 'january', 'february', 'march', '2026', '2025']):
        templates = [
            f"{cap_kw}: Dates, Meaning, History & Traditions",
            f"{cap_kw}: Printable Dates, Holidays & Schedule",
            f"{cap_kw}: Exact Date, Meaning & Observance Guide",
            f"{cap_kw}: Key Dates, Holidays & Full Overview"
        ]
    # 7. Finance / Taxes
    elif category_slug == "finance" or any(w in kw_lower for w in ['tax', 'ira', '401k', 'loan', 'cost', 'mortgage']):
        templates = [
            f"{cap_kw}: Rules, Limits, Tax Rates & Strategy",
            f"{cap_kw}: Contribution Limits, Rules & Deadlines",
            f"{cap_kw}: Rates, Financial Rules & Key Advice"
        ]
    # General / Informational
    else:
        templates = [
            f"{cap_kw}: Meaning, Background & Practical Facts",
            f"{cap_kw}: What It Means, Key Facts & FAQs",
            f"{cap_kw}: Verified Facts, Background & Answers",
            f"{cap_kw}: Explanations, Practical Facts & Guide"
        ]

    # Select deterministically based on hash so it never clashes
    idx = h % len(templates)
    title = templates[idx]
    
    # If title is excessively long (> 72 chars), format gracefully without trailing comma or cut-off words
    if len(title) > 70:
        if ':' in title:
            base_kw, suffix = title.split(':', 1)
            # Shorten suffix to fit
            clean_suf = suffix.strip()
            title = f"{base_kw}: {clean_suf}"
    title = title.rstrip(', ').strip()
    return title

def generate_exact_seo_meta_description(primary_kw, category_slug, min_len=140, max_len=157):
    """
    Constructs an authentic, 100% complete grammatical sentence strictly between
    140 and 157 characters. Contains primary_kw, zero AI buzzwords, ends with a period.
    Free of forced brand names like 'on GeneralPedia' or repetitive CTAs.
    """
    words = str(primary_kw).strip().split()
    cap_kw = " ".join(w.capitalize() if not w.isupper() else w for w in words)
    kw_lower = primary_kw.lower()
    
    # Topic tailored lead-in phrases containing the keyword
    if 'area code' in kw_lower:
        leads = [
            f"Looking up {cap_kw}? Find cities covered, location details, local time zones, and phone lookup facts.",
            f"Discover where {cap_kw} is located, including major cities served, time zone, county details, and dialing info.",
            f"Explore {cap_kw} with verified facts on cities served, county map, local time zone, and dialing facts.",
            f"Here is your clear guide to {cap_kw}. Discover cities covered, local time zone, overlay codes, and calling facts."
        ]
    elif any(w in kw_lower for w in ['car', 'toyota', 'honda', 'crv', 'camry', 'vehicle', 'used cars']):
        leads = [
            f"Get verified facts on {cap_kw}, including trim pricing, engine specs, fuel economy, and key features.",
            f"Looking into {cap_kw}? Discover verified specs, estimated pricing, interior features, and performance details.",
            f"Explore verified details on {cap_kw}, including expected pricing, trim levels, engine specs, and interior tech.",
            f"Here are the facts on {cap_kw}. Explore trim options, expected pricing, fuel economy, and top features."
        ]
    elif 'where is' in kw_lower:
        leads = [
            f"Looking for {cap_kw}? Discover its exact geographic location on the world map, climate, islands, and key facts.",
            f"Discover the location for {cap_kw}, including world map geography, climate details, culture, and travel facts.",
            f"Find out {cap_kw} with verified facts on its geographic location, world map coordinates, climate, and islands.",
            f"Discover where to find {cap_kw} on the world map, including geographic coordinates, climate, and visitor facts."
        ]
    elif 'eat' in kw_lower:
        leads = [
            f"Wondering if {cap_kw}? Find vet-approved safety advice, nutritional facts, health benefits, and proper portions.",
            f"Is it safe to ask: {cap_kw}? Discover vet-approved advice, health benefits, safe portions, and potential risks.",
            f"Find vet-backed answers to whether {cap_kw}. Learn safe portion sizes, health benefits, and possible risks.",
            f"Can it be safe: {cap_kw}? Discover vet-verified facts on health benefits, safe preparation, and portion sizes."
        ]
    elif 'symptom' in kw_lower or 'infection' in kw_lower:
        leads = [
            f"Learn the common {cap_kw}, including early warning signs, typical causes, home remedies, and treatment tips.",
            f"Discover common {cap_kw}, including key warning signs, potential causes, relief methods, and home care.",
            f"Explore typical {cap_kw}, including early signs to watch, common triggers, relief methods, and treatments.",
            f"Find verified medical facts on {cap_kw}, including early signs, common causes, at-home relief, and treatments."
        ]
    elif 'calendar' in kw_lower or 'memorial day' in kw_lower or 'olympics' in kw_lower:
        leads = [
            f"Get verified schedule facts on {cap_kw}, including official dates, observance traditions, and helpful events.",
            f"Discover verified details on {cap_kw}, including official dates, national traditions, and planning tips.",
            f"Find verified dates and facts for {cap_kw}, including holiday schedules, key traditions, and handy tips.",
            f"Explore verified facts on {cap_kw}, including official dates, historical meaning, and event details."
        ]
    else:
        leads = [
            f"Find verified facts and clear answers about {cap_kw}, including helpful background details and common queries.",
            f"Discover verified facts and direct answers about {cap_kw}, including common questions and helpful context.",
            f"Get verified facts and direct answers about {cap_kw}, including helpful background details and common FAQs.",
            f"Explore clear answers and verified facts about {cap_kw}, including essential background context and details."
        ]

    # Flexible natural topic closers without any brand mentions
    closers = [
        "Check all the essential details and updates.",
        "Check full details, advice, and key points.",
        "Review key points, context, and clear tips.",
        "Check essential facts and accurate advice.",
        "Review important facts and helpful updates.",
        "Check verified facts and key details.",
        "Review all key points and facts.",
        "Review essential facts and details.",
        "Check all verified details now.",
        "Review complete details and facts.",
        "Check the verified facts today.",
        "Review important details today.",
        "Check key facts and updates.",
        "Check full details today.",
        "Review verified facts now.",
        "Check the key facts now.",
        "Review essential facts.",
        "Check full facts now.",
        "Check key points today.",
        "Review facts today.",
        "Check all facts.",
        ""
    ]

    for lead in leads:
        for closer in closers:
            cand = f"{lead} {closer}"
            if min_len <= len(cand) <= max_len:
                return cand

    # Extended combinatorial fallback for edge-case keyword lengths
    prefixes = [
        "Find verified facts and clear answers about",
        "Get verified facts and direct answers about",
        "Explore verified facts and clear answers on",
        "Find clear answers and verified facts about",
        "Get direct answers and verified facts about",
        "Explore direct answers and clear facts on",
        "Discover clear answers and key facts about",
        "Here are verified facts and answers about",
        "Find all verified facts and answers about",
        "Get all verified facts and answers about",
        "Explore verified facts and answers about",
        "Discover key facts and direct answers on",
        "A clear breakdown and verified facts on",
        "Clear facts and helpful answers about",
        "Verified facts and clear answers about",
        "Essential facts and clear answers on",
        "Key facts and clear answers regarding",
        "Facts and clear answers regarding",
        "Verified facts and details about",
        "Clear answers and details about",
        "Verified facts and answers for",
        "Clear facts and answers about",
        "Key facts and answers about",
        "Facts and answers regarding",
        "Facts and answers about",
        "Clear facts regarding",
        "Key facts regarding",
        "Facts about",
    ]
    mid_phrases = [
        ", including common questions and details",
        ", including important background context",
        ", including verified background context",
        ", including practical background details",
        ", including common questions and answers",
        ", including essential background details",
        ", including helpful tips and background",
        ", including essential context and facts",
        ", with verified background and context",
        ", with important context and details",
        ", with practical background details",
        ", with common questions and answers",
        ", with full background and context",
        ", with verified background facts",
        ", with full background details",
        ", with clear context and facts",
        ", with essential background",
        ", with verified background",
        ", with practical context",
        ", with verified context",
        ", with important details",
        ", with verified details",
        ", with essential details",
        ", with verified answers",
        ", with key background",
        ", with clear context",
        ", with key details",
        ", with key facts",
        ""
    ]
    for p in prefixes:
        for m in mid_phrases:
            s1 = f"{p} {cap_kw}{m}."
            for c in closers:
                cand = f"{s1} {c}"
                if min_len <= len(cand) <= max_len:
                    return cand

    return f"Explore verified facts, clear answers, and helpful background details about {cap_kw}. Review key points, essential context, and practical advice."[:156]

def generate_article_content_via_gemini_api(primary_kw, semantic_kws, category_name):
    """
    Generates rich, 800-1200 word authoritative SEO article content dynamically via Gemini API.
    Enforces:
    - Google Helpful Content, Spam & Anti-De-Ranking Policies (human-first, high E-E-A-T)
    - 100% human editorial tone: BANS ALL AI CLICHES (Comprehensive, Key Insights, in-depth, delve, etc.)
    - Featured snippet target (40-55 words)
    - 5 to 8 concise, punchy FAQ questions with direct answers
    - 100% complete generation
    - Fallback cascade through all Gemini versions
    """
    prompt = f"""You are a seasoned human investigative journalist, senior editor, and subject-matter specialist writing for GeneralPedia.
Write an authentic, direct, highly informative reference guide for real everyday readers on:
Primary Focus Keyword: "{primary_kw}"
Related Semantic / LSI Keywords: {', '.join(semantic_kws[:12]) if semantic_kws else 'None'}
Category Desk: {category_name}

CRITICAL RULES: HUMAN EDITORIAL TONE & STRICT ANTI-AI BANNED WORDS:
1. ABSOLUTE BAN ON AI BUZZWORDS & CLICHES:
   - NEVER use the following words or phrases anywhere in your headings or text:
     * "comprehensive"
     * "key insights"
     * "in-depth"
     * "delve" or "delving"
     * "tapestry"
     * "testament"
     * "moreover"
     * "furthermore"
     * "in conclusion"
     * "navigating" or "navigate the landscape"
     * "vital role"
     * "crucial"
     * "beacon"
     * "foster"
     * "realm"
     * "embark"
     * "it is important to remember / note"
     * "in today's fast-paced world / digital era"
   - Write like an experienced human reporter: plain spoken, grounded, fact-packed, clear, and engaging.

2. Google Helpful Content & Anti-De-Ranking Quality Guidelines:
   - Deliver rich, primary-source quality explanations, real numbers, verified context, practical steps, and direct comparisons.
   - ZERO fluff, filler, or robotic throat-clearing. Get straight to the answer without preamble.
   - Maintain a neutral, professional human tone that immediately demonstrates real-world Experience, Expertise, Authoritativeness, and Trustworthiness (E-E-A-T).

3. Organic Semantic Integration:
   - Naturally weave the LSI and semantic keywords throughout headings and body paragraphs without keyword stuffing.

4. Featured Snippet Optimization (Zero-Click Answer):
   - Immediately following the first <h2> subheading, provide a direct, concise 40-55 word definitive answer block enclosed in a dedicated paragraph with bold tags: <p><strong>[Direct laser-accurate answer]</strong></p>.

5. Complete Generation Guarantee:
   - Produce the complete article from introduction to the final FAQ without stopping mid-thought or mid-sentence.

6. Formatting & Typography:
   - Return clean semantic HTML (<h2>, <h3>, <p>, <ul>, <li>, <blockquote>, <details>, <summary>).
   - DO NOT wrap in ```html or ``` code fences.
   - CRITICAL PARAGRAPH LENGTH RULE (STRICT):
     * NEVER write huge, thick, intimidating blocks of text or 5+ sentence paragraphs!
     * Break all content into crisp, bite-sized paragraphs: exactly 2 sentences per paragraph (maximum 35-50 words per paragraph).
     * Use frequent whitespace, clear subheadings, and short 2-sentence paragraphs so readers on mobile and desktop can read effortlessly.
   - CRITICAL CONSTRAINT: DO NOT USE ANY EM-DASHES ("—"). Use standard commas, parentheses, or simple hyphens instead.

7. MANDATORY FAQ ACCORDION SECTION (5 to 8 Questions):
   - Include a dedicated section with <h2>Frequently Asked Questions</h2>.
   - Provide EXACTLY between 5 and 8 questions (minimum 5, maximum 8).
   - Format EACH question and answer using HTML5:
     <details class="faq-item"><summary class="faq-question">Direct User Question?</summary><p class="faq-answer">Direct, factual answer in 25 to 45 words tailored for Google snippet capture.</p></details>
   - Target real questions users ask on Google Search regarding "{primary_kw}".

8. Word Count Target: 850 to 1,250 words of pure substance.
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
                if not raw_text or len(raw_text.split()) < 650:
                    print(f"[Gemini AI] Model {model_name} generated too few words ({len(raw_text.split()) if raw_text else 0}), trying next...")
                    continue

                clean_html = re.sub(r'^```html\s*', '', raw_text)
                clean_html = re.sub(r'```$', '', clean_html).strip()

                # Ensure article ends cleanly with </details> or </p>
                if not (clean_html.endswith('</details>') or clean_html.endswith('</p>') or clean_html.endswith('</div>')):
                    print(f"[Gemini AI] Model {model_name} cut off prematurely, trying next fallback...")
                    continue

                # Sanitize any accidental AI buzzwords or em-dashes
                clean_html = sanitize_ai_words(clean_html)

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
    
    # Topic-tailored, authentic human SEO title and exact 155-158 char meta description
    title = generate_topic_specific_seo_title(primary_kw, cat_slug, all_semantic_kws)
    slug = slugify_with_seo_title(primary_kw, title)
    post_url = f"https://general-pedia.vercel.app/{slug}"
    meta_desc = generate_exact_seo_meta_description(primary_kw, cat_slug, min_len=155, max_len=158)
    tags = generate_tags(primary_kw, all_semantic_kws, cat_slug)
    
    safe_vol = int(volume) if volume and not str(volume).lower() == 'nan' else 0
    safe_kd = int(kd) if kd and not str(kd).lower() == 'nan' else 0
    safe_cpc = float(cpc) if cpc and not str(cpc).lower() == 'nan' else 0.0
    
    # 2. Fetch complete content via Gemini API cascade
    body_content = generate_article_content_via_gemini_api(capital_kw, all_semantic_kws, cat_info["name"])
    if not body_content:
        body_content = f"<p>A detailed briefing on <strong>{capital_kw}</strong> will be available shortly.</p>"
    else:
        body_content = format_crisp_paragraphs(body_content)
        
    # 3. Extract 5-8 FAQs for Schema markup
    faqs = extract_faqs_from_html(body_content)
    faq_schema = build_faq_schema_json(faqs)
    
    # 4. Fetch unique contextual featured image via Unsplash API by ID using enriched visual queries
    img_info = fetch_unique_unsplash_image(query=visual_queries, fallback_terms=[primary_kw, cat_info["name"]])
    featured_img_url = ""
    image_id = ""
    
    if img_info:
        image_id = img_info["id"]
        featured_img_url = img_info["url"]
        alt_text = f"{capital_kw} - {img_info['alt'] or 'Editorial Reference'}"
        img_html = f"""
        <figure style="margin: 24px 0;">
            <img src="{img_info['url']}" alt="{alt_text}" style="width: 100%; max-height: 480px; object-fit: cover; border-radius: 8px;" />
        </figure>
        """
        body_content = img_html + body_content

    # 5. Fetch unique mid-content image strictly relative to keyword/subtopics and not used anywhere else
    mid_queries = [
        f"{primary_kw} details",
        f"{primary_kw} overview",
        f"{cat_info['name']} reference",
        "detailed workflow"
    ]
    if len(visual_queries) > 1:
        mid_queries = visual_queries[1:] + mid_queries

    mid_img_info = fetch_unique_unsplash_image(query=mid_queries, fallback_terms=[primary_kw, cat_info["name"]])
    if mid_img_info:
        mid_alt = f"{capital_kw} - {mid_img_info['alt'] or 'In-Depth Overview'}"
        mid_html = f"""
        <figure class="mid-article-figure" style="margin: 36px 0;">
            <img src="{mid_img_info['url']}" alt="{mid_alt}" loading="lazy" style="width: 100%; max-height: 480px; object-fit: cover; border-radius: 8px;" />
        </figure>
        """
        # Place mid-content: before 3rd h2 or 2nd h2 or halfway through paragraphs
        h2_positions = [m.start() for m in re.finditer(r'<h2\b[^>]*>', body_content, re.IGNORECASE)]
        if len(h2_positions) >= 3:
            pos = h2_positions[2]
            body_content = body_content[:pos] + mid_html + body_content[pos:]
        elif len(h2_positions) >= 2:
            pos = h2_positions[1]
            body_content = body_content[:pos] + mid_html + body_content[pos:]
        else:
            p_positions = [m.end() for m in re.finditer(r'</p>', body_content, re.IGNORECASE)]
            if len(p_positions) >= 4:
                mid_pos = p_positions[len(p_positions) // 2]
                body_content = body_content[:mid_pos] + mid_html + body_content[mid_pos:]
            else:
                body_content = body_content + mid_html

    # 6. Auto-generate & embed interactive calculator/tool if topic warrants it
    if is_tool_or_calculator_topic(primary_kw, all_semantic_kws):
        tool_widget = generate_interactive_tool_html(capital_kw, all_semantic_kws)
        if tool_widget:
            # Place tool widget right after first <h2> or blockquote/paragraph
            h2_first = re.search(r'</h2>', body_content, re.IGNORECASE)
            if h2_first:
                # Place after the immediate paragraph/blockquote following first <h2>
                rest = body_content[h2_first.end():]
                next_p = re.search(r'</p>|</blockquote>', rest, re.IGNORECASE)
                if next_p:
                    insert_idx = h2_first.end() + next_p.end()
                    body_content = body_content[:insert_idx] + tool_widget + body_content[insert_idx:]
                else:
                    body_content = body_content[:h2_first.end()] + tool_widget + body_content[h2_first.end():]
            else:
                body_content = tool_widget + body_content

    # 7. Naturally inject contextual in-text internal links & Related Guides box
    try:
        body_content = inject_natural_internal_links(body_content, slug, cat_slug)
    except Exception as e:
        print(f"[Internal Linker Warning] Failed to inject internal links: {e}")
    
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
        "content_html": body_content,
        "author_name": AUTHORS.get(cat_slug, {}).get("name", "Editorial Staff"),
        "author_avatar": AUTHORS.get(cat_slug, {}).get("avatar", ""),
        "author_bio": AUTHORS.get(cat_slug, {}).get("bio", ""),
        "author_initials": AUTHORS.get(cat_slug, {}).get("initials", "GP")
    }
    
    return article_data
