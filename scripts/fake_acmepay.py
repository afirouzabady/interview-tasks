"""Stand-in for the Acme Pay sandbox API, which is not reachable from outside our VPN.

    python scripts/fake_acmepay.py     # serves fixtures/acmepay_orders.json on :9099
"""
import json
import pathlib
from http.server import BaseHTTPRequestHandler, HTTPServer

ORDERS = json.loads(
    (pathlib.Path(__file__).resolve().parent.parent / "fixtures" / "acmepay_orders.json").read_text(encoding="utf-8")
)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        order_ref = self.path.rsplit("/", 1)[-1]
        order = ORDERS.get(order_ref)
        body = json.dumps(order if order else {"error": "not_found"}).encode("utf-8")

        self.send_response(200 if order else 404)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    print("fake Acme Pay listening on http://127.0.0.1:9099")
    HTTPServer(("127.0.0.1", 9099), Handler).serve_forever()
