from pathlib import Path
import json
from datetime import datetime
from zoneinfo import ZoneInfo

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.shared import Cm, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(r'D:\IOT-asm\bai3\bai3_1')
TMP = Path(r'D:\IOT-asm\tmp\bai3_report')
TMP.mkdir(parents=True, exist_ok=True)
OUT = ROOT / 'Bao_cao_Bai3_Phan1_Nhom16.docx'
results = json.loads((ROOT / 'output/kiem_tra.json').read_text(encoding='utf-8-sig'))
assert results['status'] == 'PASS', results

doc = Document()
s = doc.sections[0]
s.page_width, s.page_height = Cm(21), Cm(29.7)
s.top_margin, s.bottom_margin = Cm(1.8), Cm(1.7)
s.left_margin, s.right_margin = Cm(2.1), Cm(2.0)
s.footer_distance = Cm(0.7)
for name in ('Normal', 'Title', 'Subtitle', 'Heading 1', 'Heading 2', 'Caption'):
    st = doc.styles[name]
    st.font.name = 'Times New Roman'
    st.font.color.rgb = RGBColor(0, 0, 0)
    st.font.underline = False
    fonts = st.element.get_or_add_rPr().rFonts
    fonts.set(qn('w:eastAsia'), 'Times New Roman')
    for attr in ('asciiTheme', 'hAnsiTheme', 'eastAsiaTheme', 'cstheme'):
        fonts.attrib.pop(qn('w:' + attr), None)
    for border in st.element.findall('.//' + qn('w:pBdr')):
        border.getparent().remove(border)
    st.paragraph_format.space_after = Pt(6)
doc.styles['Normal'].font.size = Pt(12)
doc.styles['Normal'].paragraph_format.line_spacing = 1.12
doc.styles['Title'].font.size = Pt(22)
doc.styles['Title'].font.bold = True
doc.styles['Title'].paragraph_format.space_after = Pt(10)
doc.styles['Subtitle'].font.size = Pt(13)
doc.styles['Heading 1'].font.size = Pt(15)
doc.styles['Heading 1'].paragraph_format.space_before = Pt(5)
doc.styles['Heading 1'].paragraph_format.space_after = Pt(8)
doc.styles['Heading 2'].font.size = Pt(12)
doc.styles['Caption'].font.size = Pt(10.5)
doc.styles['Caption'].font.italic = True
doc.styles['Caption'].font.bold = False

code_st = doc.styles.add_style('SourceCode', 1)
code_st.font.name = 'Consolas'
code_st.font.size = Pt(8.4)
code_st.font.color.rgb = RGBColor(0, 0, 0)
code_st.paragraph_format.line_spacing = 1.0
code_st.paragraph_format.space_after = Pt(0)
code_st.paragraph_format.left_indent = Cm(0.2)

def p(text='', bold=False):
    paragraph = doc.add_paragraph()
    paragraph.add_run(text).bold = bold
    return paragraph

def h(text):
    doc.add_heading(text, 1)

def code(text):
    paragraph = doc.add_paragraph(style='SourceCode')
    ppr = paragraph._p.get_or_add_pPr()
    shade = OxmlElement('w:shd'); shade.set(qn('w:fill'), 'F4F4F4'); ppr.append(shade)
    paragraph.add_run(text.strip('\n'))
    p()

def table(headers, rows, widths):
    t = doc.add_table(rows=1, cols=len(headers))
    t.autofit = False
    for c, width in zip(t.columns, widths): c.width = Cm(width)
    for i, title in enumerate(headers): t.rows[0].cells[i].text = title
    for row in rows:
        cells = t.add_row().cells
        for i, value in enumerate(row): cells[i].text = str(value)
    for ri, row in enumerate(t.rows):
        trPr = row._tr.get_or_add_trPr()
        cant = OxmlElement('w:cantSplit'); trPr.append(cant)
        if ri == 0:
            repeat = OxmlElement('w:tblHeader'); trPr.append(repeat)
        for ci, cell in enumerate(row.cells):
            cell.width = Cm(widths[ci])
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            tcPr = cell._tc.get_or_add_tcPr()
            margins = OxmlElement('w:tcMar')
            for side in ('top', 'left', 'bottom', 'right'):
                m = OxmlElement(f'w:{side}'); m.set(qn('w:w'), '90'); m.set(qn('w:type'), 'dxa'); margins.append(m)
            tcPr.append(margins)
            borders = OxmlElement('w:tcBorders')
            for side in ('top', 'left', 'bottom', 'right'):
                b = OxmlElement(f'w:{side}'); b.set(qn('w:val'), 'single'); b.set(qn('w:sz'), '4'); b.set(qn('w:color'), 'D9D9D9'); borders.append(b)
            tcPr.append(borders)
            sh = OxmlElement('w:shd'); sh.set(qn('w:fill'), 'DCE6F1' if ri == 0 else ('F5F7FA' if ri % 2 == 0 else 'FFFFFF')); tcPr.append(sh)
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_after = Pt(2)
                paragraph.paragraph_format.line_spacing = 1.05
                for run in paragraph.runs:
                    run.font.size = Pt(10.5)
                    run.bold = ri == 0
    p()
    return t

def screenshot(number, title, lines, caption):
    im = Image.new('RGB', (1500, 630), '#FAFAFA')
    d = ImageDraw.Draw(im)
    d.rectangle((2, 2, 1497, 627), outline='#B8BEC6', width=3)
    f1 = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 36)
    f2 = ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf', 28)
    d.text((750, 175), f'CHÈN ẢNH {number}', font=f1, fill='#59616B', anchor='mm')
    d.text((750, 240), title, font=f2, fill='#59616B', anchor='mm')
    for i, line in enumerate(lines): d.text((750, 315 + i*48), line, font=f2, fill='#737B85', anchor='mm')
    fn = TMP / f'placeholder_{number}.png'; im.save(fn)
    pp = doc.add_paragraph(); pp.paragraph_format.space_after = Pt(3)
    pp.add_run().add_picture(str(fn), width=Cm(16.8))
    pp = doc.add_paragraph(caption, 'Caption')
    pp.paragraph_format.space_after = Pt(12)

# Page 1
doc.add_paragraph('Báo cáo Bài 3\nTrao đổi dữ liệu bằng AMQP', 'Title')
doc.add_paragraph('Phần 1 Bài lab trên lớp theo nhóm\nMã nhóm 16', 'Subtitle')
p('Thành viên nhóm  ........................................................................................')
p('Lớp  ........................................    Ngày thực hiện  23 tháng 10 năm 2026')
h('1 Mục tiêu và mô hình hệ thống')
p('Nhóm 16 xây dựng hệ thống mô phỏng cảm biến gồm một producer, một RabbitMQ broker và một consumer. Producer gửi nhiệt độ và độ ẩm dưới dạng JSON mỗi 5 giây; consumer nhận, phân tích và hiển thị dữ liệu. Toàn bộ hệ thống chạy bằng Docker Compose trên một máy.')
p('Kết quả kiểm tra cho thấy queue giữ bản tin trong thời gian consumer dừng và chuyển tiếp các bản tin đang chờ khi consumer hoạt động trở lại. Các vị trí chèn ảnh thực nghiệm được bố trí ở cuối báo cáo.')
code('Producer Python  -->  default exchange ""\n                          | routing key = ten queue\n                          v\n                 it4735.nhom16.telemetry  -->  Consumer Python\n                          ^                    |\n                          +------- ACK --------+')
table(['Thông số', 'Giá trị của nhóm 16'], [
    ('Giao thức', 'AMQP 0-9-1 qua thư viện Pika'),
    ('Queue và routing key', 'it4735.nhom16.telemetry'),
    ('Exchange', 'Default exchange có tên là chuỗi rỗng'),
    ('Bản tin mẫu', '{"temperature": 23, "humidity": 33}'),
    ('Chu kỳ và đơn vị', '5 giây; nhiệt độ °C; độ ẩm %'),
    ('Broker và giao diện web', 'rabbitmq:5672 nội bộ; localhost:15672 trên máy'),
], [4.4, 12.4])
p('Các tệp chính gồm common.py, producer.py, consumer.py, compose.yaml, Dockerfile và requirements.txt. Cảm biến trong bài là dữ liệu mô phỏng, không sử dụng phần cứng thật.')

# Page 2
doc.add_page_break()
h('2 Producer và cách gửi bản tin')
p('common.py đọc hostname và tài khoản từ biến môi trường, tạo BlockingConnection và khai báo queue. Cả producer và consumer đều gọi cùng hàm này để tránh khác thuộc tính queue.')
code('QUEUE_NAME = os.getenv("QUEUE_NAME", "it4735.nhom16.telemetry")\n\ndef declare_queue(channel):\n    return channel.queue_declare(queue=QUEUE_NAME, durable=True)')
p('Trong producer.py, các dòng chính trong vòng lặp gửi như sau. Biến interval mặc định bằng 5, lấy từ INTERVAL_SECONDS. Phần thiết lập kết nối và xử lý dừng nằm trong mã nguồn đính kèm.')
src = (ROOT / 'producer.py').read_text(encoding='utf-8')
start = src.index('                payload = ')
end = src.index('                sent += 1')
block = src[start:end]
code('\n'.join(line[16:] if line.startswith(' '*16) else line for line in block.splitlines()))
p('Các giá trị nhiệt độ và độ ẩm được sinh ngẫu nhiên, làm tròn một chữ số thập phân rồi chuyển thành JSON và mã hóa UTF-8. Trong cấu hình này, nhiệt độ nằm trong khoảng 23 đến 35 °C và độ ẩm từ 40 đến 80%.')
p('exchange="" chọn default exchange có sẵn của RabbitMQ. RabbitMQ tự tạo binding giữa default exchange và mỗi queue, với routing key bằng tên queue. Vì vậy producer gửi trực tiếp tới it4735.nhom16.telemetry mà không cần tự khai báo exchange hoặc binding.')
p('durable=True giữ khai báo queue khi broker khởi động lại; delivery_mode=2 đánh dấu bản tin persistent. Docker volume giữ dữ liệu broker khi tạo lại container. channel.confirm_delivery() bật xác nhận từ broker; mandatory=True phát hiện trường hợp bản tin không được định tuyến tới queue.')
p('Sau mỗi lần gửi, chương trình ghi log SENT rồi chờ đủ chu kỳ bằng connection.sleep theo từng khoảng ngắn. Cách chờ này vẫn xử lý heartbeat và phản hồi tín hiệu dừng. Khi lỗi kết nối, ứng dụng chờ 5 giây rồi kết nối lại. Cấu hình này không bảo đảm xử lý đúng một lần trong mọi sự cố mạng.')

# Page 3
doc.add_page_break()
h('3 Consumer và cách xác nhận bản tin')
p('Consumer khai báo cùng queue, đặt prefetch_count=1 và sử dụng xác nhận thủ công. Callback on_message xử lý từng bản tin như sau.')
src = (ROOT / 'consumer.py').read_text(encoding='utf-8')
start = src.index('def on_message(')
end = src.index('\n\ndef main()', start)
code(src[start:end])
code('channel.basic_qos(prefetch_count=1)\nchannel.basic_consume(queue=QUEUE_NAME,\n                      on_message_callback=on_message,\n                      auto_ack=False)')
p('parse_telemetry giải mã UTF-8 và gọi json.loads. Hàm yêu cầu JSON object có hai trường temperature và humidity là số hữu hạn; giá trị độ ẩm phải nằm trong khoảng 0 đến 100. Consumer hiển thị hai trường cùng đơn vị đo, sau đó mới gọi basic_ack.')
p('ACK cho biết consumer đã xử lý xong. Ready là số bản tin đang chờ được giao; Unacked là số bản tin đã giao nhưng chưa được xác nhận. Với consumer xử lý nhanh, hai chỉ số thường về 0 ngay sau mỗi lần nhận.')
p('Nếu JSON sai hoặc thiếu trường hợp lệ, consumer in JSON ERROR và gọi basic_nack với requeue=False. Bản tin lỗi bị loại bỏ vì bài lab không cấu hình dead letter queue; consumer tiếp tục nhận bản tin tiếp theo. Cơ chế này tránh lặp vô hạn với một bản tin hỏng.')
p('Khi consumer dừng, producer vẫn gửi vào queue. Các bản tin chưa giao chuyển thành Ready và được giữ trong queue. Khi consumer chạy lại, RabbitMQ chuyển các bản tin chờ cho consumer; sau khi xử lý và ACK, Ready và Unacked trở về 0.')
p('Không nên khái quát rằng MQTT luôn mất bản tin khi subscriber vắng mặt: khả năng nhận lại còn phụ thuộc QoS, session và cấu hình broker. Thí nghiệm này trực tiếp chứng minh hành vi của queue RabbitMQ đang sử dụng.')

# Page 4
doc.add_page_break()
h('4 Chạy hệ thống và kết quả kiểm tra')
p('Yêu cầu môi trường là Docker Desktop chạy Linux containers. Không cần cài Python trên máy chủ. Chạy các lệnh sau trong PowerShell tại thư mục bài; chỉ copy .env ở lần đầu.')
code('cd D:\\IOT-asm\\bai3\\bai3_1\nCopy-Item .env.example .env\ndocker compose up --build -d\ndocker compose ps\ndocker compose logs -f producer consumer')
p('Mở http://localhost:15672, đăng nhập bằng tài khoản mẫu nhom16 / nhom16_lab_local, rồi chọn Queues and Streams và queue it4735.nhom16.telemetry. Tài khoản lấy từ .env; producer và consumer dùng hostname rabbitmq trong Docker. Ctrl+C ở màn hình xem log chỉ thoát theo dõi log.')
p('Quy trình chụp kết quả: ghi nhận trạng thái gửi nhận; dừng consumer khoảng 30 giây; dừng producer để giữ nguyên số bản tin cho ảnh; chạy lại consumer để nhận hết rồi khởi động producer trở lại.')
code('docker compose stop consumer\nStart-Sleep -Seconds 30\ndocker compose stop producer\n# Chup trang queue sau khi chi so cap nhat\ndocker compose start consumer\ndocker compose logs --since 2m consumer\n# Chup queue da ve 0, sau do:\ndocker compose start producer')
before, stopped, after = results['before'], results['stopped_30_seconds'], results['resumed']
when = datetime.fromisoformat(stopped['time']).astimezone(ZoneInfo('Asia/Ho_Chi_Minh')).strftime('%H:%M ngày %d/%m/%Y')
p(f'Kiểm tra thực tế bằng verify.ps1 trên Docker tại {when}. Kết quả gốc được lưu trong output/kiem_tra.json và output/kiem_tra.txt.', bold=True)
table(['Trạng thái', 'Ready', 'Unacked', 'Consumer'], [
    ('Trước khi dừng', before['ready'], before['unacked'], before['consumers']),
    ('Dừng consumer khoảng 30 giây', stopped['ready'], stopped['unacked'], stopped['consumers']),
    ('Chạy lại và nhận hết', after['ready'], after['unacked'], after['consumers']),
], [9.1, 2.3, 2.7, 2.7])
p('Kiểm tra bổ sung gửi chuỗi hello rồi JSON hợp lệ cho kết quả PASS: consumer báo lỗi bản tin đầu và tiếp tục hiển thị temperature=23 C, humidity=33 %. Các ảnh màn hình được chèn tại bốn khung ở các trang sau.')
p('Tài liệu tham khảo: đề Bài 3 trong thư mục bai3; RabbitMQ Hello World Python https://www.rabbitmq.com/tutorials/tutorial-one-python; RabbitMQ Work Queues https://www.rabbitmq.com/tutorials/tutorial-two-python; Docker Official Image https://hub.docker.com/_/rabbitmq.', False)

# Page 5
doc.add_page_break()
h('5 Ảnh chạy chương trình và trang queue')
p('Thay từng hình giữ chỗ bằng ảnh chụp thực tế: nhấn phải vào hình, chọn Change Picture hoặc Thay đổi ảnh, chọn ảnh đã lưu trong anh_bao_cao. Điền danh sách thành viên ở trang đầu trước khi nộp.')
screenshot(1, 'Ba container và log gửi nhận',
           ['docker compose ps', 'docker compose logs --tail 12 producer consumer'],
           'Hình 1  RabbitMQ, producer và consumer đang chạy; log hiển thị nhiệt độ và độ ẩm.')
screenshot(2, 'Queue khi consumer đang hoạt động',
           ['it4735.nhom16.telemetry', 'Consumers = 1 và phần Message rates'],
           'Hình 2  Trang quản trị queue nhóm 16 khi hệ thống gửi và nhận dữ liệu bình thường.')
p('Gợi ý chụp ảnh: giữ được tên queue và các nhãn Ready, Unacked, Consumers trong cùng ảnh. Với chu kỳ 5 giây, biểu đồ tốc độ có thể tạm bằng 0 giữa hai bản tin.')

# Page 6
doc.add_page_break()
h('6 Ảnh kiểm chứng lưu bản tin trong queue')
p('Dừng consumer khoảng 30 giây trong khi producer tiếp tục gửi. Sau đó dừng producer để có thời gian chụp ảnh, rồi chạy lại consumer và quan sát queue được xử lý hết.')
screenshot(3, 'Queue tích bản tin khi consumer dừng',
           ['Consumers = 0 và Ready tăng khoảng 6 bản tin', 'Chờ giao diện cập nhật khoảng 5 giây trước khi chụp'],
           f'Hình 3  Bản tin chờ trong queue khi consumer dừng. Lần kiểm tra tự động ghi nhận Ready = {stopped["ready"]}.')
screenshot(4, 'Consumer chạy lại và nhận hết bản tin',
           ['Ready = 0 và Unacked = 0', 'Log RECEIVED xuất hiện liên tiếp khi nhận dồn'],
           'Hình 4  Consumer nhận các bản tin tồn đọng; queue trở về trạng thái không còn bản tin chờ.')
p('Nhận xét: thí nghiệm cho thấy producer và consumer hoạt động độc lập về thời gian nhờ queue. Việc dừng consumer không làm mất các bản tin đã được broker tiếp nhận và đang chờ trong lần thử này.')

# Page numbers are useful in this multi-page report.
f = s.footer.paragraphs[0]
f.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r = f.add_run('Nhóm 16  |  '); r.font.size = Pt(9)
field = OxmlElement('w:fldSimple'); field.set(qn('w:instr'), 'PAGE'); f._p.append(field)
doc.core_properties.title = 'Báo cáo Bài 3 Phần 1 Nhóm 16'
doc.core_properties.author = 'Nhóm 16'
doc.core_properties.subject = 'Trao đổi dữ liệu cảm biến bằng AMQP và RabbitMQ Docker'
doc.save(OUT)
print(OUT)
