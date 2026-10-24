"""Client Python: gui HTTP GET va hien thi du lieu ngau nhien nhan tu server."""

import argparse
import json
import math
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def read_sensor(url):
    request = Request(url, method="GET", headers={"Accept": "application/json"})
    with urlopen(request, timeout=10) as response:
        status = response.status
        data = json.loads(response.read().decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Du lieu JSON phai la mot object.")
    for field in ("temperature", "humidity"):
        value = data.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"Truong {field} phai la so.")
        if not math.isfinite(value):
            raise ValueError(f"Truong {field} phai la so huu han.")
    if not 0 <= data["humidity"] <= 100:
        raise ValueError("Do am phai nam trong khoang 0 den 100%.")
    return status, data


def main():
    parser = argparse.ArgumentParser(description="Client HTTP GET - Bai 1")
    parser.add_argument("--url", default="http://127.0.0.1:8000/api/sensor")
    args = parser.parse_args()
    try:
        print(f"Request: GET {args.url}")
        status, data = read_sensor(args.url)
        print(f"HTTP status: {status} OK")
        print("JSON:", json.dumps(data, ensure_ascii=False))
        print(f"Nhiet do (temperature): {data['temperature']:g} do C")
        print(f"Do am (humidity): {data['humidity']:g}%")
    except HTTPError as exc:
        parser.exit(1, f"Loi HTTP: {exc.code}\n")
    except (URLError, TimeoutError, OSError) as exc:
        parser.exit(1, f"Loi ket noi: {exc}\n")
    except (ValueError, UnicodeError) as exc:
        parser.exit(1, f"Loi du lieu: {exc}\n")


if __name__ == "__main__":
    main()
