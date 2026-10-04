"""
image_system.py - GeneralPedia AI & Custom Image Management System
Manages local and AI-generated image assets, ensures synchronization between
root and static hosting folders, and allows custom image attribution per article.
"""

import os
import sys
import json
import shutil
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images")
SITE_IMAGES_DIR = os.path.join(BASE_DIR, "site", "images")
POSTS_DIR = os.path.join(BASE_DIR, "posts")
DB_PATH = os.path.join(BASE_DIR, "data", "posts_database.json")

def ensure_image_directories():
    os.makedirs(IMAGES_DIR, exist_ok=True)
    os.makedirs(SITE_IMAGES_DIR, exist_ok=True)

def sync_all_images():
    """Sync all images from images/ to site/images/."""
    ensure_image_directories()
    synced = 0
    for fname in os.listdir(IMAGES_DIR):
        src = os.path.join(IMAGES_DIR, fname)
        dst = os.path.join(SITE_IMAGES_DIR, fname)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
            synced += 1
    print(f"[Image System] Synchronized {synced} images to site/images/.")
    return synced

def list_post_images():
    """List images for all posts."""
    if not os.path.exists(POSTS_DIR):
        print("Posts directory not found.")
        return
    
    print("\n" + "=" * 80)
    print("GENERALPEDIA POST IMAGE INVENTORY")
    print("=" * 80)
    
    for fname in sorted(os.listdir(POSTS_DIR)):
        if fname.endswith(".json"):
            fpath = os.path.join(POSTS_DIR, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    p = json.load(f)
                slug = p.get("slug") or p.get("id")
                feat = p.get("featured_image", "None")
                is_local = "generalpedia.com/images" in feat
                tag = "[LOCAL/AI]" if is_local else "[UNSPLASH]"
                print(f"{tag:<11} {slug:<45} -> {feat[:60]}...")
            except Exception as e:
                pass
    print("=" * 80)

def assign_custom_images(slug, feat_img_path, mid_img_path=None, feat_alt=None, mid_alt=None):
    """Assign local custom/AI images to a post and update theme."""
    ensure_image_directories()
    post_file = os.path.join(POSTS_DIR, f"{slug}.json")
    if not os.path.exists(post_file):
        print(f"Error: Post '{slug}' not found at {post_file}")
        return False
    
    with open(post_file, "r", encoding="utf-8") as f:
        post = json.load(f)
    
    # Copy featured image
    feat_dest_name = f"{slug}-featured.jpg"
    shutil.copy2(feat_img_path, os.path.join(IMAGES_DIR, feat_dest_name))
    shutil.copy2(feat_img_path, os.path.join(SITE_IMAGES_DIR, feat_dest_name))
    feat_url = f"https://www.generalpedia.com/images/{feat_dest_name}"
    post["featured_image"] = feat_url
    
    # If mid image provided
    if mid_img_path:
        mid_dest_name = f"{slug}-mid.jpg"
        shutil.copy2(mid_img_path, os.path.join(IMAGES_DIR, mid_dest_name))
        shutil.copy2(mid_img_path, os.path.join(SITE_IMAGES_DIR, mid_dest_name))
        mid_url = f"https://www.generalpedia.com/images/{mid_dest_name}"
    else:
        mid_url = None
    
    content = post.get("content_html", "")
    
    # Replace top image in HTML
    top_img_m = re.search(r'<figure[^>]*>\s*<img[^>]*src="([^"]+)"[^>]*alt="([^"]*)"[^>]*>\s*</figure>', content)
    if top_img_m:
        old_url = top_img_m.group(1)
        alt = feat_alt or top_img_m.group(2)
        new_figure = f'<figure style="margin: 24px 0;">\n    <img src="{feat_url}" alt="{alt}" width="1200" height="675" style="width: 100%; max-height: 480px; object-fit: cover; border-radius: 8px;" />\n</figure>'
        content = re.sub(r'<figure[^>]*>\s*<img[^>]*src="[^"]+"[^>]*>\s*</figure>', new_figure, content, count=1)
    
    # Replace mid image in HTML if provided
    if mid_url:
        mid_img_m = re.search(r'<figure class="mid-article-figure"[^>]*>\s*<img[^>]*src="([^"]+)"[^>]*alt="([^"]*)"[^>]*>\s*</figure>', content)
        if mid_img_m:
            alt = mid_alt or mid_img_m.group(2)
            new_mid = f'<figure class="mid-article-figure" style="margin: 36px 0;">\n    <img src="{mid_url}" alt="{alt}" width="1200" height="675" loading="lazy" style="width: 100%; max-height: 480px; object-fit: cover; border-radius: 8px;" />\n</figure>'
            content = re.sub(r'<figure class="mid-article-figure"[^>]*>\s*<img[^>]*src="[^"]+"[^>]*>\s*</figure>', new_mid, content, count=1)
    
    post["content_html"] = content
    
    # Save post
    with open(post_file, "w", encoding="utf-8") as f:
        json.dump(post, f, indent=2)
    
    # Update DB
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r", encoding="utf-8") as f:
            db = json.load(f)
        for idx, item in enumerate(db):
            if item.get("id") == slug or item.get("slug") == slug:
                db[idx] = post
                break
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2)
            
    print(f"[Image System] Successfully updated post '{slug}' with custom images!")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "sync":
            sync_all_images()
        elif cmd == "list":
            list_post_images()
        elif cmd == "assign" and len(sys.argv) >= 4:
            s = sys.argv[2]
            f_img = sys.argv[3]
            m_img = sys.argv[4] if len(sys.argv) > 4 else None
            assign_custom_images(s, f_img, m_img)
        else:
            print("Usage: python image_system.py [sync|list|assign <slug> <feat_img_path> [mid_img_path]]")
    else:
        sync_all_images()
        list_post_images()
