# Bài 3 Phần 1 — AMQP RabbitMQ — Nhóm 16

Bài lab **theo nhóm** trong đề Bài 3. Dữ liệu cảm biến được mô phỏng bằng Python; không cần thiết bị thật và không cần cài Python trên máy chạy.

## Chạy nhanh trên Windows

Cần Docker Desktop đang chạy ở chế độ **Linux containers**, có Internet lần đầu để tải image và thư viện. Mở PowerShell:

```powershell
cd D:\IOT-asm\bai3\bai3_1
Copy-Item .env.example .env
docker compose up --build -d
docker compose ps
docker compose logs -f producer consumer
```

`Ctrl+C` chỉ thoát màn hình xem log; các container vẫn chạy. Những lần sau chỉ cần `docker compose up -d`. Nếu đã chỉnh `.env`, giữ lại file đó, không copy đè.

Mở **http://localhost:15672**, đăng nhập `nhom16` / `nhom16_lab_local` (tài khoản mẫu trong `.env.example`). Chọn **Queues and Streams → it4735.nhom16.telemetry**. Lần đầu có thể chờ khoảng 1 phút để broker khởi động.

## Mô hình và thông số

```text
producer Python        RabbitMQ Docker                       consumer Python
JSON mỗi 5 giây  -->   default exchange (tên rỗng)       -->  parse JSON và in
                      routing key = tên queue                 nhiệt độ và độ ẩm
                      it4735.nhom16.telemetry             <--  ACK sau xử lý
```

Payload: `{"temperature": 23, "humidity": 33}`. Đơn vị: °C và %. Producer sinh nhiệt độ 23–35 °C và độ ẩm 40–80%. Queue durable, bản tin persistent, broker có volume; đây là cấu hình bổ sung để giữ dữ liệu khi khởi động lại. Producer bật publisher confirms. Hai chương trình khai báo cùng tên và cùng thuộc tính queue.

Trong Docker, ứng dụng kết nối tới hostname `rabbitmq`, cổng `5672`, bằng tài khoản riêng đọc từ biến môi trường. Không dùng `guest` giữa các container vì giới hạn localhost. Cổng quản trị là `15672`. Các cổng chỉ được công bố ở `127.0.0.1` cho bài lab trên một máy.

## Demo và chụp ảnh báo cáo

1. **Ảnh 1 — Các container và log:** chạy `docker compose ps` và `docker compose logs --tail 12 producer consumer`. Chụp được các dòng `SENT`, `RECEIVED`, nhiệt độ và độ ẩm.
2. **Ảnh 2 — Queue khi đang nhận:** mở trang queue, chụp tên queue, **Consumers = 1**, Ready thường bằng 0 và phần Message rates. Nếu 5 giây mới có 1 bản tin, tốc độ có thể tạm về 0 trong khoảng lấy mẫu.
3. **Ảnh 3 — Tích bản tin khoảng 30 giây:**

   ```powershell
   docker compose stop consumer
   Start-Sleep -Seconds 30
   docker compose stop producer
   ```

   Chờ giao diện cập nhật khoảng 5 giây, chụp **Consumers = 0**, **Ready tăng khoảng 6** (có thể lệch 1 do thời điểm dừng). Dừng producer giúp giữ nguyên số bản tin để chụp ảnh. Không bấm **Purge** hay **Get messages** trong lúc demo.
4. **Ảnh 4 — Nhận hết bản tin chờ:**

   ```powershell
   docker compose start consumer
   docker compose logs --since 2m consumer
   ```

   Chụp log nhiều dòng `RECEIVED` xuất hiện liên tiếp và trang queue có **Ready = 0**, **Unacked = 0**. Sau đó chạy lại `docker compose start producer`.

Lưu ảnh vào `anh_bao_cao/`, chèn vào bốn khung tương ứng trong file Word. Khung Word có gợi ý chính xác nội dung cần chụp. Không dùng ảnh minh họa thay cho ảnh chạy thật.

## Kiểm tra tự động tùy chọn

```powershell
powershell -ExecutionPolicy Bypass -File .\verify.ps1
```

Script kiểm tra gửi nhận, dừng consumer 30 giây, Ready tăng, chạy lại consumer để xả queue, thử một payload sai rồi một payload đúng. Kết quả thực tế ghi vào `output/kiem_tra.json` và `output/kiem_tra.txt`. Script tạm dừng/khởi động producer và consumer, cuối cùng đưa cả hai về trạng thái chạy. Dùng script trước khi chụp ảnh, vì script tự khởi động lại consumer.

## Giải thích mã nguồn

- `common.py`: lấy cấu hình từ môi trường, mở kết nối AMQP, khai báo queue `durable=True` dùng chung.
- `producer.py`: sinh hai giá trị, `json.dumps`, `basic_publish(exchange="", routing_key=QUEUE_NAME)` mỗi 5 giây; `delivery_mode=2`, content type JSON, xác nhận từ broker. Khi lỗi kết nối, chờ rồi kết nối lại. Khi mất xác nhận do đứt mạng, trạng thái bản tin có thể không chắc chắn; bản demo không cam kết exactly once.
- `consumer.py`: `basic_consume(auto_ack=False)`, đọc UTF-8, `json.loads`, kiểm tra hai trường số, hiển thị và ACK. Bản tin sai bị NACK với `requeue=False` nên không lặp vô hạn; bài lab không cấu hình dead letter queue nên bản tin sai sẽ bị loại bỏ. Consumer tiếp tục chạy.
- `compose.yaml`: 3 dịch vụ, chờ broker healthy, Docker DNS và volume dữ liệu.
- `Dockerfile`, `requirements.txt`: image Python 3.12 và Pika 1.3.2.

Queue giữ bản tin chưa nhận trong lúc consumer dừng; khi consumer chạy lại, nó nhận các bản tin tồn đọng. Kết luận này áp dụng cho cấu hình queue hiện tại. Với MQTT, việc nhận lại khi subscriber vắng mặt phụ thuộc QoS, session và cấu hình broker; không nên kết luận mọi topic MQTT đều luôn mất bản tin.

## Dừng và xử lý nhanh

```powershell
docker compose stop           # dừng, giữ container và dữ liệu
docker compose start          # chạy lại container đã tạo
docker compose down           # gỡ container và network, giữ volume
```

- Báo cannot connect / pipe docker_engine: mở Docker Desktop, chờ engine sẵn sàng.
- Cổng bị chiếm: đổi `AMQP_PORT` hoặc `MANAGEMENT_PORT` trong `.env`, ví dụ 5673 và 15673, rồi `docker compose up -d`; mở web ở cổng mới. Các container vẫn dùng cổng nội bộ 5672.
- Đổi user/password trong `.env` sau khi đã có volume không tự đổi tài khoản broker cũ. Giữ tài khoản ban đầu hoặc đổi trong giao diện quản trị rồi đồng bộ `.env` và tạo lại các container ứng dụng.
- Nếu báo `PRECONDITION_FAILED`, queue cũ có thuộc tính khác. Dùng queue mới bằng cách sửa `QUEUE_NAME` ở Compose, hoặc chỉ xóa queue lab khi đã nhận hết và không cần dữ liệu.

## Nộp bài

Nộp báo cáo Word đã điền thành viên và chèn ảnh, cùng mã nguồn trong thư mục này. File `Bai3_1_Nhom16_Nop_bai.zip` ở thư mục `bai3/` là gói thuận tiện; nếu bổ sung ảnh/báo cáo sau đó, cần nén lại. Không đưa `.env` hoặc thông tin đăng nhập thật vào gói nộp; đã có `.env.example` cho tài khoản demo.

Tài liệu đối chiếu: [RabbitMQ Hello World Python](https://www.rabbitmq.com/tutorials/tutorial-one-python), [RabbitMQ Work Queues](https://www.rabbitmq.com/tutorials/tutorial-two-python), [RabbitMQ Docker Official Image](https://hub.docker.com/_/rabbitmq).
