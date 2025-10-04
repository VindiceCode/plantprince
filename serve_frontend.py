#!/usr/bin/env python3
"""
Simple HTTP server to serve the frontend HTML file.
This avoids CORS issues when accessing the backend API.
"""
import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

PORT = 3000
FRONTEND_DIR = Path("frontend")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)

if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🌿 Smart Garden Planner Frontend")
        print(f"Serving at http://localhost:{PORT}")
        print(f"Frontend directory: {FRONTEND_DIR.absolute()}")
        print("\nPress Ctrl+C to stop the server")
        
        # Open browser automatically
        webbrowser.open(f"http://localhost:{PORT}")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped")