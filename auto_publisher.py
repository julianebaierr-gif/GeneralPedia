import os
import io
import json
import time
import urllib.request
import pandas as pd
from datetime import datetime

try:
    from config import POSTS_DIR, DATA_DIR, SHEET_GID, SPREADSHEET_ID
    from article_generator import generate_article
    from sheet_sync import log_post_to_sheet
except ImportError:
    from .config import POSTS_DIR, DATA_DIR, SHEET_GID, SPREADSHEET_ID
    from .article_generator import generate_article
    from .sheet_sync import log_post_to_sheet

ONLINE_SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={SHEET_GID}"
POSTS_DB_FILE = os.path.join(DATA_DIR, "posts_database.json")
PUBLISHER_STATE_FILE = os.path.join(DATA_DIR, "publisher_state.json")

# Fixed ordered list of all active categories to cycle through (7 categories)
CATEGORY_CYCLE = [
    "how-to",
    "finance",
    "health",
    "tools",
    "automotive",
    "lifestyle",
    "culture"
]

def get_publisher_state():
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(PUBLISHER_STATE_FILE):
        try:
            with open(PUBLISHER_STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {"last_category_index": -1, "last_category_slug": None, "cycle_count": 0}

def save_publisher_state(state):
    with open(PUBLISHER_STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)

def get_posts_database():
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(POSTS_DB_FILE):
        with open(POSTS_DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_posts_database(posts):
    with open(POSTS_DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(posts, f, indent=2)

def fetch_online_keywords_dataframe():
    """Fetches keywords directly from live Google Sheet URL over HTTPS"""
    req = urllib.request.Request(ONLINE_SHEET_CSV_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=20) as resp:
        content = resp.read().decode('utf-8', errors='ignore')
        return pd.read_csv(io.StringIO(content))

def publish_next_post(target_category=None):
    """
    Automated job:
    1. Reads live topics directly from online Google Sheet via HTTPS
    2. Cycles through categories one-by-one (Round-Robin) or targets specific category if requested
    3. If an entire category is exhausted (no unposted keywords), it skips to the next
    4. When all categories finish their turn, cycles back to the 1st category
    5. Generates 800-1200 words via Gemini API & Unsplash API
    6. Saves post, logs to Google Sheet via Webhook, and rebuilds index.html
    """
    from article_generator import slugify, detect_category

    df = fetch_online_keywords_dataframe()
    posts = get_posts_database()
    state = get_publisher_state()

    existing_ids = {str(p.get('id', '')).strip().lower() for p in posts}
    existing_slugs = {str(p.get('slug', '')).strip().lower() for p in posts}
    existing_kws = {str(p.get('primary_keyword', '')).strip().lower() for p in posts}

    # Group all available, unposted rows by their detected category
    unposted_by_category = {cat: [] for cat in CATEGORY_CYCLE}

    for idx, row in df.iterrows():
        primary_kw = str(row['Primary_Focus_Keyword']).strip()
        slug = slugify(primary_kw).lower()
        if slug in existing_ids or slug in existing_slugs or primary_kw.lower() in existing_kws:
            continue

        sem_raw = str(row.get('Semantic_Keywords_List', ''))
        semantic_kws = [k.strip() for k in sem_raw.split(',') if k.strip() and k.strip().lower() != 'none (single standalone topic)']
        detected_cat = detect_category(primary_kw, semantic_kws)

        if detected_cat not in unposted_by_category:
            unposted_by_category[detected_cat] = []
        unposted_by_category[detected_cat].append(row)

    # Determine which category should publish next
    last_idx = state.get("last_category_index", -1)
    total_cats = len(CATEGORY_CYCLE)

    selected_row = None
    selected_cat = None
    selected_cat_idx = None

    # If a specific category was requested manually, prioritize it
    if target_category and target_category in unposted_by_category and unposted_by_category[target_category]:
        selected_row = unposted_by_category[target_category][0]
        selected_cat = target_category
        selected_cat_idx = CATEGORY_CYCLE.index(target_category) if target_category in CATEGORY_CYCLE else last_idx
        print(f"[Direct-Category] Selected Category '{target_category}' ({len(unposted_by_category[target_category])} keywords remaining)")
    else:
        # Try every category in order starting right after last_idx
        for step in range(1, total_cats + 1):
            candidate_idx = (last_idx + step) % total_cats
            candidate_cat = CATEGORY_CYCLE[candidate_idx]
            available_rows = unposted_by_category.get(candidate_cat, [])

            if available_rows:
                selected_row = available_rows[0]
                selected_cat = candidate_cat
                selected_cat_idx = candidate_idx
                print(f"[Round-Robin] Selected Category '{candidate_cat}' ({len(available_rows)} keywords remaining in category)")
                break
            else:
                print(f"[Round-Robin] Category '{candidate_cat}' has 0 available keywords, skipping to next category...")

        # If all standard categories in cycle are exhausted, fallback to any unposted category
        if selected_row is None:
            for cat, rows in unposted_by_category.items():
                if rows:
                    selected_row = rows[0]
                    selected_cat = cat
                    selected_cat_idx = CATEGORY_CYCLE.index(cat) if cat in CATEGORY_CYCLE else 0
                    break

    if selected_row is None:
        return {"success": False, "message": "All keywords in all categories have been published!"}

    primary_kw = str(selected_row['Primary_Focus_Keyword']).strip()
    sem_raw = str(selected_row.get('Semantic_Keywords_List', ''))
    semantic_kws = [k.strip() for k in sem_raw.split(',') if k.strip() and k.strip().lower() != 'none (single standalone topic)']

    vol = selected_row.get('Primary_Volume', 0)
    kd = selected_row.get('Primary_KD', 0)
    cpc = selected_row.get('Primary_CPC', 0.0)

    # 1. Generate SEO Article via Gemini API & Unsplash API
    article = generate_article(primary_kw, semantic_kws, volume=vol, kd=kd, cpc=cpc)
    
    # 2. Save individual JSON post
    os.makedirs(POSTS_DIR, exist_ok=True)
    post_filepath = os.path.join(POSTS_DIR, f"{article['slug']}.json")
    with open(post_filepath, 'w', encoding='utf-8') as f:
        json.dump(article, f, indent=2)
        
    # 3. Add to live posts database
    posts.insert(0, article)
    save_posts_database(posts)
    
    # 4. Log to Google Sheet via Webhook
    sheet_res = log_post_to_sheet(
        keywords=article['primary_keyword'],
        category=article['category_name'],
        tags=article['tags'],
        status="Published",
        post_url=article['post_url'],
        post_date_time=article['published_at']
    )
    
    # 5. Save updated round-robin state
    new_cycle_count = state.get("cycle_count", 0)
    if selected_cat_idx == total_cats - 1:
        new_cycle_count += 1
    save_publisher_state({
        "last_category_index": selected_cat_idx,
        "last_category_slug": selected_cat,
        "cycle_count": new_cycle_count,
        "last_published_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    })

    # 6. Rebuild static HTML pages, index.html, sitemap.xml, site_data.js
    try:
        from rebuild_full_theme import rebuild_site
        rebuild_site()
        print("[Auto-Publisher] Successfully rebuilt all HTML pages, sitemap, and index.")
    except Exception as e:
        print(f"[Auto-Publisher Error] Failed to rebuild theme: {e}")
        import traceback
        traceback.print_exc()
        
    # 7. Auto-submit new article URL to Google Indexing API
    indexing_res = None
    try:
        from google_indexing import submit_url_to_google_indexing
        indexing_res = submit_url_to_google_indexing(article['post_url'])
    except Exception as e:
        print(f"[Auto-Publisher Error] Google Indexing API call failed: {e}")
        
    return {
        "success": True,
        "category": selected_cat,
        "article": article,
        "sheet_sync": sheet_res,
        "indexing": indexing_res,
        "total_published": len(posts)
    }

if __name__ == "__main__":
    print("Testing 100% online API publish run...")
    res = publish_next_post()
    print("Result:", json.dumps(res, indent=2))
