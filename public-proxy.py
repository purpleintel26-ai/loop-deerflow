#!/usr/bin/env python3
"""
Simple HTTP reverse proxy to expose DeerFlow publicly
Uses only standard library - no external dependencies
"""

import http.server
import socketserver
import urllib.request
import urllib.error
import threading
import json
from datetime import datetime

# Configuration
LOCAL_DEERFLOW = "http://localhost:8000"
PUBLIC_PORT = 8765  # Change this if needed

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    """Proxy requests to DeerFlow backend"""
    
    def log_message(self, format, *args):
        """Custom logging"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {self.client_address[0]} - {format % args}")
    
    def do_GET(self):
        """Handle GET requests"""
        self._proxy_request("GET")
    
    def do_POST(self):
        """Handle POST requests"""
        self._proxy_request("POST")
    
    def _proxy_request(self, method):
        """Proxy request to DeerFlow"""
        target_url = f"{LOCAL_DEERFLOW}{self.path}"
        
        try:
            # Create request
            req = urllib.request.Request(
                target_url,
                method=method,
                headers=self._get_headers()
            )
            
            # Add body for POST
            if method == "POST" and 'Content-Length' in self.headers:
                content_length = int(self.headers['Content-Length'])
                body = self.rfile.read(content_length)
                req.data = body
            
            # Forward request
            with urllib.request.urlopen(req, timeout=30) as response:
                # Send status
                self.send_response(response.status)
                
                # Send headers
                for header, value in response.headers.items():
                    if header.lower() not in ['transfer-encoding', 'content-encoding']:
                        self.send_header(header, value)
                self.end_headers()
                
                # Send body
                self.wfile.write(response.read())
                
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.end_headers()
            self.wfile.write(f"Error: {e.reason}".encode())
            
        except Exception as e:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(f"Proxy error: {str(e)}".encode())
    
    def _get_headers(self):
        """Filter and return headers"""
        headers = {}
        for key, value in self.headers.items():
            if key.lower() not in ['host', 'content-length']:
                headers[key] = value
        return headers


def get_public_ip():
    """Get public IP address"""
    try:
        with urllib.request.urlopen('https://api.ipify.org', timeout=5) as response:
            return response.read().decode().strip()
    except:
        return "unknown"


def main():
    """Start proxy server"""
    public_ip = get_public_ip()
    
    print("=" * 60)
    print("🚀 DeerFlow Public Proxy")
    print("=" * 60)
    print(f"\nLocal DeerFlow:  {LOCAL_DEERFLOW}")
    print(f"Public Port:     {PUBLIC_PORT}")
    print(f"Public IP:       {public_ip}")
    print(f"\n🔗 PUBLIC URL:")
    print(f"   http://{public_ip}:{PUBLIC_PORT}")
    print(f"\n📊 Health Check:")
    print(f"   curl http://{public_ip}:{PUBLIC_PORT}/health")
    print(f"\n📚 API Docs:")
    print(f"   http://{public_ip}:{PUBLIC_PORT}/docs")
    print("\n" + "=" * 60)
    print("Press Ctrl+C to stop")
    print("=" * 60 + "\n")
    
    # Start server
    with socketserver.ThreadingTCPServer(("0.0.0.0", PUBLIC_PORT), ProxyHandler) as httpd:
        httpd.serve_forever()


if __name__ == "__main__":
    main()
