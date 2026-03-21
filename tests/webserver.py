from http.server import BaseHTTPRequestHandler, HTTPServer

class RedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(301)
        self.send_header('Location', 'http://mycustomurl.htb')
        self.end_headers()

HTTPServer(('0.0.0.0', 8080), RedirectHandler).serve_forever()
