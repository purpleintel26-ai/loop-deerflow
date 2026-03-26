#!/usr/bin/env python3
import http.server, socketserver, urllib.request
from datetime import datetime

LOCAL = 'http://localhost:8000'
PORT = 8765

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, f, *a): 
        print(f'[{datetime.now().strftime("%H:%M:%S")}] {f%a}')
    
    def do_GET(self):
        if self.path == '/':
            self.serve_file('/root/.openclaw/workspace/loop-deerflow/public/index.html', 'text/html')
        else:
            self.proxy()
    
    def serve_file(self, path, ctype):
        try:
            with open(path, 'rb') as f:
                self.send_response(200)
                self.send_header('Content-Type', ctype)
                self.end_headers()
                self.wfile.write(f.read())
        except Exception as e:
            self.send_error(404, str(e))
    
    def proxy(self):
        try:
            headers = {h:v for h,v in self.headers.items() if h.lower() != 'host'}
            req = urllib.request.Request(f'{LOCAL}{self.path}', headers=headers)
            with urllib.request.urlopen(req, timeout=30) as r:
                self.send_response(r.status)
                for h,v in r.headers.items():
                    if h.lower() not in ['transfer-encoding']:
                        self.send_header(h, v)
                self.end_headers()
                self.wfile.write(r.read())
        except Exception as e:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(f'Proxy Error: {e}'.encode())

print('🚀 LOOP DeerFlow')
print(f'📍 http://0.0.0.0:{PORT}')
socketserver.ThreadingTCPServer(('0.0.0.0', PORT), Handler).serve_forever()
