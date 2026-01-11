#!/usr/bin/env python3
"""Custom HTTP server with correct MIME types for Angular/TypeScript"""
import http.server
import socketserver
import os

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def guess_type(self, path):
        """Override MIME type guessing for TypeScript files"""
        mimetype, encoding = super().guess_type(path)
        if path.endswith('.tsx') or path.endswith('.ts'):
            return 'application/javascript', encoding
        return mimetype, encoding
    
    def end_headers(self):
        # Ensure correct Content-Type header
        path = self.path.split('?')[0]
        if path.endswith('.tsx') or path.endswith('.ts'):
            # Remove any existing Content-Type and set correct one
            if 'Content-Type' in self._headers_buffer:
                self._headers_buffer = [h for h in self._headers_buffer if not h.startswith(b'Content-Type')]
            self.send_header('Content-Type', 'application/javascript; charset=utf-8')
        super().end_headers()
    
    def log_message(self, format, *args):
        # Suppress verbose logging
        pass

if __name__ == '__main__':
    PORT = 3000
    os.chdir('/Users/markforster/Downloads/pdf-concept-tagger (2)')
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"✅ Frontend server: http://localhost:{PORT}")
        print("   Serving with correct MIME types")
        print("   Press Ctrl+C to stop")
        httpd.serve_forever()
