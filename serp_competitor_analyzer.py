import os
import re
import json
import urllib.request
import urllib.parse
from env_loader import get_secret

GEMINI_API_KEY = get_secret("GEMINI_API_KEY")

FALLBACK_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.7-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-flash-latest",
    "gemini-2.5-flash"
]

def fetch_top_competitors(keyword, max_results=8):
    """
    Retrieves real-time organic search engine competitor results (top 5 to 8)
    including rank, title, snippet, and source domain.
    Uses robust desktop headers to bypass bot detection without external paid APIs.
    """
    clean_kw = re.sub(r'[^\w\s-]', '', str(keyword)).strip()
    encoded_query = urllib.parse.quote(clean_kw)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/'
    }
    
    results = []
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            
            # Extract result titles and snippets from DDG HTML markup
            title_matches = re.findall(r'<h2 class="result__title">\s*<a[^>]*>(.*?)</a>', html, re.DOTALL)
            snippet_matches = re.findall(r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
            url_matches = re.findall(r'<a[^>]+class="result__url"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
            
            count = min(len(title_matches), max_results)
            for i in range(count):
                raw_title = re.sub(r'<[^>]+>', '', title_matches[i]).strip()
                raw_snippet = re.sub(r'<[^>]+>', '', snippet_matches[i]).strip() if i < len(snippet_matches) else ""
                raw_url = url_matches[i][1].strip() if i < len(url_matches) else ""
                
                # Filter out empty or duplicate entries
                if raw_title and len(raw_title) > 5:
                    results.append({
                        "rank": len(results) + 1,
                        "title": raw_title,
                        "snippet": raw_snippet,
                        "domain": raw_url.split('/')[0] if raw_url else "web"
                    })
                    if len(results) >= max_results:
                        break
                        
        print(f"[SERP Analyzer] Successfully fetched {len(results)} live competitor results for '{keyword}'.")
    except Exception as e:
        print(f"[SERP Analyzer Warning] Live SERP fetch encountered notice: {e}. Utilizing fallback intel.")
        
    return results

def generate_heuristic_50_plus_lsi(primary_kw, existing_semantic_kws=None):
    """
    Robust algorithmic fallback that generates 50+ high-relevance LSI/semantic terms
    and comprehensive content gaps across intent categories.
    Guarantees the publishing pipeline NEVER crashes if external APIs are offline.
    """
    kw = primary_kw.strip()
    words = [w for w in re.split(r'\s+', kw.lower()) if w]
    stem = " ".join(words)
    
    # 1. Core Intent Variations & Synonyms
    variations = [
        f"{stem} meaning",
        f"{stem} overview",
        f"{stem} definition",
        f"{stem} key facts",
        f"{stem} explained",
        f"{stem} full breakdown",
        f"{stem} step by step",
        f"{stem} practical tips",
        f"{stem} essential details",
        f"{stem} real-world examples",
        f"{stem} standard rules",
        f"{stem} comparison",
        f"{stem} advantages and limits",
        f"{stem} common issues",
        f"{stem} verified facts"
    ]
    
    # 2. User Questions & Problem Solving
    questions = [
        f"what is {stem}",
        f"how does {stem} work",
        f"why is {stem} important",
        f"when to use {stem}",
        f"how much does {stem} cost",
        f"how to get started with {stem}",
        f"what are common mistakes with {stem}",
        f"what to know before {stem}",
        f"how to calculate {stem}",
        f"how to choose the best {stem}",
        f"is {stem} safe",
        f"who needs {stem}"
    ]
    
    # 3. High-Intent Semantic Entities & Technical Terms
    entities = [
        f"{stem} specifications",
        f"{stem} requirements",
        f"{stem} benchmarks",
        f"{stem} standards",
        f"{stem} checklist",
        f"{stem} documentation",
        f"{stem} procedures",
        f"{stem} calculations",
        f"{stem} formula",
        f"{stem} safety precautions",
        f"{stem} maintenance",
        f"{stem} timeline",
        f"{stem} eligibility criteria",
        f"{stem} expert recommendations"
    ]
    
    # 4. Long-Tail & Subtopic Angles
    long_tail = [
        f"{stem} alternatives",
        f"{stem} pros and cons",
        f"{stem} common pitfalls",
        f"{stem} best practices",
        f"{stem} troubleshooting",
        f"{stem} official regulations",
        f"{stem} key features",
        f"{stem} historical context",
        f"{stem} future trends",
        f"{stem} step by step instructions",
        f"{stem} average rates",
        f"{stem} practical applications",
        f"{stem} reference guide"
    ]
    
    combined = []
    seen = set()
    
    # Add any existing provided semantic keywords
    if existing_semantic_kws:
        for k in existing_semantic_kws:
            clean = str(k).strip()
            if clean and clean.lower() not in seen and clean.lower() != stem:
                seen.add(clean.lower())
                combined.append(clean)
                
    for group in [variations, questions, entities, long_tail]:
        for item in group:
            item_clean = item.strip()
            if item_clean.lower() not in seen:
                seen.add(item_clean.lower())
                combined.append(item_clean)
                
    content_gaps = [
        f"Competitors lacked exact step-by-step implementation details for {primary_kw}.",
        f"Competitors omitted concrete numerical benchmarks, real data points, or pricing tables.",
        f"Competitors gave generic high-level overviews without addressing common edge-case problems.",
        f"Competitors failed to provide clear troubleshooting and safety caveats for {primary_kw}.",
        f"Competitors missed answering direct user questions regarding timelines and practical requirements."
    ]
    
    visual_queries = [
        f"{primary_kw} detailed view",
        f"{primary_kw} practical setup",
        f"{primary_kw} real-world context"
    ]
    
    return {
        "competitor_summary": f"Standard industry overview of {primary_kw} focusing on definitions, general procedures, and basic tips.",
        "content_gaps": content_gaps,
        "semantic_keywords": combined[:60], # Ensures 50+
        "visual_queries": visual_queries
    }

def analyze_competitors_and_extract_lsi(primary_kw, competitor_results, existing_semantic_kws=None):
    """
    Performs deep competitor SERP analysis via Gemini API:
    1. Audits top 5 to 8 competitor titles, snippets, and angles.
    2. Extracts 50+ rich LSI and semantic keywords (covering intent, entities, questions, variations).
    3. Identifies specific content gaps competitors missed.
    4. Provides Unsplash photographic visual queries.
    """
    if not GEMINI_API_KEY:
        print("[SERP Analyzer] GEMINI_API_KEY not found in local environment. Using robust heuristic LSI engine.")
        return generate_heuristic_50_plus_lsi(primary_kw, existing_semantic_kws)
        
    competitor_text_block = ""
    if competitor_results:
        for comp in competitor_results:
            competitor_text_block += f"- Rank {comp.get('rank', '?')} [{comp.get('domain', 'web')}]: {comp.get('title', '')} | Snippet: {comp.get('snippet', '')}\n"
    else:
        competitor_text_block = "No direct SERP text extracted; perform competitive SERP simulation based on current Google top ranking standards."

    clean_existing = []
    if existing_semantic_kws:
        clean_existing = [k.strip() for k in existing_semantic_kws if k.strip() and k.strip().lower() != 'none (single standalone topic)']

    prompt = f"""You are a Lead SEO Strategist, SERP Intelligence Analyst, and Master Content Architect for GeneralPedia.
You are conducting a thorough competitor analysis to ensure our upcoming article on:
Primary Focus Keyword: "{primary_kw}"
Existing Seed Keywords: {', '.join(clean_existing[:10]) if clean_existing else 'None'}

Here is the intelligence gathered from the top 5 to 8 ranking competitors on Google SERP:
{competitor_text_block}

Perform an exhaustive, rigorous 4-part intelligence audit:

1. COMPETITOR STRATEGY & ANGLE BREAKDOWN:
   - Briefly summarize what the top ranking competitors are focusing on (their structure, angles, and search intent).

2. CONTENT GAP IDENTIFICATION (CRITICAL TO OUTRANK COMPETITORS):
   - Identify 4 to 6 specific, tangible "Content Gaps" — critical details, missing data, concrete numbers, edge cases, step-by-step procedures, or user questions that competitors either completely missed or explained poorly.

3. EXHAUSTIVE 50+ SEMANTIC & LSI KEYWORD EXTRACTION:
   - Provide AT LEAST 50 distinct, high-relevance LSI and semantic keywords strictly related to "{primary_kw}".
   - You MUST categorize them across these four buckets to ensure comprehensive topical coverage:
     a) Core LSI Synonyms & Search Variations (15+ terms)
     b) High-Intent Semantic Entities & Technical Terms (15+ terms)
     c) User Questions & Problem-Solving Queries (10+ terms)
     d) Long-Tail Secondary & Related Subtopics (10+ terms)
   - Ensure the total combined list in "all_lsi_and_semantic_keywords" has 50+ items!

4. VISUAL SEARCH QUERIES (FOR UNSPLASH STOCK PHOTOS):
   - Provide 3 to 4 concrete, descriptive visual search phrases for real-world photography (e.g., authentic settings, equipment, hands-on action; avoid abstract concepts).

OUTPUT FORMAT:
Return strictly a valid JSON object with no markdown code fences:
{{
  "competitor_summary": "Summary of competitor strategies and dominant angles...",
  "content_gaps": [
    "Gap 1: Competitors missed...",
    "Gap 2: Competitors only gave vague descriptions without...",
    "Gap 3: ...",
    "Gap 4: ..."
  ],
  "all_lsi_and_semantic_keywords": [
    "keyword 1", "keyword 2", "...at least 50 distinct keywords..."
  ],
  "visual_queries": [
    "query 1", "query 2", "query 3"
  ]
}}
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.25,
            "responseMimeType": "application/json"
        }
    }
    
    for model_name in FALLBACK_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json', 'User-Agent': 'GeneralPedia-SERP-Analyzer/1.0'}
            )
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                raw_json = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '').strip()
                
                # Strip any accidental code fences
                raw_json = re.sub(r'^```(json)?\s*', '', raw_json)
                raw_json = re.sub(r'```$', '', raw_json).strip()
                
                parsed = json.loads(raw_json)
                
                keywords = parsed.get("all_lsi_and_semantic_keywords", [])
                gaps = parsed.get("content_gaps", [])
                summary = parsed.get("competitor_summary", "")
                visuals = parsed.get("visual_queries", [])
                
                # Deduplicate and ensure >= 50 keywords
                clean_kws = []
                seen = set()
                for k in keywords:
                    k_str = str(k).strip()
                    if k_str and k_str.lower() not in seen and k_str.lower() != primary_kw.lower():
                        seen.add(k_str.lower())
                        clean_kws.append(k_str)
                        
                # If model returned fewer than 50 keywords, intelligently supplement with heuristic terms
                if len(clean_kws) < 50:
                    heuristic = generate_heuristic_50_plus_lsi(primary_kw, clean_existing)
                    for hk in heuristic["semantic_keywords"]:
                        if hk.lower() not in seen:
                            seen.add(hk.lower())
                            clean_kws.append(hk)
                            if len(clean_kws) >= 60:
                                break
                                
                print(f"[SERP Analyzer Success] Model {model_name} generated {len(clean_kws)} LSI keywords and {len(gaps)} content gaps.")
                return {
                    "competitor_summary": summary,
                    "content_gaps": gaps if gaps else ["Competitors lacked actionable step-by-step depth and real data benchmarks."],
                    "semantic_keywords": clean_kws[:65], # 50+ rich keywords
                    "visual_queries": visuals if visuals else [f"{primary_kw} practical guide", f"{primary_kw} details"]
                }
        except Exception as e:
            print(f"[SERP Analyzer Notice] Model {model_name} analysis error: {e}. Trying fallback...")
            continue

    print("[SERP Analyzer Warning] All Gemini API models failed for competitor analysis. Using heuristic engine.")
    return generate_heuristic_50_plus_lsi(primary_kw, existing_semantic_kws)

def analyze_serp_for_keyword(primary_kw, existing_semantic_kws=None):
    """
    Main entry point:
    1. Fetches top 5 to 8 competitors live from SERP.
    2. Deeply audits competitors, extracts 50+ semantic/LSI keywords, and uncovers content gaps.
    3. Returns full competitive intelligence dossier.
    """
    print(f"\n========================================================")
    print(f"[SERP & Competitor Intelligence] Starting audit for: '{primary_kw}'")
    print(f"========================================================")
    
    # 1. Fetch top 5 to 8 competitors
    competitors = fetch_top_competitors(primary_kw, max_results=8)
    
    # 2. Analyze competitors and extract 50+ LSI keywords & content gaps
    intel = analyze_competitors_and_extract_lsi(primary_kw, competitors, existing_semantic_kws)
    intel["competitor_results"] = competitors
    
    print(f"[SERP Audit Complete] Found {len(competitors)} competitors, extracted {len(intel['semantic_keywords'])} LSI keywords, and identified {len(intel['content_gaps'])} content gaps.\n")
    return intel
