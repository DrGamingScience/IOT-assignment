# Bài 1 - Phần 1: Trao đổi dữ liệu sử dụng HTTP API

Chỉ thực hiện **bài lab trên lớp (Phần 1)**. Không bao gồm ThingSpeak hoặc bài tập về nhà.

## Yêu cầu và kết quả

- Server có nhiệt độ **23°C**, độ ẩm **33%** (dữ liệu mẫu cố định).
- Client gửi **HTTP GET** đến `http://127.0.0.1:8000/api/sensor`.
- Server trả **200 OK**, `Content-Type: application/json; charset=utf-8`.
- Client phân tích JSON và hiển thị hai giá trị.

```json
{"temperature": 23, "humidity": 33}
```

## Chạy chương trình

Cần Python 3.9 trở lên. Không cần cài thư viện bên ngoài.
Mở hai cửa sổ terminal tại thư mục này (thư mục chứa `server.py`).

**Cửa sổ 1 - server:**

```console
python server.py
```

**Cửa sổ 2 - client:**

```console
python client.py
```

Kết quả:

```text
Request: GET http://127.0.0.1:8000/api/sensor
HTTP status: 200 OK
JSON: {"temperature": 23, "humidity": 33}
Nhiet do (temperature): 23 do C
Do am (humidity): 33%
```

Nếu máy dùng lệnh `py`, thay `python` bằng `py`.
Nhấn Ctrl+C tại cửa sổ server để kết thúc.

## Client trình duyệt và ảnh kết quả

Sau khi bật server, mở **http://127.0.0.1:8000/** rồi bấm **Gửi GET tới server**.
Trang hiển thị dữ liệu nhận được, request, mã trạng thái và JSON phản hồi.
Không mở `client.html` trực tiếp bằng đường dẫn file; hãy mở qua server như trên.

- `output/anh_client_web.jpg`: ảnh chụp client web sau khi thực hiện GET.
- `output/anh_client_python.jpg`: ảnh chụp trang hiển thị log từ lần chạy client Python thực tế.
- `output/client-output.txt`: đầu ra client Python được lưu khi chạy kiểm tra.
- `output/kiem-tra.txt`: kết quả kiểm tra HTTP và client.
- `evidence.html`: trang lưu kết quả kiểm tra đã thực hiện, không phải màn hình terminal.

## Cấu trúc mã nguồn

| File | Vai trò |
| --- | --- |
| `server.py` | Tạo server HTTP và API cảm biến, phục vụ client web |
| `client.py` | Client dòng lệnh, gửi GET và phân tích JSON |
| `client.html` | Client trình duyệt, gửi GET bằng `fetch()` |
| `verify.py` | Chạy kiểm tra trên server đang bật, lưu log và trang bằng chứng |

Chạy kiểm tra lại (server phải đang bật):

```console
python verify.py
```

## Đổi cổng nếu 8000 đang được sử dụng

```console
python server.py --port 8080
python client.py --url http://127.0.0.1:8080/api/sensor
python verify.py --base-url http://127.0.0.1:8080
```

Client có timeout 10 giây và báo lỗi HTTP, lỗi kết nối hoặc JSON không hợp lệ.
Đường dẫn API không tồn tại trả mã 404. Chương trình không kết nối cảm biến vật lý;
đề bài cho phép server có thông tin cảm biến mẫu.

## Nộp bài

Nộp báo cáo PDF cùng file ZIP mã nguồn. Báo cáo để trống tên nhóm, thành viên và lớp
để người nộp điền bằng chức năng chú thích văn bản của trình đọc PDF hoặc tự ghi
thông tin trong bản báo cáo trước khi nộp.
