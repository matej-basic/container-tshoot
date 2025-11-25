import http.server
import socketserver
import os

PORT = os.getenv("PORT", "8080")

handler = http.server.SimpleHTTPRequestHandler
httpd = socketserver.TCPServer(("127.0.0.1", PORT), handler)

print(f"Serving on port {PORT}")
httpd.serve_forever()
