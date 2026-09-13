import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

try:
    from config import SITE_DIR, POSTS_DIR, DATA_DIR
    from auto_publisher import publish_next_post, get_posts_database
except ImportError:
    from .config import SITE_DIR, POSTS_DIR, DATA_DIR
    from .auto_publisher import publish_next_post, get_posts_database

PORT = 8080

class GeneralPediaHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SITE_DIR, **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        
        # API: List all posts
        if parsed.path == '/api/posts':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            posts = get_posts_database()
            self.wfile.write(json.dumps(posts).encode('utf-8'))
            return
            
        # API: Get single post
        if parsed.path.startswith('/api/post/'):
            post_id = parsed.path.replace('/api/post/', '').strip('/')
            post_path = os.path.join(POSTS_DIR, f"{post_id}.json")
            if os.path.exists(post_path):
                with open(post_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode('utf-8'))
                return
            else:
                self.send_response(404)
                self.end_headers()
                return

        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        
        # API: Trigger publish next
        if parsed.path == '/api/publish-next':
            result = publish_next_post()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
            return
            
        self.send_response(404)
        self.end_headers()

def run_server():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, GeneralPediaHandler)
    print(f"GeneralPedia.com live server running at http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    run_server()
