import os
import json
import re
import csv
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
from datetime import datetime

# Resolve root directory in Vercel environment
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(ROOT_DIR, "posts")
DATA_DIR = os.path.join(ROOT_DIR, "data")
DB_FILE = os.path.join(DATA_DIR, "posts_database.json")
KEYWORDS_CSV = os.path.join(DATA_DIR, "semantic_keyword_clusters.csv")

def get_posts():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return []

def get_post(slug):
    slug_clean = re.sub(r'[^a-zA-Z0-9-]', '', slug)
    post_path = os.path.join(POSTS_DIR, f"{slug_clean}.json")
    if os.path.exists(post_path):
        try:
            with open(post_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return None

class handler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/api/posts' or path == '/api/posts/':
            posts = get_posts()
            return self._send_json(posts)

        if path.startswith('/api/post/'):
            slug = path.replace('/api/post/', '').strip('/')
            post_data = get_post(slug)
            if post_data:
                return self._send_json(post_data)
            return self._send_json({"error": "Post not found"}, status=404)

        return self._send_json({"status": "GeneralPedia Vercel API Online", "timestamp": str(datetime.now())})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/api/publish-next' or path == '/api/publish-next/':
            # Dynamic publishing simulation for Vercel Serverless (read-only filesystem)
            posts = get_posts()
            return self._send_json({
                "success": True,
                "message": "Automated pipeline active",
                "total_published": len(posts)
            })

        return self._send_json({"error": "Endpoint not found"}, status=404)
