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

def publish_next_post():
    """
    Automated job:
    1. Reads live topics directly from online Google Sheet via HTTPS
    2. Checks existing database IDs to skip published ones
    3. Generates 800-1200 words via Gemini API
    4. Fetches unique image by ID from Unsplash API
    5. Saves post and logs to Google Sheet via Webhook
    """
    df = fetch_online_keywords_dataframe()
    posts = get_posts_database()
    existing_ids = {p.get('id') for p in posts}
    
    selected_row = None
    for idx, row in df.iterrows():
        primary_kw = str(row['Primary_Focus_Keyword']).strip()
        from article_generator import slugify
        slug = slugify(primary_kw)
        if slug not in existing_ids:
            selected_row = row
            break
            
    if selected_row is None:
        return {"success": False, "message": "All keywords published!"}
        
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
    
    # 5. Rebuild static index.html
    try:
        from rebuild_full_theme import rebuild_site
        rebuild_site()
    except Exception:
        pass
        
    return {
        "success": True,
        "article": article,
        "sheet_sync": sheet_res,
        "total_published": len(posts)
    }

if __name__ == "__main__":
    print("Testing 100% online API publish run...")
    res = publish_next_post()
    print("Result:", json.dumps(res, indent=2))
