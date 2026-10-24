"""Bai tap ve nha ca nhan: gui va doc du lieu ThingSpeak bang HTTP API."""

import json
import os
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

# Gia tri vi du trong de; thay bang thong tin channel cua ban khi can.
WRITE_API_KEY = os.getenv("THINGSPEAK_WRITE_API_KEY", "T7H40F0X82VGW7L5")
CHANNEL_ID = os.getenv("THINGSPEAK_CHANNEL_ID", "1529099")
READ_API_KEY = os.getenv("THINGSPEAK_READ_API_KEY", "")
BASE_URL = "https://api.thingspeak.com"
TEMPERATURE = 20
HUMIDITY = 33


def send_data(method):
    fields = {"field1": TEMPERATURE, "field2": HUMIDITY}
    params = {"api_key": WRITE_API_KEY}
    if method == "GET":
        params.update(fields)
        body = None
        headers = {}
    else:
        body = json.dumps(fields).encode("utf-8")
        headers = {"Content-Type": "application/json"}

    url = BASE_URL + "/update?" + urlencode(params)
    request = Request(url, data=body, headers=headers, method=method)
    print(f"{method} /update | field1={TEMPERATURE}, field2={HUMIDITY}")
    if body is not None:
        print("Content-Type: application/json")
        print("Body:", body.decode("utf-8"))
    with urlopen(request, timeout=15) as response:
        result = response.read().decode("utf-8").strip()
        print("HTTP status:", response.status)
    entry_id = int(result)
    print("Response (entry_id):", entry_id)
    if entry_id == 0:
        print("Cap nhat that bai: kiem tra API key va khoang cach 15 giay.")
        return False
    print("Gui du lieu thanh cong.")
    return True


def read_data():
    params = {"results": 2}
    if READ_API_KEY:
        params["api_key"] = READ_API_KEY
    url = f"{BASE_URL}/channels/{CHANNEL_ID}/feeds.json?{urlencode(params)}"
    print(f"GET /channels/{CHANNEL_ID}/feeds.json?results=2")
    request = Request(url, headers={"Accept": "application/json"})
    with urlopen(request, timeout=15) as response:
        data = json.loads(response.read().decode("utf-8"))
        print("HTTP status:", response.status)
    feeds = data["feeds"]
    if not feeds:
        print("Channel chua co du lieu.")
    for feed in feeds:
        temperature = feed.get("field1")
        humidity = feed.get("field2")
        print("Entry:", feed.get("entry_id"), "| Thoi gian:", feed.get("created_at"))
        print("Nhiet do (field1):", "Khong co du lieu" if temperature is None else f"{temperature} do C")
        print("Do am (field2):", "Khong co du lieu" if humidity is None else f"{humidity}%")
    return True


def main():
    success = True
    for method in ("GET", "POST"):
        if method == "POST":
            print("\nCho 16 giay truoc lan gui tiep theo...", flush=True)
            time.sleep(16)
        try:
            success = send_data(method) and success
        except (HTTPError, URLError, OSError, ValueError) as exc:
            print(f"Loi gui {method}: {exc}")
            success = False
    print("\nDoc 2 ban ghi moi nhat:")
    try:
        read_data()
    except (HTTPError, URLError, OSError, ValueError, KeyError, TypeError) as exc:
        print("Loi doc du lieu:", exc)
        success = False
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
