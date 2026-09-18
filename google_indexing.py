import os
import json
import requests
from env_loader import get_secret

INDEXING_ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
SCOPES = ["https://www.googleapis.com/auth/indexing"]

def submit_url_to_google_indexing(url, notification_type="URL_UPDATED"):
    """
    Submits a URL to the Google Web Search Indexing API.
    notification_type: 'URL_UPDATED' or 'URL_DELETED'
    """
    raw_key = get_secret("GOOGLE_INDEXING_KEY")
    if not raw_key:
        print("[Google Indexing API] GOOGLE_INDEXING_KEY not found in environment. Skipping indexing ping.")
        return {"success": False, "message": "GOOGLE_INDEXING_KEY not set"}

    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import Request
    except ImportError:
        print("[Google Indexing API Warning] google-auth package not installed. Skipping indexing ping.")
        return {"success": False, "message": "google-auth not installed"}

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
        token = credentials.token

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        payload = {
            "url": url,
            "type": notification_type
        }

        response = requests.post(INDEXING_ENDPOINT, headers=headers, json=payload, timeout=20)
        res_data = response.json() if response.content else {}

        if response.status_code == 200:
            print(f"[Google Indexing API Success] URL successfully submitted: {url}")
            return {"success": True, "data": res_data}
        else:
            print(f"[Google Indexing API Error] Status {response.status_code}: {res_data}")
            return {"success": False, "status_code": response.status_code, "error": res_data}

    except Exception as e:
        print(f"[Google Indexing API Exception] Failed to submit URL: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    test_url = "https://www.generalpedia.com/roth-ira-calculator-how-works-formula-quick"
    print(f"Testing Google Indexing API for: {test_url}")
    result = submit_url_to_google_indexing(test_url)
    print("Result:", result)
