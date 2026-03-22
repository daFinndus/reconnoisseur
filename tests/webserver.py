from http.server import BaseHTTPRequestHandler, HTTPServer


class RedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self.send_response(301)
        self.send_header("Location", "http://dafinndus.htb")
        self.end_headers()


HTTPServer(("0.0.0.0", 61240), RedirectHandler).serve_forever()
