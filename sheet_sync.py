import os
import csv
import json
import urllib.request
from datetime import datetime
try:
    from config import SPREADSHEET_ID, SHEET_GID, APPS_SCRIPT_WEBHOOK_URL, DATA_DIR
except ImportError:
    from .config import SPREADSHEET_ID, SHEET_GID, APPS_SCRIPT_WEBHOOK_URL, DATA_DIR

LOCAL_SHEET_MIRROR = os.path.join(DATA_DIR, "published_posts_sheet.csv")

def init_local_mirror():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(LOCAL_SHEET_MIRROR):
        with open(LOCAL_SHEET_MIRROR, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Keywords", "Category", "Tags", "Status", "Post Url", "Post Date / Time"])

def log_post_to_sheet(keywords, category, tags, status, post_url, post_date_time=None):
    """
    Logs published post to Google Sheets (via Webhook if configured, plus local persistent mirror).
    """
    if not post_date_time:
        post_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    tags_str = ", ".join(tags) if isinstance(tags, list) else str(tags)
    
    # 1. Update Local Sheet Mirror
    init_local_mirror()
    with open(LOCAL_SHEET_MIRROR, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([keywords, category, tags_str, status, post_url, post_date_time])
    
    webhook_url = os.environ.get("GENERALPEDIA_SHEET_WEBHOOK", APPS_SCRIPT_WEBHOOK_URL)
    
    # 2. Update Live Google Sheet if webhook provided
    if webhook_url and webhook_url.startswith("http"):
        try:
            payload = {
                "keywords": keywords,
                "category": category,
                "tags": tags_str,
                "status": status,
                "post_url": post_url,
                "post_date_time": post_date_time
            }
            req = urllib.request.Request(
                webhook_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                return {"success": True, "source": "Google Sheets Live Webhook", "response": result}
        except Exception as e:
            return {"success": True, "source": "Local Mirror (Webhook Pending)", "error": str(e)}
            
    return {"success": True, "source": "Local Mirror (Ready for Sheet Upload)"}
