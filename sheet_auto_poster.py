import os
import io
import json
import urllib.request
import pandas as pd
from datetime import datetime

SHEET_EXPORT_URL = "https://docs.google.com/spreadsheets/d/1IDS7DUc4PrlYbxhKwlqsoeQK70JH10-M_Qq80zm_-b0/export?format=csv&gid=758476499"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(BASE_DIR, "posts")
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_FILE = os.path.join(DATA_DIR, "posts_database.json")
INDEX_HTML = os.path.join(BASE_DIR, "index.html")

try:
    from article_generator import generate_article
except ImportError:
    from .article_generator import generate_article

def fetch_online_sheet_keywords():
    """Fetch keywords directly from user's live online Google Sheet URL"""
    print(f"Fetching keywords directly from online Google Sheet...")
    req = urllib.request.Request(
        SHEET_EXPORT_URL,
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        content = resp.read().decode('utf-8', errors='ignore')
        df = pd.read_csv(io.StringIO(content))
        print(f"Successfully loaded {len(df)} keyword clusters directly from online Google Sheet!")
        return df

def run_auto_post_from_sheet(count=1):
    """
    Picks next topics directly from the online Google Sheet,
    generates optimized articles, updates posts database, and updates index.html.
    """
    df = fetch_online_sheet_keywords()
    
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(POSTS_DIR, exist_ok=True)
    
    posts = []
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                posts = json.load(f)
        except Exception:
            posts = []
            
    existing_ids = {p.get('id') for p in posts}
    
    published_now = 0
    for idx, row in df.iterrows():
        primary_kw = str(row['Primary_Focus_Keyword']).strip()
        sem_raw = str(row.get('Semantic_Keywords_List', ''))
        semantic_kws = [k.strip() for k in sem_raw.split(',') if k.strip() and k.strip().lower() != 'none (single standalone topic)']
        
        from article_generator import slugify
        slug = slugify(primary_kw)
        
        if slug in existing_ids:
            continue
            
        vol = row.get('Primary_Volume', 0)
        kd = row.get('Primary_KD', 0)
        cpc = row.get('Primary_CPC', 0.0)
        
        article = generate_article(primary_kw, semantic_kws, volume=vol, kd=kd, cpc=cpc)
        
        # Save individual post JSON
        post_path = os.path.join(POSTS_DIR, f"{slug}.json")
        with open(post_path, 'w', encoding='utf-8') as f:
            json.dump(article, f, indent=2)
            
        # Add to database
        posts.insert(0, article)
        existing_ids.add(slug)
        published_now += 1
        print(f"-> Published from Sheet: '{article['title']}' ({article['category_name']})")
        
        if published_now >= count:
            break
            
    # Save updated database
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(posts, f, indent=2)
        
    print(f"Done! Total posts now in database: {len(posts)}")
    return published_now

if __name__ == "__main__":
    run_auto_post_from_sheet(2)
