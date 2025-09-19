#!/usr/bin/env python3
"""
Simple HTTP server to serve the API Gateway test UI
"""
import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 3000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers to allow requests to the API Gateway
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

def main():
    # Change to the directory containing the HTML file
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Check if the HTML file exists
    if not os.path.exists('simple_ui.html'):
        print("❌ Error: simple_ui.html not found!")
        sys.exit(1)
    
    # Start the server
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"🚀 Starting API Gateway Test UI server...")
        print(f"📱 UI available at: http://localhost:{PORT}/simple_ui.html")
        print(f"🔗 API Gateway at: http://localhost:8081")
        print(f"⏹️  Press Ctrl+C to stop the server")
        print()
        
        # Open the UI in the default browser
        try:
            webbrowser.open(f'http://localhost:{PORT}/simple_ui.html')
            print("🌐 Opened UI in your default browser")
        except:
            print("⚠️  Could not open browser automatically")
        
        print()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped")

if __name__ == "__main__":
    main()
