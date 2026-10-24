"""Server HTTP cung cap du lieu nhiet do va do am gia lap ngau nhien."""

import argparse
import json
import random
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

TEMPERATURE_RANGE = (20.0, 35.0)  # Don vi: do C.
HUMIDITY_RANGE = (40, 80)  # Don vi: %.


def generate_sensor_data():
    """Sinh du lieu cam bien gia lap moi cho moi request GET."""
    return {
        "temperature": round(random.uniform(*TEMPERATURE_RANGE), 1),
        "humidity": random.randint(*HUMIDITY_RANGE),
    }


class SensorHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/api/sensor":
            # Tao du lieu moi, chuyen thanh JSON va gui ve client.
            body = json.dumps(generate_sensor_data()).encode("utf-8")
            content_type = "application/json; charset=utf-8"
        else:
            self.send_error(404, "Endpoint not found")
            return

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def main():
    parser = argparse.ArgumentParser(description="Server cam bien HTTP - Bai 1")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    try:
        with ThreadingHTTPServer((args.host, args.port), SensorHandler) as server:
            print(f"Server: http://{args.host}:{args.port}", flush=True)
            print("API: GET /api/sensor -> du lieu gia lap ngau nhien moi", flush=True)
            print("Nhiet do: 20-35 do C; do am: 40-80%.", flush=True)
            print("Nhan Ctrl+C de dung server.", flush=True)
            server.serve_forever()
    except KeyboardInterrupt:
        print("\nDa dung server.")
    except OSError as exc:
        parser.exit(1, f"Khong khoi dong duoc server: {exc}\n")


if __name__ == "__main__":
    main()
