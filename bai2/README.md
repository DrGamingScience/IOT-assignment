# Bài 2 - Bài tập về nhà (cá nhân)

Thực hiện Phần 2 trong PDF bằng Python, chỉ dùng thư viện chuẩn.

- GET: gửi field1 (nhiệt độ = 20), field2 (độ ẩm = 33) trong query string, dùng urlencode().
- POST: gửi hai trường trong body JSON, header Content-Type: application/json.
- Chờ 16 giây giữa hai lần gửi để đáp ứng mức tối thiểu 15 giây của đề.
- GET: đọc hai bản ghi mới nhất, parse JSON và hiển thị field1, field2 trong mảng feeds.
- Phản hồi 0 được báo là cập nhật thất bại; entry_id khác 0 là thành công.

## Chạy

Cần Python 3 và kết nối Internet. Trong PowerShell:

~~~powershell
cd D:\IOT-asm\bai2
python main.py
~~~

Chương trình mặc định dùng API key và Channel ID **ví dụ trong PDF**. Chưa xác nhận thông tin ví dụ còn hoạt động. Nếu dùng channel của bạn, bật Field 1 (Temperature) và Field 2 (Humidity), lấy Write API Key cùng Channel ID của channel đó, rồi đặt:

~~~powershell
$env:THINGSPEAK_WRITE_API_KEY = "WRITE_API_KEY_CUA_BAN"
$env:THINGSPEAK_CHANNEL_ID = "CHANNEL_ID_CUA_BAN"
python main.py
~~~

Nếu channel riêng tư, đặt thêm Read API Key trước khi chạy:

~~~powershell
$env:THINGSPEAK_READ_API_KEY = "READ_API_KEY_CUA_BAN"
~~~

Đổi TEMPERATURE và HUMIDITY ở đầu main.py nếu cần giá trị khác. Nếu máy dùng lệnh py, thay python bằng py. Chờ ít nhất 15 giây sau lần gửi trước nếu chạy lại.

## Bước 2 - Postman

1. Import ThingSpeak.postman_collection.json vào Postman.
2. Tại Variables của collection, đặt write_api_key và channel_id tương ứng với channel của bạn (mặc định là ví dụ trong đề).
3. Gửi request 1, chờ ít nhất 15 giây, rồi gửi request 2.
4. Gửi request 3, xem JSON trong feeds. Với channel riêng tư, thêm query parameter api_key bằng Read API Key vào request 3.
5. Chụp ảnh từng request và phản hồi. HTTP 200 kèm body 0 vẫn là cập nhật thất bại.

## Báo cáo và kết quả

- output/bao-cao.pdf: báo cáo ngắn gọn, mã nguồn chính và giải thích.
- output/ket-qua-chay.txt: log chạy thật trong môi trường hiện tại.

Môi trường hiện tại chặn kết nối mạng (WinError 10013), nên chưa xác nhận gửi/đọc thành công với ThingSpeak. Báo cáo ghi rõ giới hạn này, chưa có ảnh kết quả thành công. Trước khi nộp, chạy trên máy có Internet, điền thông tin cá nhân và bổ sung ảnh màn hình terminal cùng ba request Postman vào báo cáo.

Tài liệu API: [Write Data](https://www.mathworks.com/help/thingspeak/writedata.html), [Read Data](https://www.mathworks.com/help/thingspeak/readdata.html).
