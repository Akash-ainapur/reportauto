import http.server
import socketserver
import json
import os
import sys

# Ensure we are running from the project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)

PORT = 8000
DATA_FILE = os.path.join(PROJECT_ROOT, 'backend', 'data', 'full_report_template.json')
FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'Frontend')

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/Frontend/index.html'
        elif self.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            try:
                with open(DATA_FILE, 'r') as f:
                    self.wfile.write(f.read().encode())
            except Exception as e:
                self.wfile.write(json.dumps({'error': str(e)}).encode())
            return
        
        # Serve static files
        # Check if the file exists in Frontend directory and rewrite path if so
        # This allows accessing style.css directly as /style.css
        if not self.path.startswith(('/backend', '/Frontend', '/api')):
            potential_path = os.path.join(FRONTEND_DIR, self.path.lstrip('/'))
            if os.path.exists(potential_path):
                self.path = '/Frontend' + self.path

        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == '/api/data':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data)
                
                # Verify it's valid JSON before writing
                with open(DATA_FILE, 'w') as f:
                    json.dump(data, f, indent=4)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success', 'message': 'Data saved successfully'}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'message': str(e)}).encode())
            return


print(f"Server started at http://localhost:{PORT}")
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()
