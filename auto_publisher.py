import os
import json
import time
import pandas as pd
from datetime import datetime

try:
    from config import POSTS_DIR, DATA_DIR
    from article_generator import generate_article
    from sheet_sync import log_post_to_sheet
except ImportError:
    from .config import POSTS_DIR, DATA_DIR
    from .article_generator import generate_article
    from .sheet_sync import log_post_to_sheet

KEYWORDS_CSV = r"C:\Users\Admin\.gemini\antigravity\scratch\semantic_keyword_clusters.csv"
STATE_FILE = os.path.join(DATA_DIR, "publisher_state.json")
POSTS_DB_FILE = os.path.join(DATA_DIR, "posts_database.json")

def get_publisher_state():
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"published_count": 0, "last_published_index": -1, "published_ids": []}

def save_publisher_state(state):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
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

def publish_next_post():
    """
    Automated job:
    1. Reads next topic from cluster list
    2. Generates article
    3. Saves post to database & disk
    4. Logs to Google Sheet & Local Mirror
    """
    if not os.path.exists(KEYWORDS_CSV):
        return {"success": False, "error": "Keywords cluster file not found"}
        
    df = pd.read_csv(KEYWORDS_CSV)
    state = get_publisher_state()
    next_idx = state.get("last_published_index", -1) + 1
    
    if next_idx >= len(df):
        return {"success": False, "message": "All keywords published!"}
        
    row = df.iloc[next_idx]
    primary_kw = str(row['Primary_Focus_Keyword']).strip()
    sem_raw = str(row.get('Semantic_Keywords_List', ''))
    semantic_kws = [k.strip() for k in sem_raw.split(',') if k.strip() and k.strip().lower() != 'none (single standalone topic)']
    
    vol = row.get('Primary_Volume', 0)
    kd = row.get('Primary_KD', 0)
    cpc = row.get('Primary_CPC', 0.0)
    
    # 1. Generate SEO Article
    article = generate_article(primary_kw, semantic_kws, volume=vol, kd=kd, cpc=cpc)
    
    # 2. Save Markdown / JSON post
    os.makedirs(POSTS_DIR, exist_ok=True)
    post_filepath = os.path.join(POSTS_DIR, f"{article['slug']}.json")
    with open(post_filepath, 'w', encoding='utf-8') as f:
        json.dump(article, f, indent=2)
        
    # 3. Add to live posts database
    posts = get_posts_database()
    # Prepend newest
    posts.insert(0, {k: v for k, v in article.items() if k != 'content_html'})
    save_posts_database(posts)
    
    # 4. Log to Google Sheet
    all_kws_combined = primary_kw
    if semantic_kws:
        all_kws_combined += " (LSI: " + ", ".join(semantic_kws[:4]) + ")"
        
    sheet_res = log_post_to_sheet(
        keywords=all_kws_combined,
        category=article['category_name'],
        tags=article['tags'],
        status="Published",
        post_url=article['post_url'],
        post_date_time=article['published_at']
    )
    
    # 5. Update State
    state["last_published_index"] = next_idx
    state["published_count"] = state.get("published_count", 0) + 1
    state["published_ids"].append(article['id'])
    save_publisher_state(state)
    
    return {
        "success": True,
        "article": article,
        "sheet_sync": sheet_res,
        "total_published": state["published_count"]
    }

if __name__ == "__main__":
    print("Testing single automated publish run...")
    res = publish_next_post()
    print("Result:", json.dumps(res, indent=2))
