# -*- coding: utf-8 -*-
"""
Natural Internal Linking Module for GeneralPedia.
Can be run standalone to re-link all posts, or imported to link individual articles.
"""
import os
import json
import re

SCRATCH_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRATCH_DIR, "data", "posts_database.json")
POSTS_DIR = os.path.join(SCRATCH_DIR, "posts")

ANCHOR_MAP = [
    {
        "id": "12mm-to-inches-meaning-background-practical-facts",
        "title": "12mm To Inches: Complete Metric & Hardware Guide",
        "category": "tools",
        "patterns": [r"\b12mm to inches\b", r"\bmetric to imperial\b", r"\bmetric measurements\b", r"\bmetric and imperial\b"]
    },
    {
        "id": "how-to-change-a-tire-meaning-background",
        "title": "How To Change A Tire: Step-by-Step Emergency Guide",
        "category": "automotive",
        "patterns": [r"\bhow to change a tire\b", r"\bspare tire\b", r"\broadside emergency\b", r"\bvehicle maintenance\b"]
    },
    {
        "id": "oz-to-gallon-explanations-practical-facts-guide",
        "title": "Oz To Gallon: Liquid Volume & Conversions",
        "category": "tools",
        "patterns": [r"\boz to gallon\b", r"\bfluid ounces\b", r"\bliquid measurements\b", r"\bvolume conversions\b"]
    },
    {
        "id": "thrush-in-mouth-common-causes-home-remedies",
        "title": "Thrush In Mouth: Causes & Natural Home Remedies",
        "category": "health",
        "patterns": [r"\bthrush in mouth\b", r"\boral thrush\b", r"\boral hygiene\b", r"\bimmune system\b"]
    },
    {
        "id": "tax-brackets-2025-key-dates-holidays-full",
        "title": "Tax Brackets 2025: Federal Tax Rates & Deadlines",
        "category": "finance",
        "patterns": [r"\btax brackets 2025\b", r"\bfederal tax brackets\b", r"\bincome tax\b", r"\btax rate\b", r"\btax bracket\b"]
    },
    {
        "id": "best-running-shoes-2025-printable-dates-holidays",
        "title": "Best Running Shoes 2025: Cushioning & Athletic Footwear",
        "category": "how-to",
        "patterns": [r"\brunning shoes\b", r"\bathletic footwear\b", r"\bcushioning\b"]
    },
    {
        "id": "twilight-movies-in-order-full-story-characters",
        "title": "Twilight Movies In Order: Full Saga Timeline",
        "category": "culture",
        "patterns": [r"\btwilight movies\b", r"\bmovie franchise\b", r"\bcinematic release\b"]
    },
    {
        "id": "dryer-vent-cleaning-what-know-tips-easy",
        "title": "Dryer Vent Cleaning: Essential Fire Safety & Tips",
        "category": "lifestyle",
        "patterns": [r"\bdryer vent cleaning\b", r"\bhousehold safety\b", r"\bventilation\b", r"\bfire hazard\b"]
    },
    {
        "id": "roth-ira-calculator-how-works-formula-quick",
        "title": "Roth IRA Calculator: Formulas & Compound Growth",
        "category": "tools",
        "patterns": [r"\broth ira\b", r"\bretirement savings\b", r"\bcompound interest\b", r"\bfinancial planning\b"]
    },
    {
        "id": "loan-payoff-calculator-free-online-tool-formula",
        "title": "Loan Payoff Calculator: Amortization & Debt Reduction",
        "category": "tools",
        "patterns": [r"\bloan payoff calculator\b", r"\binterest rate\b", r"\bmonthly payments\b", r"\bdebt payoff\b"]
    },
    {
        "id": "honda-crv-2026-price-specs-features-trim",
        "title": "Honda CR-V 2026: Pricing, Specs & Trims",
        "category": "automotive",
        "patterns": [r"\bhonda cr-v\b", r"\bcompact suv\b", r"\ball-wheel drive\b"]
    },
    {
        "id": "2025-toyota-camry-features-fuel-economy-trim",
        "title": "2025 Toyota Camry: Hybrid Performance & MPG",
        "category": "automotive",
        "patterns": [r"\btoyota camry\b", r"\bhybrid sedan\b", r"\bfuel economy\b", r"\bmpg\b"]
    },
    {
        "id": "used-cars-for-sale-real-specs-performance",
        "title": "Used Cars For Sale: Buyer Checklist & Inspection",
        "category": "automotive",
        "patterns": [r"\bused cars\b", r"\bpre-owned vehicle\b", r"\bvehicle inspection\b"]
    },
    {
        "id": "sinus-infection-symptoms-main-causes-diagnosis-recovery",
        "title": "Sinus Infection Symptoms: Causes & Recovery Guide",
        "category": "health",
        "patterns": [r"\bsinus infection\b", r"\bsinus pressure\b", r"\bcongestion\b", r"\bantibiotics\b"]
    },
    {
        "id": "can-dogs-eat-bananas-safety-benefits-serving",
        "title": "Can Dogs Eat Bananas: Canine Nutrition & Benefits",
        "category": "finance",
        "patterns": [r"\bcan dogs eat bananas\b", r"\bpet health\b", r"\bdog nutrition\b"]
    },
    {
        "id": "the-wizard-of-oz-classic-movie-facts",
        "title": "The Wizard of Oz: Classic Movie History & Facts",
        "category": "finance",
        "patterns": [r"\bthe wizard of oz\b", r"\bclassic cinema\b", r"\bfilm history\b"]
    },
    {
        "id": "2026-winter-olympics-location-schedule-sports-updates",
        "title": "2026 Winter Olympics: Venues & Competition Guide",
        "category": "finance",
        "patterns": [r"\bwinter olympics\b", r"\bolympic games\b", r"\bathletic competition\b"]
    },
    {
        "id": "memorial-day-2026-dates-meaning-history-traditions",
        "title": "Memorial Day 2026: Origins, Observance & Meaning",
        "category": "how-to",
        "patterns": [r"\bmemorial day\b", r"\bfederal holiday\b", r"\bnational traditions\b"]
    }
]

def get_active_targets():
    targets = list(ANCHOR_MAP)
    known_ids = {t["id"] for t in targets}
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                db_posts = json.load(f)
            for p in db_posts:
                pid = p.get("slug") or p.get("id")
                if pid and pid not in known_ids:
                    pkw = p.get("primary_keyword", "")
                    clean_kw = re.sub(r'[^a-zA-Z0-9\s]', '', pkw).strip().lower()
                    if clean_kw:
                        targets.append({
                            "id": pid,
                            "title": p.get("title", pkw),
                            "category": p.get("category_slug", "guide"),
                            "patterns": [rf"\b{re.escape(clean_kw)}\b"]
                        })
                        known_ids.add(pid)
        except Exception:
            pass
    return targets

def inject_natural_internal_links(content_html, curr_id, curr_cat=None):
    if not content_html:
        return content_html

    # Clean any residual related reading boxes, lists, or bullets completely
    clean_content = re.sub(r'<div class="gp-related-reading-box">.*?</div>\s*', '', content_html, flags=re.DOTALL)
    clean_content = re.sub(r'<ul class="gp-related-reading-list">.*?</ul>\s*', '', clean_content, flags=re.DOTALL)
    clean_content = re.sub(r'<li class="gp-related-reading-item">.*?</li>\s*', '', clean_content, flags=re.DOTALL)
    clean_content = re.sub(r'\s*</div>\s*<ul class="gp-related-reading-list">', '', clean_content)
    clean_content = re.sub(r'<a\b[^>]*class="gp-internal-link"[^>]*>(.*?)</a>', r'\1', clean_content)

    targets = get_active_targets()

    # Natural In-Text Linking directly on words/phrases inside <p> paragraphs
    linked_in_this_post = set()
    p_pattern = re.compile(r'(<p\b[^>]*>)(.*?)(</p>)', re.IGNORECASE | re.DOTALL)

    def link_p(match):
        open_tag = match.group(1)
        text = match.group(2)
        close_tag = match.group(3)

        if '<a ' in text or 'gp-interactive-tool' in text or '<button' in text:
            return match.group(0)

        for target in targets:
            if target["id"] == curr_id or target["id"] in linked_in_this_post or len(linked_in_this_post) >= 3:
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

    # 2. Add 'Recommended Further Reading & Related Guides' strictly BELOW FAQs
    same_cat_targets = [t for t in targets if t["id"] != curr_id and t.get("category") == curr_cat]
    other_cat_targets = [t for t in targets if t["id"] != curr_id and t.get("category") != curr_cat]
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

def process_all_articles():
    if not os.path.exists(DB_PATH):
        print("posts_database.json not found!")
        return

    with open(DB_PATH, "r", encoding="utf-8") as f:
        posts = json.load(f)

    for post in posts:
        curr_id = post.get("slug") or post.get("id")
        curr_cat = post.get("category_slug", "")
        old_html = post.get("content_html", "")

        new_html = inject_natural_internal_links(old_html, curr_id, curr_cat)
        post["content_html"] = new_html

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

    print(f"Successfully processed all {len(posts)} articles with pure in-text internal links.")

if __name__ == "__main__":
    process_all_articles()
