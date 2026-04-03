#!/usr/bin/env python3
"""
Simple OAuth proxy for Sveltia CMS / Decap CMS GitHub backend.
Run this alongside your zensical serve.
"""
import http.server
import socketserver
import urllib.request
import urllib.parse
import json
import os

PORT = 4567
CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID', '')
CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET', '')

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress logs

    def do_GET(self):
        if self.path.startswith('/auth'):
            # Exchange code for token
            query = urllib.parse.parse_qs(self.path.split('?')[1]) if '?' in self.path else {}
            code = query.get('code', [''])[0]
            
            if code:
                data = {
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET,
                    'code': code
                }
                req = urllib.request.Request(
                    'https://github.com/login/oauth/access_token',
                    data=urllib.parse.urlencode(data).encode(),
                    headers={'Accept': 'application/json'}
                )
                try:
                    with urllib.request.urlopen(req) as resp:
                        token_data = json.loads(resp.read())
                        token = token_data.get('access_token', '')
                        
                        # Redirect back to admin with token
                        self.send_response(302)
                        self.send_header('Location', f'http://localhost:8000/admin/#access_token={token}')
                        self.end_headers()
                        return
                except Exception as e:
                    print(f"Error: {e}")
            
            self.send_response(400)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Error: Set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET environment variables")
        exit(1)
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"OAuth proxy running on http://localhost:{PORT}")
        print(f"Use callback URL: http://localhost:{PORT}/auth")
        httpd.serve_forever()
