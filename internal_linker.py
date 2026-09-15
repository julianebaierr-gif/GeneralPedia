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
        "id": "memorial-day-2026-dates-meaning-history-traditions",
        "title": "Memorial Day 2026: Dates, Meaning, History & Traditions",
        "category": "how-to",
        "patterns": [r"\bmemorial day 2026\b", r"\bmemorial day\b", r"\bfederal holiday\b"]
    },
    {
        "id": "tax-brackets-2025-key-dates-holidays-full",
        "title": "Tax Brackets 2025: Key Dates, Holidays & Full Overview",
        "category": "finance",
        "patterns": [r"\btax brackets 2025\b", r"\bfederal tax brackets\b", r"\bincome tax rate\b", r"\btax bracket\b"]
    },
    {
        "id": "sinus-infection-symptoms-main-causes-diagnosis-recovery",
        "title": "Sinus Infection Symptoms: Main Causes, Diagnosis & Recovery Steps",
        "category": "health",
        "patterns": [r"\bsinus infection symptoms\b", r"\bsinus infection\b", r"\bsinus pressure\b", r"\bnasal congestion\b"]
    },
    {
        "id": "january-2026-calendar-dates-meaning-history-traditions",
        "title": "January 2026 Calendar: Dates, Meaning, History & Traditions",
        "category": "tools",
        "patterns": [r"\bjanuary 2026 calendar\b", r"\b2026 calendar\b", r"\bmonthly calendar\b"]
    },
    {
        "id": "2025-toyota-camry-features-fuel-economy-trim",
        "title": "2025 Toyota Camry: Features, Fuel Economy & Trim Details",
        "category": "automotive",
        "patterns": [r"\b2025 toyota camry\b", r"\btoyota camry\b", r"\bhybrid sedan\b", r"\bfuel economy\b"]
    },
    {
        "id": "can-dogs-eat-bananas-safety-benefits-serving",
        "title": "Can Dogs Eat Bananas? Safety, Benefits & Serving Tips",
        "category": "lifestyle",
        "patterns": [r"\bcan dogs eat bananas\b", r"\bdog nutrition\b", r"\bcanine diet\b", r"\bpet health\b"]
    },
    {
        "id": "2026-winter-olympics-location-schedule-sports-updates",
        "title": "2026 Winter Olympics: Location, Schedule, Sports & Updates",
        "category": "culture",
        "patterns": [r"\b2026 winter olympics\b", r"\bwinter olympics\b", r"\bmilano cortina 2026\b", r"\bolympic games\b"]
    }
]

def get_active_targets():
    targets = []
    known_ids = set()
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
    # Fallback to ANCHOR_MAP only if database is empty
    if not targets:
        targets = list(ANCHOR_MAP)
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
