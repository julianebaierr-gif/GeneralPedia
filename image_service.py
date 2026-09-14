import os
import json
import urllib.request
import urllib.parse
from env_loader import get_secret

UNSPLASH_ACCESS_KEY = get_secret("UNSPLASH_ACCESS_KEY")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USED_IMAGES_FILE = os.path.join(BASE_DIR, "data", "used_images.json")

def get_used_images():
    if os.path.exists(USED_IMAGES_FILE):
        try:
            with open(USED_IMAGES_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def record_used_image(image_id):
    used = get_used_images()
    used.add(str(image_id))
    os.makedirs(os.path.dirname(USED_IMAGES_FILE), exist_ok=True)
    with open(USED_IMAGES_FILE, "w", encoding="utf-8") as f:
        json.dump(list(used), f, indent=2)

def fetch_unique_unsplash_image(query, fallback_terms=None):
    """
    Fetches a photo via Unsplash API ensuring each image is used EXACTLY ONCE globally
    by tracking and enforcing image ID uniqueness.
    Tries primary query, then fallback_terms, then individual keywords.
    """
    used_ids = get_used_images()
    
    # Candidate queries list to try in order
    queries_to_try = []
    if isinstance(query, list):
        queries_to_try.extend([q.strip() for q in query if q and q.strip()])
    elif query and query.strip():
        queries_to_try.append(query.strip())
        
    if fallback_terms:
        if isinstance(fallback_terms, list):
            queries_to_try.extend([t.strip() for t in fallback_terms if t and t.strip()])
        elif isinstance(fallback_terms, str) and fallback_terms.strip():
            queries_to_try.append(fallback_terms.strip())

    for q in queries_to_try:
        clean_q = urllib.parse.quote(q)
        url = f"https://api.unsplash.com/search/photos?query={clean_q}&client_id={UNSPLASH_ACCESS_KEY}&per_page=20&orientation=landscape"
        req = urllib.request.Request(url, headers={'User-Agent': 'GeneralPedia/1.0'})
        
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                results = data.get('results', [])
                
                for photo in results:
                    photo_id = str(photo.get('id', ''))
                    if photo_id and photo_id not in used_ids:
                        record_used_image(photo_id)
                        img_url = photo['urls'].get('regular') or photo['urls'].get('small')
                        alt = photo.get('alt_description') or q
                        author = photo.get('user', {}).get('name', 'Unsplash Contributor')
                        return {
                            "id": photo_id,
                            "url": img_url,
                            "alt": alt,
                            "credit": author
                        }
        except Exception as e:
            print(f"Unsplash API error for '{q}': {e}")
            continue

    # Final fallback: split first query into keywords
    if queries_to_try:
        words = queries_to_try[0].split()
        for w in words:
            if len(w) > 3 and not w.isdigit():
                clean_w = urllib.parse.quote(w)
                url = f"https://api.unsplash.com/search/photos?query={clean_w}&client_id={UNSPLASH_ACCESS_KEY}&per_page=15&orientation=landscape"
                req = urllib.request.Request(url, headers={'User-Agent': 'GeneralPedia/1.0'})
                try:
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        data = json.loads(resp.read().decode('utf-8'))
                        for photo in data.get('results', []):
                            photo_id = str(photo.get('id', ''))
                            if photo_id and photo_id not in used_ids:
                                record_used_image(photo_id)
                                img_url = photo['urls'].get('regular') or photo['urls'].get('small')
                                alt = photo.get('alt_description') or w
                                author = photo.get('user', {}).get('name', 'Unsplash Contributor')
                                return {
                                    "id": photo_id,
                                    "url": img_url,
                                    "alt": alt,
                                    "credit": author
                                }
                except Exception:
                    continue

    return None
