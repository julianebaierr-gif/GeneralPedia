# -*- coding: utf-8 -*-
"""
Natural Internal Linking Engine for GeneralPedia.
Handles:
1. Contextual in-text anchor links within paragraphs (max 2-3 per post, 100% natural).
2. Curated & dynamic regex pattern generation for all topics.
3. Post-FAQ 'Recommended Further Reading & Related Guides' box.
4. Two-way bidirectional linking: whenever a new article is generated, it links out to existing
   articles, and automatically scans existing articles across the website to link in to the new article!
"""
import os
import json
import re

SCRATCH_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRATCH_DIR, "data", "posts_database.json")
POSTS_DIR = os.path.join(SCRATCH_DIR, "posts")

# Master Curated Anchor Patterns for Established Topic Clusters
ANCHOR_MAP = [
    # Health Cluster
    {
        "id": "ast-blood-test-main-causes-diagnosis-recovery",
        "title": "AST Blood Test: Normal Ranges, Elevated Causes & Health Steps",
        "category": "health",
        "patterns": [
            r"\bast blood test\b",
            r"\bast serum level\b",
            r"\bast levels\b",
            r"\baspartate aminotransferase\b",
            r"\bliver enzyme levels\b",
            r"\belevated liver enzymes\b",
            r"\bliver enzymes\b"
        ]
    },
    {
        "id": "fatty-liver-disease-common-causes-home-remedies",
        "title": "Fatty Liver Disease: Primary Causes, Lifestyle Management & Care",
        "category": "health",
        "patterns": [
            r"\bfatty liver disease\b",
            r"\bfatty liver\b",
            r"\bhepatic steatosis\b",
            r"\bnafld\b",
            r"\bliver fat\b"
        ]
    },
    {
        "id": "how-to-stop-snoring-what-do-common",
        "title": "How to Stop Snoring: Practical Techniques, Causes & Doctor Advice",
        "category": "health",
        "patterns": [
            r"\bhow to stop snoring\b",
            r"\bstop snoring\b",
            r"\bchronic snoring\b",
            r"\bsnoring remedies\b",
            r"\bsnoring habits\b"
        ]
    },
    {
        "id": "sinus-infection-symptoms-main-causes-diagnosis-recovery",
        "title": "Sinus Infection Symptoms: Causes, Recovery Timelines & Relief",
        "category": "health",
        "patterns": [
            r"\bsinus infection symptoms\b",
            r"\bsinus infection\b",
            r"\bsinusitis\b",
            r"\bsinus pressure\b",
            r"\bnasal congestion\b",
            r"\bsinus inflammation\b"
        ]
    },
    {
        "id": "thrush-in-mouth-common-causes-home-remedies",
        "title": "Oral Thrush: Common Triggers, Soothing Care & Clinical Options",
        "category": "health",
        "patterns": [
            r"\bthrush in mouth\b",
            r"\boral thrush\b",
            r"\boral candidiasis\b",
            r"\bcandida infection\b",
            r"\bmouth yeast infection\b"
        ]
    },
    {
        "id": "skin-cancer-on-face-common-causes-home",
        "title": "Skin Cancer on Face: Early Warning Signs, Causes & Clinical Care",
        "category": "health",
        "patterns": [
            r"\bskin cancer on face\b",
            r"\bskin cancer\b",
            r"\bmelanoma\b",
            r"\bbasal cell carcinoma\b",
            r"\bsquamous cell carcinoma\b",
            r"\bfacial skin lesions\b"
        ]
    },

    # Finance Cluster
    {
        "id": "tax-brackets-2025-key-dates-holidays-full",
        "title": "Tax Brackets 2025: Key Dates, Holidays & Full Overview",
        "category": "finance",
        "patterns": [
            r"\btax brackets 2025\b",
            r"\bfederal tax brackets\b",
            r"\btax brackets\b",
            r"\btax bracket\b",
            r"\bmarginal tax rate\b",
            r"\bincome tax brackets\b"
        ]
    },
    {
        "id": "tax-refund-status-rules-limits-rates-strategy",
        "title": "Tax Refund Status: Rules, Limits, Tax Rates & Filing Strategy",
        "category": "finance",
        "patterns": [
            r"\btax refund status\b",
            r"\birs tax refund\b",
            r"\btax refund\b",
            r"\bwhere's my refund\b",
            r"\bfederal tax refund\b",
            r"\birs refund\b"
        ]
    },
    {
        "id": "rogue-credit-union-rules-limits-tax-rates",
        "title": "Rogue Credit Union: Rules, Limits, Tax Rates & Account Features",
        "category": "finance",
        "patterns": [
            r"\brogue credit union\b",
            r"\bcredit unions\b",
            r"\bcredit union accounts\b",
            r"\bcredit union\b"
        ]
    },
    {
        "id": "whole-life-insurance-contribution-limits-rules-deadlines",
        "title": "Whole Life Insurance: Contribution Limits, Rules & Deadlines",
        "category": "finance",
        "patterns": [
            r"\bwhole life insurance\b",
            r"\bpermanent life insurance\b",
            r"\bcash value life insurance\b",
            r"\blife insurance policy\b",
            r"\blife insurance policies\b"
        ]
    },
    {
        "id": "professional-liability-insurance-contribution-limits-rules-deadlines",
        "title": "Professional Liability Insurance: Contribution Limits, Rules & Deadlines",
        "category": "finance",
        "patterns": [
            r"\bprofessional liability insurance\b",
            r"\berrors and omissions insurance\b",
            r"\berrors and omissions\b",
            r"\bliability insurance\b"
        ]
    },
    {
        "id": "get-insurance-quotes-rates-financial-rules-key",
        "title": "Get Insurance Quotes: Rates, Financial Rules & Comparison Guide",
        "category": "finance",
        "patterns": [
            r"\bget insurance quotes\b",
            r"\binsurance quotes\b",
            r"\bcompare insurance rates\b",
            r"\bauto insurance quotes\b",
            r"\binsurance rate comparison\b"
        ]
    },
    {
        "id": "roth-ira-calculator-how-works-formula-quick",
        "title": "Roth IRA Calculator: How It Works, Formula & Quick Returns",
        "category": "tools",
        "patterns": [
            r"\broth ira calculator\b",
            r"\broth ira\b",
            r"\broth iras\b",
            r"\bira contribution limits\b",
            r"\broth conversion\b"
        ]
    },

    # Automotive Cluster
    {
        "id": "2025-toyota-camry-features-fuel-economy-trim",
        "title": "2025 Toyota Camry: Features, Fuel Economy & Trim Details",
        "category": "automotive",
        "patterns": [
            r"\b2025 toyota camry\b",
            r"\btoyota camry\b",
            r"\bcamry hybrid\b",
            r"\bcamry\b"
        ]
    },
    {
        "id": "honda-crv-2026-price-specs-features-trim",
        "title": "Honda CR-V 2026: Price, Specs, Features & Trim Options",
        "category": "automotive",
        "patterns": [
            r"\bhonda crv 2026\b",
            r"\b2026 honda cr-v\b",
            r"\bhonda cr-v\b",
            r"\bhonda crv\b"
        ]
    },
    {
        "id": "chevy-equinox-ev-what-means-key-facts",
        "title": "Chevy Equinox EV: What It Means, Key Facts & Practical Insights",
        "category": "automotive",
        "patterns": [
            r"\bchevy equinox ev\b",
            r"\bchevrolet equinox ev\b",
            r"\bequinox ev\b",
            r"\belectric equinox\b"
        ]
    },
    {
        "id": "ford-explorer-st",
        "title": "Ford Explorer ST: Full Model Review, Specs & What to Know",
        "category": "automotive",
        "patterns": [
            r"\bford explorer st\b",
            r"\bford explorer\b",
            r"\bexplorer st\b"
        ]
    },
    {
        "id": "used-cars-for-sale-real-specs-performance",
        "title": "Used Cars for Sale: Real Specs, Performance & Buying Guide",
        "category": "automotive",
        "patterns": [
            r"\bused cars for sale\b",
            r"\bbuying used cars\b",
            r"\bused cars\b",
            r"\bused car\b",
            r"\bpre-owned vehicles\b",
            r"\bpre-owned vehicle\b"
        ]
    },
    {
        "id": "how-to-change-a-tire-meaning-background",
        "title": "How to Change a Tire: Meaning, Background & Practical Facts",
        "category": "automotive",
        "patterns": [
            r"\bhow to change a tire\b",
            r"\bchange a tire\b",
            r"\bchanging a tire\b",
            r"\bchange a flat tire\b",
            r"\bspare tire\b",
            r"\bflat tire\b"
        ]
    },

    # Lifestyle & Pet Health Cluster
    {
        "id": "can-dogs-eat-bananas-safety-benefits-serving",
        "title": "Can Dogs Eat Bananas? Safety, Benefits & Serving Tips",
        "category": "lifestyle",
        "patterns": [
            r"\bcan dogs eat bananas\b",
            r"\bbananas for dogs\b",
            r"\bfeeding bananas to dogs\b",
            r"\bdogs eat bananas\b"
        ]
    },
    {
        "id": "giardia-in-dogs-practical-tips-guide-solutions",
        "title": "Giardia in Dogs: Practical Tips, Overview & Effective Solutions",
        "category": "lifestyle",
        "patterns": [
            r"\bgiardia in dogs\b",
            r"\bcanine giardia\b",
            r"\bgiardia infection\b",
            r"\bdog parasite\b"
        ]
    },
    {
        "id": "dog-years-to-human-essential-advice-methods",
        "title": "Dog Years to Human Years: Essential Advice, Methods & Overview",
        "category": "lifestyle",
        "patterns": [
            r"\bdog years to human years\b",
            r"\bdog years to human\b",
            r"\bdog years\b",
            r"\bcanine aging\b",
            r"\bdog's age in human years\b"
        ]
    },
    {
        "id": "how-to-bake-sourdough-bread-practical-tips",
        "title": "How to Bake Sourdough Bread: Practical Tips, Instructions & Guide",
        "category": "lifestyle",
        "patterns": [
            r"\bhow to bake sourdough bread\b",
            r"\bbake sourdough bread\b",
            r"\bbaking sourdough bread\b",
            r"\bsourdough bread\b",
            r"\bsourdough starter\b",
            r"\bhomemade sourdough\b"
        ]
    },
    {
        "id": "dryer-vent-cleaning-what-know-tips-easy",
        "title": "Dryer Vent Cleaning: What to Know, Tips & Easy Practical Steps",
        "category": "lifestyle",
        "patterns": [
            r"\bdryer vent cleaning\b",
            r"\bclean dryer vent\b",
            r"\bcleaning dryer vents\b",
            r"\bdryer vent\b",
            r"\bdryer duct\b"
        ]
    },
    {
        "id": "how-cook-bacon-oven",
        "title": "How To Cook Bacon In The Oven: Essential Advice, Methods & Overview",
        "category": "lifestyle",
        "patterns": [
            r"\bhow to cook bacon in the oven\b",
            r"\bcook bacon in the oven\b",
            r"\bcooking bacon in the oven\b",
            r"\boven-baked bacon\b",
            r"\bbaked bacon in the oven\b",
            r"\bbaking bacon in the oven\b",
            r"\boven baked bacon\b"
        ]
    },

    # Tools / Calculations / Units
    {
        "id": "right-triangle-calculator",
        "title": "Right Triangle Calculator: Accurate Calculation, Formula & Steps",
        "category": "tools",
        "patterns": [
            r"\bright triangle calculator\b",
            r"\bright triangle\b",
            r"\bhypotenuse\b",
            r"\bpythagorean theorem\b"
        ]
    },
    {
        "id": "12mm-to-inches-meaning-background-practical-facts",
        "title": "12mm to Inches: Meaning, Background & Practical Facts",
        "category": "tools",
        "patterns": [
            r"\b12mm to inches\b",
            r"\b12mm in inches\b",
            r"\bmm to inches\b",
            r"\bmillimeters to inches\b"
        ]
    },
    {
        "id": "oz-to-gallon-explanations-practical-facts-overview",
        "title": "Oz to Gallon: Explanations, Practical Facts & Overview",
        "category": "tools",
        "patterns": [
            r"\boz to gallon\b",
            r"\bfluid ounces to gallon\b",
            r"\bfl oz to gallon\b",
            r"\bounces to gallons\b"
        ]
    },
    {
        "id": "323-area-code-location-cities-served-lookup",
        "title": "323 Area Code: Location, Cities Served & Lookup Details",
        "category": "tools",
        "patterns": [
            r"\b323 area code\b",
            r"\barea code 323\b",
            r"\blos angeles area code\b"
        ]
    },
    {
        "id": "january-2026-calendar-dates-meaning-history-traditions",
        "title": "January 2026 Calendar: Dates, Meaning, History & Traditions",
        "category": "tools",
        "patterns": [
            r"\bjanuary 2026 calendar\b",
            r"\b2026 calendar\b",
            r"\bmonthly calendar\b"
        ]
    },

    # How-To & Home Services
    {
        "id": "air-conditioning-installation-what-means-key-facts",
        "title": "Air Conditioning Installation: What It Means, Key Facts & Advice",
        "category": "how-to",
        "patterns": [
            r"\bair conditioning installation\b",
            r"\bac installation\b",
            r"\bhvac installation\b",
            r"\bcentral air installation\b",
            r"\binstalling air conditioning\b"
        ]
    },
    {
        "id": "best-running-shoes-2025-printable-dates-holidays",
        "title": "Best Running Shoes 2025: Printable Dates, Holidays & Buying Guide",
        "category": "how-to",
        "patterns": [
            r"\bbest running shoes 2025\b",
            r"\brunning shoes 2025\b",
            r"\brunning shoes\b",
            r"\bmarathon running shoes\b"
        ]
    },
    {
        "id": "how-old-is-elon-musk-explanations-practical",
        "title": "How Old Is Elon Musk: Explanations, Practical Facts & Overview",
        "category": "how-to",
        "patterns": [
            r"\bhow old is elon musk\b",
            r"\belon musk's age\b",
            r"\belon musk\b"
        ]
    },
    {
        "id": "english-to-german-translation-what-means-key",
        "title": "English to German Translation: What It Means, Key Facts & Rules",
        "category": "how-to",
        "patterns": [
            r"\benglish to german translation\b",
            r"\bgerman translation\b",
            r"\btranslate english to german\b"
        ]
    },
    {
        "id": "when-does-lent-start-what-means-key",
        "title": "When Does Lent Start: What It Means, Key Facts & History",
        "category": "how-to",
        "patterns": [
            r"\bwhen does lent start\b",
            r"\blent season\b",
            r"\bash wednesday\b",
            r"\blenten season\b"
        ]
    },
    {
        "id": "memorial-day-2026-dates-meaning-history-traditions",
        "title": "Memorial Day 2026: Dates, Meaning, History & Traditions",
        "category": "how-to",
        "patterns": [
            r"\bmemorial day 2026\b",
            r"\bmemorial day weekend\b",
            r"\bmemorial day\b",
            r"\bfederal holiday\b"
        ]
    },

    # Culture
    {
        "id": "2026-winter-olympics-location-schedule-sports-updates",
        "title": "2026 Winter Olympics: Location, Schedule, Sports & Updates",
        "category": "culture",
        "patterns": [
            r"\b2026 winter olympics\b",
            r"\bwinter olympics\b",
            r"\bmilano cortina 2026\b",
            r"\bmilano cortina\b"
        ]
    },
    {
        "id": "the-wizard-of-oz-classic-movie-facts",
        "title": "The Wizard of Oz: Classic Movie Facts, Characters & Legacy",
        "category": "culture",
        "patterns": [
            r"\bthe wizard of oz\b",
            r"\bwizard of oz\b"
        ]
    },
    {
        "id": "queen-of-wands-card-meaning-symbolism-overview",
        "title": "Queen of Wands: Card Meaning, Symbolism & Full Overview",
        "category": "culture",
        "patterns": [
            r"\bqueen of wands\b",
            r"\btarot card\b",
            r"\btarot reading\b"
        ]
    },
    {
        "id": "where-is-cape-verde-geography-country-map",
        "title": "Where Is Cape Verde: Geography, Country Map & Key Facts",
        "category": "culture",
        "patterns": [
            r"\bwhere is cape verde\b",
            r"\bcape verde islands\b",
            r"\bcape verde\b",
            r"\bcabo verde\b"
        ]
    },
    {
        "id": "atlanta-hawks-vs-knicks-match-player-stats",
        "title": "Hawks vs Knicks: Player Stats & Box Score Analysis",
        "category": "culture",
        "patterns": [
            r"\batlanta hawks vs knicks\b",
            r"\bhawks vs knicks\b",
            r"\bknicks vs hawks\b"
        ]
    }
]

def get_active_targets():
    """
    Returns full list of targets combining ANCHOR_MAP with any dynamic targets
    from posts_database.json that aren't yet in ANCHOR_MAP.
    """
    known_ids = {t["id"] for t in ANCHOR_MAP}
    all_targets = list(ANCHOR_MAP)
    
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                db_posts = json.load(f)
            for p in db_posts:
                pid = p.get("slug") or p.get("id")
                if pid and pid not in known_ids:
                    pkw = p.get("primary_keyword", "")
                    clean_kw = re.sub(r'[^a-zA-Z0-9\s]', '', pkw).strip().lower()
                    patterns = []
                    if clean_kw and len(clean_kw) > 3:
                        patterns.append(rf"\b{re.escape(clean_kw)}\b")
                    
                    # Also add any 2-3 word semantic keywords
                    for skw in p.get("semantic_keywords", []):
                        clean_skw = re.sub(r'[^a-zA-Z0-9\s]', '', skw).strip().lower()
                        if clean_skw and len(clean_skw.split()) >= 2 and len(clean_skw) > 4:
                            patterns.append(rf"\b{re.escape(clean_skw)}\b")
                            
                    if patterns:
                        all_targets.append({
                            "id": pid,
                            "title": p.get("title", pkw),
                            "category": p.get("category_slug", "guide"),
                            "patterns": patterns[:5]
                        })
                        known_ids.add(pid)
        except Exception as e:
            print(f"[Internal Linker Warning] Failed reading db for dynamic targets: {e}")
            
    return all_targets

def inject_natural_internal_links(content_html, curr_id, curr_cat=None, max_links=2):
    """
    Naturally injects up to max_links contextual anchor links inside <p> paragraphs,
    and appends a curated 'Recommended Further Reading & Related Guides' card strictly after FAQs.
    """
    if not content_html:
        return content_html

    # 1. Clean existing in-text links and related reading boxes to prevent duplicates
    clean_content = re.sub(r'<div class="gp-related-reading-box">.*?</div>\s*', '', content_html, flags=re.DOTALL)
    clean_content = re.sub(r'<ul class="gp-related-reading-list">.*?</ul>\s*', '', clean_content, flags=re.DOTALL)
    clean_content = re.sub(r'<li class="gp-related-reading-item">.*?</li>\s*', '', clean_content, flags=re.DOTALL)
    clean_content = re.sub(r'\s*</div>\s*<ul class="gp-related-reading-list">', '', clean_content)
    clean_content = re.sub(r'<a\b[^>]*class=["\']gp-internal-link["\'][^>]*>(.*?)</a>', r'\1', clean_content)

    targets = get_active_targets()

    # Prioritize targets from same category first, then cross-category
    same_cat_targets = [t for t in targets if t["id"] != curr_id and t.get("category") == curr_cat]
    other_cat_targets = [t for t in targets if t["id"] != curr_id and t.get("category") != curr_cat]
    sorted_targets = same_cat_targets + other_cat_targets

    # 2. Contextual In-Text Linking directly on words/phrases inside <p> paragraphs
    linked_in_this_post = set()
    p_pattern = re.compile(r'(<p\b[^>]*>)(.*?)(</p>)', re.IGNORECASE | re.DOTALL)

    def link_p(match):
        open_tag = match.group(1)
        text = match.group(2)
        close_tag = match.group(3)

        # Skip paragraphs containing links, tools, or interactive buttons
        if '<a ' in text or 'gp-interactive-tool' in text or '<button' in text:
            return match.group(0)

        for target in sorted_targets:
            if target["id"] == curr_id or target["id"] in linked_in_this_post or len(linked_in_this_post) >= max_links:
                continue
            for pat in target["patterns"]:
                reg = re.compile(pat, re.IGNORECASE)
                m = reg.search(text)
                if m:
                    phrase = m.group(0)
                    t_id = target["id"]
                    t_title = target["title"].replace('"', '&quot;')
                    link_html = f'<a href="/{t_id}" class="gp-internal-link" title="{t_title}" onclick="handleCardClick(event, \'{t_id}\')">{phrase}</a>'
                    text = text[:m.start()] + link_html + text[m.end():]
                    linked_in_this_post.add(t_id)
                    break

        return f"{open_tag}{text}{close_tag}"

    updated_content = p_pattern.sub(link_p, clean_content)

    # 3. Add 'Recommended Further Reading & Related Guides' strictly BELOW FAQs
    CURATED_RELATED_MAP = {
        "how-cook-bacon-oven": [
            "how-to-bake-sourdough-bread-practical-tips",
            "oz-to-gallon-explanations-practical-facts-overview",
            "12mm-to-inches-meaning-background-practical-facts"
        ],
        "how-to-bake-sourdough-bread-practical-tips": [
            "how-cook-bacon-oven",
            "oz-to-gallon-explanations-practical-facts-overview",
            "dryer-vent-cleaning-what-know-tips-easy"
        ]
    }

    curated_ids = CURATED_RELATED_MAP.get(curr_id, [])
    if curated_ids:
        curated_targets = [t for t in targets if t["id"] in curated_ids]
        curated_targets.sort(key=lambda t: curated_ids.index(t["id"]) if t["id"] in curated_ids else 99)
        remaining = [t for t in (same_cat_targets + other_cat_targets) if t["id"] not in curated_ids]
        selected_related = (curated_targets + remaining)[:3]
    else:
        selected_related = (same_cat_targets + other_cat_targets)[:3]

    if selected_related:
        items_html = ""
        for t in selected_related:
            cat_display = t.get("category", "Guide").replace("-", " ").title()
            t_id = t["id"]
            t_title = t["title"]
            items_html += f"""
        <li class="gp-related-reading-item">
          <span class="gp-related-reading-badge">{cat_display}</span>
          <a href="/{t_id}" class="gp-related-reading-link" onclick="handleCardClick(event, '{t_id}')">{t_title}</a>
        </li>"""

        box_html = f"""
<div class="gp-related-reading-box">
  <div class="gp-related-reading-title">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
    <span>Recommended Further Reading &amp; Related Guides</span>
  </div>
  <ul class="gp-related-reading-list">{items_html}
  </ul>
</div>
"""
        # Place strictly after the last </details> (end of FAQs), or at the very end of content
        last_details_matches = list(re.finditer(r'</details>', updated_content, re.IGNORECASE))
        if last_details_matches:
            insert_idx = last_details_matches[-1].end()
            updated_content = updated_content[:insert_idx] + box_html + updated_content[insert_idx:]
        else:
            updated_content = updated_content + box_html

    return updated_content

def link_existing_articles_to_new(new_id, new_title, new_cat, new_patterns, db_posts=None, max_inbound=3):
    """
    Scans existing published articles in database to check if any naturally mention
    the new article's topic/patterns. If found and safe, injects an inbound link pointing
    to the new article.
    """
    if db_posts is None:
        if not os.path.exists(DB_PATH):
            return []
        with open(DB_PATH, "r", encoding="utf-8") as f:
            db_posts = json.load(f)

    inbound_created = []

    for post in db_posts:
        pid = post.get("slug") or post.get("id")
        if pid == new_id:
            continue
        
        html = post.get("content_html", "")
        # Don't add if already links to this target
        if f'href="/{new_id}"' in html or f"handleCardClick(event, '{new_id}')" in html:
            continue
            
        # Count existing in-text links in this post
        existing_intext_links = len(re.findall(r'<a\b[^>]*class=["\']gp-internal-link["\'][^>]*>', html))
        if existing_intext_links >= 3:
            continue

        p_pattern = re.compile(r'(<p\b[^>]*>)(.*?)(</p>)', re.IGNORECASE | re.DOTALL)
        modified = False

        def link_p_inbound(match):
            nonlocal modified
            if modified:
                return match.group(0)

            open_tag = match.group(1)
            text = match.group(2)
            close_tag = match.group(3)

            if '<a ' in text or 'gp-interactive-tool' in text or '<button' in text:
                return match.group(0)

            for pat in new_patterns:
                reg = re.compile(pat, re.IGNORECASE)
                m = reg.search(text)
                if m:
                    phrase = m.group(0)
                    t_title = new_title.replace('"', '&quot;')
                    link_html = f'<a href="/{new_id}" class="gp-internal-link" title="{t_title}" onclick="handleCardClick(event, \'{new_id}\')">{phrase}</a>'
                    text = text[:m.start()] + link_html + text[m.end():]
                    modified = True
                    inbound_created.append((pid, phrase))
                    break

            return f"{open_tag}{text}{close_tag}"

        new_html = p_pattern.sub(link_p_inbound, html)
        if modified:
            post["content_html"] = new_html
            # Save individual post file
            post_file = os.path.join(POSTS_DIR, f"{pid}.json")
            if os.path.exists(post_file):
                try:
                    with open(post_file, "r", encoding="utf-8") as pf:
                        pdata = json.load(pf)
                    pdata["content_html"] = new_html
                    with open(post_file, "w", encoding="utf-8") as pf:
                        json.dump(pdata, pf, indent=2, ensure_ascii=False)
                except Exception:
                    pass

    return inbound_created

def link_new_article_bidirectionally(article_data, db_posts=None):
    """
    Two-way automated internal linking for new articles:
    1. Outbound: Injects natural links from the new article into existing articles.
    2. Inbound: Checks existing articles across the website to see which can naturally
       link into this new article, and updates them!
    """
    new_id = article_data.get("slug") or article_data.get("id")
    new_title = article_data.get("title", "")
    new_cat = article_data.get("category_slug", "guide")
    raw_content = article_data.get("content_html", "")

    # 1. Outbound linking (New -> Existing)
    linked_content = inject_natural_internal_links(raw_content, new_id, new_cat)
    article_data["content_html"] = linked_content

    # 2. Inbound linking (Existing -> New)
    # Generate anchor patterns for the new article
    pkw = article_data.get("primary_keyword", "")
    clean_kw = re.sub(r'[^a-zA-Z0-9\s]', '', pkw).strip().lower()
    new_patterns = []
    if clean_kw and len(clean_kw) > 3:
        new_patterns.append(rf"\b{re.escape(clean_kw)}\b")

    for skw in article_data.get("semantic_keywords", []):
        clean_skw = re.sub(r'[^a-zA-Z0-9\s]', '', skw).strip().lower()
        if clean_skw and len(clean_skw.split()) >= 2 and len(clean_skw) > 4:
            new_patterns.append(rf"\b{re.escape(clean_skw)}\b")

    inbound = []
    if new_patterns:
        inbound = link_existing_articles_to_new(new_id, new_title, new_cat, new_patterns, db_posts=db_posts)
        if inbound:
            print(f"[Bidirectional Linker] Created {len(inbound)} natural inbound links to '{new_id}':")
            for src, phr in inbound:
                print(f"   <- From '{src}' on phrase: '{phr}'")

    return article_data

def process_all_articles(rebuild_theme=False):
    """
    Processes all articles in database, injects natural internal links, updates JSON files,
    and optionally triggers full site rebuild.
    """
    if not os.path.exists(DB_PATH):
        print("posts_database.json not found!")
        return

    with open(DB_PATH, "r", encoding="utf-8") as f:
        posts = json.load(f)

    total_intext_links = 0
    posts_with_links = 0

    for post in posts:
        curr_id = post.get("slug") or post.get("id")
        curr_cat = post.get("category_slug", "")
        old_html = post.get("content_html", "")

        new_html = inject_natural_internal_links(old_html, curr_id, curr_cat)
        post["content_html"] = new_html

        links = re.findall(r'<a\b[^>]*class=["\']gp-internal-link["\'][^>]*>(.*?)</a>', new_html)
        if links:
            posts_with_links += 1
            total_intext_links += len(links)

        post_file = os.path.join(POSTS_DIR, f"{curr_id}.json")
        if os.path.exists(post_file):
            try:
                with open(post_file, "r", encoding="utf-8") as pf:
                    data = json.load(pf)
                data["content_html"] = new_html
                with open(post_file, "w", encoding="utf-8") as pf:
                    json.dump(data, pf, indent=2, ensure_ascii=False)
            except Exception:
                pass

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)

    print(f"Successfully processed all {len(posts)} articles.")
    print(f"Posts with in-text internal links: {posts_with_links}/{len(posts)}")
    print(f"Total in-text internal links injected: {total_intext_links}")

    if rebuild_theme:
        try:
            from rebuild_full_theme import rebuild_site
            rebuild_site()
            print("Successfully rebuilt full site theme and pre-rendered pages!")
        except Exception as e:
            print(f"Warning: Failed to rebuild site: {e}")

if __name__ == "__main__":
    process_all_articles(rebuild_theme=True)
