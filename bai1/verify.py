"""Kiem tra HTTP that va luu dau ra client de dua vao bao cao."""

import argparse
import html
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from urllib.error import HTTPError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description="Kiem tra Bai 1, server phai dang bat")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")
    output = ROOT / "output"
    output.mkdir(exist_ok=True)
    with urlopen(base + "/api/sensor", timeout=10) as response:
        assert response.status == 200
        assert response.headers.get_content_type() == "application/json"
        assert json.loads(response.read()) == {"temperature": 23, "humidity": 33}
    checks = ["PASS: GET /api/sensor -> 200 OK, Content-Type application/json",
              "PASS: JSON temperature=23, humidity=33"]
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    result = subprocess.run([sys.executable, str(ROOT / "client.py"), "--url", base + "/api/sensor"],
                            capture_output=True, text=True, encoding="utf-8", env=env, timeout=15)
    assert result.returncode == 0, result.stderr
    assert "23 do C" in result.stdout and "33%" in result.stdout
    checks.append("PASS: Client Python GET, parse JSON, hien thi 23 do C va 33%")
    try:
        urlopen(base + "/khong-ton-tai", timeout=10)
        raise AssertionError("Endpoint khong ton tai phai tra 404")
    except HTTPError as exc:
        assert exc.code == 404
    invalid = subprocess.run([sys.executable, str(ROOT / "client.py"), "--url", base + "/khong-ton-tai"],
                             capture_output=True, text=True, encoding="utf-8", env=env, timeout=15)
    assert invalid.returncode == 1 and "404" in invalid.stderr
    checks.append("PASS: Endpoint sai -> HTTP 404, client thoat voi ma 1")
    text = "\n".join(checks) + "\n"
    (output / "client-output.txt").write_text(result.stdout, encoding="utf-8")
    (output / "kiem-tra.txt").write_text(text, encoding="utf-8")
    timestamp = datetime.now(timezone(timedelta(hours=7))).strftime("%d/%m/%Y %H:%M:%S (UTC+7)")
    page = f'''<!doctype html><html lang="vi"><meta charset="utf-8">
<title>Bài 1 | Kết quả client Python</title>
<style>body{{background:#edf2f7;color:#162535;font:16px Arial;margin:0}}
main{{max-width:1000px;margin:42px auto;padding:0 28px}}h1{{font-size:32px}}
.label{{font-size:13px;color:#426788;font-weight:bold;letter-spacing:1px}}
p{{color:#526477;line-height:1.6}}pre{{background:#172b3e;color:#e1edf7;border-radius:12px;
padding:24px;white-space:pre-wrap;font:16px Consolas,monospace;line-height:1.7}}
.checks{{background:white;color:#126a71;border:1px solid #dce5ee;font-size:14px}}
.note{{font-size:14px}}</style><main>
<div class="label">BÀI 1 / PHẦN 1 / KẾT QUẢ CHẠY THỰC TẾ</div>
<h1>Client Python nhận dữ liệu từ server</h1>
<p>Đầu ra được lưu từ tiến trình chạy <b>client.py</b> bằng Python.<br>
Thời điểm kiểm tra: {timestamp}</p>
<pre>python client.py --url {html.escape(base)}/api/sensor\n\n{html.escape(result.stdout)}</pre>
<h2>Kiểm tra kết quả</h2><pre class="checks">{html.escape(text)}</pre>
<p class="note">Ảnh chụp trang này thể hiện log chạy thật đã lưu; đây là trang trình duyệt hiển thị log, không phải ảnh cửa sổ terminal. Dữ liệu cảm biến là mẫu cố định 23°C và 33%.</p>
</main></html>'''
    (ROOT / "evidence.html").write_text(page, encoding="utf-8")
    print(result.stdout, end="")
    print(text, end="")


if __name__ == "__main__":
    main()
