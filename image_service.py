import os
import json
import urllib.request
import urllib.parse
from env_loader import get_secret

UNSPLASH_ACCESS_KEY = get_secret("UNSPLASH_ACCESS_KEY")
USED_IMAGES_FILE = r"C:\Users\Admin\.gemini\antigravity\scratch\generalpedia\data\used_images.json"

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

def fetch_unique_unsplash_image(query):
    """
    Fetches a photo via Unsplash API ensuring each image is used EXACTLY ONCE globally
    by tracking and enforcing image ID uniqueness.
    """
    used_ids = get_used_images()
    clean_q = urllib.parse.quote(query.strip())
    
    url = f"https://api.unsplash.com/search/photos?query={clean_q}&client_id={UNSPLASH_ACCESS_KEY}&per_page=20&orientation=landscape"
    req = urllib.request.Request(url, headers={'User-Agent': 'GeneralPedia/1.0'})
    
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            results = data.get('results', [])
            
            # Find the first image ID that has NEVER been used before
            for photo in results:
                photo_id = str(photo.get('id', ''))
                if photo_id and photo_id not in used_ids:
                    record_used_image(photo_id)
                    img_url = photo['urls'].get('regular') or photo['urls'].get('small')
                    alt = photo.get('alt_description') or query
                    author = photo.get('user', {}).get('name', 'Unsplash Contributor')
                    return {
                        "id": photo_id,
                        "url": img_url,
                        "alt": alt,
                        "credit": author
                    }
                    
            # If all were used, try first word
            words = query.split()
            if len(words) > 1:
                return fetch_unique_unsplash_image(words[0])
    except Exception as e:
        print(f"Unsplash API error for '{query}': {e}")
        
    return None
