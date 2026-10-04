import os
import re
import json
import time
import requests
import urllib.request
import urllib.parse
from env_loader import get_secret

GEMINI_API_KEY = get_secret("GEMINI_API_KEY")

FALLBACK_MODELS = [
    "gemini-3.7-flash",
    "gemini-3.8-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-flash-latest"
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

def generate_heuristic_100_plus_lsi(primary_kw, existing_semantic_kws=None):
    """
    Robust algorithmic fallback that generates 100+ high-relevance LSI/semantic terms
    and 6 to 8 comprehensive content gaps across distinct intent categories.
    Guarantees the publishing pipeline NEVER crashes if external APIs are offline.
    """
    kw = primary_kw.strip()
    words = [w for w in re.split(r'\s+', kw.lower()) if w]
    stem = " ".join(words)
    
    # 1. Core Intent Variations & Synonyms (20 terms)
    variations = [
        f"{stem} meaning",
        f"{stem} overview",
        f"{stem} definition",
        f"{stem} key facts",
        f"{stem} explained",
        f"{stem} full breakdown",
        f"{stem} essential details",
        f"{stem} verified facts",
        f"{stem} complete reference",
        f"{stem} background context",
        f"{stem} core concepts",
        f"{stem} practical summary",
        f"{stem} fundamental principles",
        f"{stem} origins and development",
        f"{stem} key characteristics",
        f"{stem} definitive guide",
        f"{stem} comprehensive review",
        f"{stem} in practice",
        f"{stem} structural framework",
        f"{stem} primary functions"
    ]
    
    # 2. User Questions & Problem Solving (20 terms)
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
        f"who needs {stem}",
        f"where to find {stem}",
        f"can you use {stem}",
        f"what happens if {stem}",
        f"how long does {stem} take",
        f"what are the requirements for {stem}",
        f"how does {stem} compare",
        f"which is better for {stem}",
        f"what to look for in {stem}"
    ]
    
    # 3. Step-by-Step, Procedural & Logistical Terms (18 terms)
    procedural = [
        f"{stem} step by step instructions",
        f"{stem} practical checklist",
        f"{stem} workflow implementation",
        f"{stem} operational timeline",
        f"{stem} preparation guidelines",
        f"{stem} execution phases",
        f"{stem} setup procedures",
        f"{stem} recommended practices",
        f"{stem} verified protocols",
        f"{stem} maintenance schedule",
        f"{stem} configuration rules",
        f"{stem} standard operating procedure",
        f"{stem} inspection checklist",
        f"{stem} monitoring criteria",
        f"{stem} handling instructions",
        f"{stem} transition steps",
        f"{stem} routine management",
        f"{stem} milestone checklist"
    ]
    
    # 4. Technical Terms, Metrics, Benchmarks & Specifications (18 terms)
    entities = [
        f"{stem} specifications",
        f"{stem} numerical benchmarks",
        f"{stem} official standards",
        f"{stem} calculation formula",
        f"{stem} technical documentation",
        f"{stem} performance metrics",
        f"{stem} eligibility criteria",
        f"{stem} quantitative analysis",
        f"{stem} reference dataset",
        f"{stem} threshold parameters",
        f"{stem} capacity limits",
        f"{stem} efficiency ratings",
        f"{stem} testing protocol",
        f"{stem} measurement benchmarks",
        f"{stem} official compliance",
        f"{stem} statistical averages",
        f"{stem} regulatory framework",
        f"{stem} expert evaluation"
    ]
    
    # 5. Comparisons, Tradeoffs & Alternatives (16 terms)
    comparisons = [
        f"{stem} vs alternative methods",
        f"{stem} pros and cons breakdown",
        f"{stem} comparative analysis",
        f"{stem} cost performance trade-offs",
        f"{stem} traditional vs modern approach",
        f"{stem} differences and similarities",
        f"{stem} top alternatives",
        f"{stem} replacement options",
        f"{stem} advantages and disadvantages",
        f"{stem} side by side comparison",
        f"{stem} efficiency comparison",
        f"{stem} value assessment",
        f"{stem} practical tradeoffs",
        f"{stem} selection criteria",
        f"{stem} market alternatives",
        f"{stem} decision matrix"
    ]
    
    # 6. Pitfalls, Risk Mitigation, Safety & Caveats (16 terms)
    pitfalls = [
        f"{stem} common pitfalls to avoid",
        f"{stem} risk mitigation strategies",
        f"{stem} critical safety precautions",
        f"{stem} troubleshooting edge cases",
        f"{stem} warning signs and red flags",
        f"{stem} error handling protocols",
        f"{stem} compliance risks",
        f"{stem} quality control checks",
        f"{stem} preventable oversights",
        f"{stem} corrective actions",
        f"{stem} consumer warnings",
        f"{stem} diagnostic troubleshooting",
        f"{stem} failure prevention",
        f"{stem} verification checks",
        f"{stem} hazard mitigation",
        f"{stem} emergency contingency"
    ]
    
    # 7. Industry Context, Long-Tail, Schedules & FAQs (16 terms)
    long_tail = [
        f"{stem} historical timeline and origins",
        f"{stem} current market trends",
        f"{stem} statutory deadlines and dates",
        f"{stem} industry best practices",
        f"{stem} legal and regulatory compliance",
        f"{stem} real-world case examples",
        f"{stem} professional recommendations",
        f"{stem} future outlook and updates",
        f"{stem} community standards",
        f"{stem} official documentation references",
        f"{stem} certified guidelines",
        f"{stem} practical takeaways",
        f"{stem} frequently asked questions",
        f"{stem} authoritative reference guide",
        f"{stem} everyday practical applications",
        f"{stem} core reference summary"
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
                
    for group in [variations, questions, procedural, entities, comparisons, pitfalls, long_tail]:
        for item in group:
            item_clean = item.strip()
            if item_clean.lower() not in seen:
                seen.add(item_clean.lower())
                combined.append(item_clean)
                
    content_gaps = [
        f"Competitors lacked exact step-by-step implementation details, logistical specifics, and verified data points for {primary_kw}.",
        f"Competitors omitted concrete numerical benchmarks, real data matrices, and comparative reference tables.",
        f"Competitors gave generic high-level overviews without addressing common edge-case problems and practical pitfalls.",
        f"Competitors failed to provide clear troubleshooting rules, safety caveats, and expert-verified protocols.",
        f"Competitors missed answering direct user search queries regarding timelines, schedules, and specific compliance factors.",
        f"Competitors omitted actionable cost/performance trade-offs and objective alternative comparisons.",
        f"Competitors overlooked regulatory, historical, and primary-source context essential for comprehensive authority.",
        f"Competitors lacked direct, zero-click featured snippet answers for quick user reference."
    ]
    
    visual_queries = [
        f"{primary_kw} detailed view",
        f"{primary_kw} practical setup",
        f"{primary_kw} real-world context"
    ]
    
    return {
        "competitor_summary": f"Standard industry overview of {primary_kw} focusing on definitions, general procedures, and basic tips.",
        "content_gaps": content_gaps,
        "semantic_keywords": combined[:115], # Guarantees 100+ keywords
        "visual_queries": visual_queries
    }

# Backward compatibility alias
generate_heuristic_50_plus_lsi = generate_heuristic_100_plus_lsi

def analyze_competitors_and_extract_lsi(primary_kw, competitor_results, existing_semantic_kws=None):
    """
    Performs deep competitor SERP analysis via Gemini API:
    1. Audits top 5 to 8 competitor titles, snippets, and angles.
    2. Extracts 100+ rich LSI and semantic keywords across 6 distinct intent categories.
    3. Identifies 6 to 8 critical content gaps competitors missed.
    4. Provides Unsplash photographic visual queries.
    """
    if not GEMINI_API_KEY:
        print("[SERP Analyzer] GEMINI_API_KEY not found in local environment. Using robust heuristic LSI engine.")
        return generate_heuristic_100_plus_lsi(primary_kw, existing_semantic_kws)
        
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
   - Identify 6 to 8 specific, tangible "Content Gaps" — critical details, missing data, concrete numbers, edge cases, step-by-step procedures, or user questions that competitors either completely missed or explained poorly.

3. EXHAUSTIVE 100+ SEMANTIC & LSI KEYWORD EXTRACTION:
   - Provide AT LEAST 100 distinct, high-relevance LSI and semantic keywords strictly related to "{primary_kw}".
   - You MUST categorize them across these six buckets to ensure comprehensive topical coverage:
     a) Core LSI Synonyms & Search Variations (25+ terms)
     b) High-Intent Semantic Entities & Technical Terms (25+ terms)
     c) User Questions & Problem-Solving Queries (20+ terms)
     d) Long-Tail Secondary & Related Subtopics (15+ terms)
     e) Comparison, Tradeoff & Alternative Phrases (15+ terms)
     f) Procedural, Safety, Rules & Numerical Phrases (15+ terms)
   - Ensure the total combined list in "all_lsi_and_semantic_keywords" has AT LEAST 100 items (target 100 to 115 distinct keywords)!

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
    "Gap 4: ...",
    "Gap 5: ...",
    "Gap 6: ...",
    "Gap 7: ...",
    "Gap 8: ..."
  ],
  "all_lsi_and_semantic_keywords": [
    "keyword 1", "keyword 2", "...at least 100 distinct keywords..."
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
        for attempt in range(2):
            try:
                resp = requests.post(url, json=payload, headers={'User-Agent': 'GeneralPedia-SERP-Analyzer/1.0'}, timeout=35)
                if resp.status_code == 503 and attempt == 0:
                    print(f"[SERP Analyzer Notice] Model {model_name} temporary 503 spike. Retrying in 2.5s...")
                    time.sleep(2.5)
                    continue
                if resp.status_code != 200:
                    print(f"[SERP Analyzer Notice] Model {model_name} returned status {resp.status_code}. Trying next fallback...")
                    break
                data = resp.json()
                raw_json = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '').strip()
                
                # Strip any accidental code fences
                raw_json = re.sub(r'^```(json)?\s*', '', raw_json)
                raw_json = re.sub(r'```$', '', raw_json).strip()
                
                parsed = json.loads(raw_json)
                
                keywords = parsed.get("all_lsi_and_semantic_keywords", [])
                gaps = parsed.get("content_gaps", [])
                summary = parsed.get("competitor_summary", "")
                visuals = parsed.get("visual_queries", [])
                
                # Deduplicate and ensure >= 100 keywords
                clean_kws = []
                seen = set()
                for k in keywords:
                    k_str = str(k).strip()
                    if k_str and k_str.lower() not in seen and k_str.lower() != primary_kw.lower():
                        seen.add(k_str.lower())
                        clean_kws.append(k_str)
                        
                # If model returned fewer than 100 keywords, intelligently supplement with heuristic terms
                if len(clean_kws) < 100:
                    heuristic = generate_heuristic_100_plus_lsi(primary_kw, clean_existing)
                    for hk in heuristic["semantic_keywords"]:
                        if hk.lower() not in seen:
                            seen.add(hk.lower())
                            clean_kws.append(hk)
                            if len(clean_kws) >= 110:
                                break

                # Ensure at least 6 content gaps
                if len(gaps) < 6:
                    heuristic = generate_heuristic_100_plus_lsi(primary_kw, clean_existing)
                    for hg in heuristic["content_gaps"]:
                        if hg not in gaps:
                            gaps.append(hg)
                            if len(gaps) >= 8:
                                break
                                
                print(f"[SERP Analyzer Success] Model {model_name} generated {len(clean_kws)} LSI keywords and {len(gaps)} content gaps.")
                return {
                    "competitor_summary": summary,
                    "content_gaps": gaps if gaps else ["Competitors lacked actionable step-by-step depth and real data benchmarks."],
                    "semantic_keywords": clean_kws[:115], # 100+ rich keywords
                    "visual_queries": visuals if visuals else [f"{primary_kw} practical guide", f"{primary_kw} details"]
                }
            except Exception as e:
                print(f"[SERP Analyzer Notice] Model {model_name} analysis error: {e}. Trying fallback...")
                break

    print("[SERP Analyzer Warning] All Gemini API models failed for competitor analysis. Using heuristic engine.")
    return generate_heuristic_100_plus_lsi(primary_kw, existing_semantic_kws)

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
