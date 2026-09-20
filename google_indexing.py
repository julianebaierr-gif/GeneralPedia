import os
import re
import json
import time
import xml.etree.ElementTree as ET
import requests
from env_loader import get_secret

INDEXING_ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
SCOPES = ["https://www.googleapis.com/auth/indexing"]

def get_google_auth_token():
    raw_key = get_secret("GOOGLE_INDEXING_KEY")
    if not raw_key:
        return None

    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import Request
    except ImportError:
        print("[Google Indexing API Warning] google-auth package not installed.")
        return None

    try:
        if os.path.exists(raw_key):
            service_account_info = json.load(open(raw_key, 'r', encoding='utf-8'))
        else:
            service_account_info = json.loads(raw_key)

        credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=SCOPES
        )
        credentials.refresh(Request())
        return credentials.token
    except Exception as e:
        print(f"[Google Indexing API Exception] Failed to obtain auth token: {e}")
        return None

def submit_url_to_google_indexing(url, notification_type="URL_UPDATED", token=None):
    """
    Submits a single URL to the Google Web Search Indexing API.
    notification_type: 'URL_UPDATED' or 'URL_DELETED'
    """
    if not token:
        token = get_google_auth_token()

    if not token:
        print("[Google Indexing API] GOOGLE_INDEXING_KEY not available or invalid. Skipping indexing ping.")
        return {"success": False, "message": "Authentication token unavailable"}

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    payload = {
        "url": url,
        "type": notification_type
    }

    try:
        response = requests.post(INDEXING_ENDPOINT, headers=headers, json=payload, timeout=15)
        res_data = response.json() if response.content else {}

        if response.status_code == 200:
            print(f"[Google Indexing API Success] URL indexed: {url}")
            return {"success": True, "data": res_data}
        else:
            print(f"[Google Indexing API Error] ({response.status_code}) for {url}: {res_data}")
            return {"success": False, "status_code": response.status_code, "error": res_data}
    except Exception as e:
        print(f"[Google Indexing API Exception] Error submitting {url}: {e}")
        return {"success": False, "error": str(e)}

def extract_urls_from_sitemap(sitemap_path=None):
    """
    Extracts all URLs listed in sitemap.xml.
    """
    if not sitemap_path:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        sitemap_path = os.path.join(base_dir, "sitemap.xml")

    if not os.path.exists(sitemap_path):
        print(f"[Google Indexing API] Sitemap file not found at: {sitemap_path}")
        return []

    try:
        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        urls = []
        for elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
            if elem.text:
                urls.append(elem.text.strip())
        return urls
    except Exception as e:
        print(f"[Google Indexing API] Failed to parse sitemap: {e}")
        return []

def submit_all_site_urls(sitemap_path=None):
    """
    Submits all URLs in the entire website (from sitemap.xml) to Google Indexing API.
    """
    urls = extract_urls_from_sitemap(sitemap_path)
    if not urls:
        print("[Google Indexing API] No URLs found in sitemap.")
        return {"total": 0, "success": 0, "failed": 0}

    token = get_google_auth_token()
    if not token:
        print("[Google Indexing API] GOOGLE_INDEXING_KEY not set. Skipping batch submission.")
        return {"total": len(urls), "success": 0, "failed": len(urls), "message": "No key configured"}

    print(f"\n=======================================================")
    print(f"[Google Indexing API] Starting Full Site Indexing for {len(urls)} URLs...")
    print(f"=======================================================")

    success_count = 0
    failed_count = 0

    for idx, url in enumerate(urls, 1):
        res = submit_url_to_google_indexing(url, token=token)
        if res.get("success"):
            success_count += 1
        else:
            failed_count += 1
        time.sleep(0.2)

    print(f"=======================================================")
    print(f"[Google Indexing API Complete] Total: {len(urls)} | Success: {success_count} | Failed: {failed_count}")
    print(f"=======================================================\n")

    return {
        "total": len(urls),
        "success": success_count,
        "failed": failed_count
    }

if __name__ == "__main__":
    print("Running full site indexing submission...")
    submit_all_site_urls()
