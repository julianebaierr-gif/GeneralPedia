import os
import json
import glob

base_dir = r'C:\Users\Admin\.gemini\antigravity\scratch\generalpedia'
posts_dir = os.path.join(base_dir, 'posts')
db_path = os.path.join(base_dir, 'data', 'posts_database.json')

if os.path.exists(db_path):
    with open(db_path, 'r', encoding='utf-8') as f:
        try:
            db = json.load(f)
        except Exception:
            db = []
else:
    db = []

db_map = {p.get('id'): i for i, p in enumerate(db)}

post_files = glob.glob(os.path.join(posts_dir, '*.json'))
print(f"Found {len(post_files)} post files in posts/")

updated_count = 0
added_count = 0

for pf in post_files:
    with open(pf, 'r', encoding='utf-8') as f:
        p_data = json.load(f)
    
    p_id = p_data.get('id') or p_data.get('slug')
    if not p_id:
        continue
    
    # Ensure consistent fields
    p_data['id'] = p_id
    p_data['slug'] = p_id
    
    if p_id in db_map:
        idx = db_map[p_id]
        db[idx] = p_data
        updated_count += 1
    else:
        db.append(p_data)
        db_map[p_id] = len(db) - 1
        added_count += 1

with open(db_path, 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print(f"Sync complete: {updated_count} updated, {added_count} added. Total in DB: {len(db)}")
