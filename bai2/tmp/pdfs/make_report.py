from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted, Table, TableStyle, Image, PageBreak
from PIL import Image as PILImage

ROOT = Path(r'D:\IOT-asm\bai1')
OUT = ROOT / 'output'
OUT.mkdir(exist_ok=True)
for name, filename in [('Arial', 'arial.ttf'), ('ArialBold', 'arialbd.ttf'), ('Mono', 'consola.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(Path('C:/Windows/Fonts') / filename)))
pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='ArialBold', italic='Arial', boldItalic='ArialBold')
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='VN', fontName='Arial', fontSize=10.4, leading=15.5, spaceAfter=9, textColor=colors.HexColor('#243647')))
styles.add(ParagraphStyle(name='VNTitle', fontName='ArialBold', fontSize=23, leading=30, spaceAfter=15, textColor=colors.HexColor('#126a71')))
styles.add(ParagraphStyle(name='VNH', fontName='ArialBold', fontSize=14, leading=20, spaceBefore=8, spaceAfter=10, textColor=colors.HexColor('#126a71')))
styles.add(ParagraphStyle(name='SmallVN', fontName='Arial', fontSize=8.8, leading=12.5, spaceAfter=8, textColor=colors.HexColor('#526477')))
styles.add(ParagraphStyle(name='CodeVN', fontName='Mono', fontSize=7.6, leading=10.3, leftIndent=10, rightIndent=10, borderPadding=10, backColor=colors.HexColor('#f0f4f8'), spaceAfter=12))
story = []
width = A4[0] - 88

def p(text, style='VN'):
    story.append(Paragraph(text, styles[style]))

def code(text):
    story.append(Preformatted(text.rstrip(), styles['CodeVN']))

def picture(name, caption):
    path = OUT / name
    size = PILImage.open(path).size
    story.append(Image(str(path), width=450, height=450 * size[1] / size[0]))
    story.append(Spacer(1, 5))
    p(caption, 'SmallVN')

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor('#dce5ee'))
    canvas.line(44, 38, A4[0]-44, 38)
    canvas.setFont('Arial', 8)
    canvas.setFillColor(colors.HexColor('#526477'))
    canvas.drawString(44, 25, 'Bài 1 - Phần 1 | Trao đổi dữ liệu sử dụng HTTP API')
    canvas.drawRightString(A4[0]-44, 25, f'Trang {doc.page}')
    canvas.restoreState()

p('BÁO CÁO BÀI 1', 'VNTitle')
p('Trao đổi dữ liệu sử dụng HTTP API', 'VNH')
p('<b>Phạm vi:</b> Phần 1 - Bài lab trên lớp (theo nhóm).')
p('Nhóm: ....................................... &nbsp;&nbsp; Lớp: .......................................<br/>Thành viên: ...............................................................................................')
p('1. Mục tiêu và phương án thực hiện', 'VNH')
p('Xây dựng server có thông tin nhiệt độ và độ ẩm. Client sử dụng HTTP request với phương thức GET để nhận thông tin và hiển thị kết quả. Chương trình sử dụng Python và thư viện chuẩn, không cần cài thêm gói phụ thuộc.')
p('Server cung cấp dữ liệu mẫu cố định <b>23°C</b> và <b>33%</b> theo ví dụ trong đề. Dữ liệu truyền qua HTTP thật trên máy cục bộ; không sử dụng cảm biến vật lý.')
rows = [[Paragraph('<b>Thành phần</b>',styles['VN']), Paragraph('<b>Chức năng</b>',styles['VN'])],
        [Paragraph('server.py',styles['VN']), Paragraph('Lắng nghe tại 127.0.0.1:8000; trả dữ liệu JSON.',styles['VN'])],
        [Paragraph('client.py',styles['VN']), Paragraph('Gửi GET, phân tích JSON, hiển thị nhiệt độ và độ ẩm.',styles['VN'])],
        [Paragraph('client.html',styles['VN']), Paragraph('Client trình duyệt, hiển thị trực quan và phản hồi HTTP.',styles['VN'])]]
table = Table(rows, colWidths=[115, width-115])
table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e4f0f0')),('GRID',(0,0),(-1,-1),.5,colors.HexColor('#dce5ee')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),3)]))
story.append(table)
p('2. Luồng trao đổi và định dạng dữ liệu', 'VNH')
code('Client -> GET /api/sensor -> Server\nClient <- 200 OK + JSON   <- Server\n\n{"temperature": 23, "humidity": 33}')
p('<b>temperature:</b> nhiệt độ, đơn vị °C. <b>humidity:</b> độ ẩm, đơn vị %. Header phản hồi: <b>Content-Type: application/json; charset=utf-8</b>.')
p('3. Cách chạy', 'VNH')
p('Mở hai terminal tại thư mục chứa mã nguồn. Ở terminal thứ nhất chạy server, giữ server hoạt động rồi chạy client ở terminal thứ hai.')
code('python server.py\npython client.py')
p('Để dùng client web, mở <b>http://127.0.0.1:8000/</b> và bấm <b>Gửi GET tới server</b>. Nhấn Ctrl+C ở terminal server để dừng.', 'SmallVN')
story.append(PageBreak())

p('4. Mã nguồn chính của server', 'VNH')
p('<b>File server.py.</b> Đoạn trích dưới đây là nhánh trả dữ liệu cảm biến. Mã nguồn đầy đủ trong file còn phục vụ các trang HTML và cho phép cấu hình host/cổng.')
server_lines = (ROOT/'server.py').read_text(encoding='utf-8').splitlines()
server_text = (ROOT/'server.py').read_text(encoding='utf-8')
server_excerpt = server_text[server_text.index('import argparse'):server_text.index('        elif path')] + '        else:\n            self.send_error(404, "Endpoint not found")\n            return\n\n' + server_text[server_text.index('        self.send_response'):server_text.index('\n\ndef main')]
code(server_excerpt)
p('<b>Giải thích:</b> SENSOR_DATA lưu hai giá trị cảm biến. do_GET() xử lý request GET; urlsplit() lấy đường dẫn request. Khi client gọi /api/sensor, json.dumps() chuyển dữ liệu sang JSON, encode() chuyển sang byte để truyền qua mạng.')
p('send_response(200) báo thành công. Các header xác định kiểu nội dung, số byte phản hồi và yêu cầu không dùng dữ liệu cũ từ bộ nhớ đệm. end_headers() kết thúc phần header; wfile.write() gửi JSON tới client. Đường dẫn không tồn tại trả HTTP 404.')
p('Khởi tạo và chạy server', 'VNH')
code(server_text[server_text.index('    try:\n'):server_text.index('    except KeyboardInterrupt')])
p('ThreadingHTTPServer lắng nghe kết nối tại host/cổng đã cấu hình và xử lý nhiều request. serve_forever() giữ server hoạt động đến khi người dùng nhấn Ctrl+C. Mặc định server chỉ phục vụ trên máy cục bộ (127.0.0.1).')
p('Server còn trả client.html tại đường dẫn / để client trình duyệt có thể gửi request tới cùng server. Do đó người dùng mở trang qua HTTP thay vì mở file HTML trực tiếp.', 'SmallVN')
story.append(PageBreak())

p('5. Mã nguồn chính của client', 'VNH')
p('<b>File client.py.</b> Client sử dụng urllib.request để gửi GET, đọc phản hồi và chuyển chuỗi JSON thành dữ liệu Python.')
client_lines = (ROOT/'client.py').read_text(encoding='utf-8').splitlines()
code('import argparse' + (ROOT/'client.py').read_text(encoding='utf-8').split('import argparse',1)[1])
p('<b>Giải thích:</b> Request(..., method="GET") chỉ định phương thức GET. urlopen(..., timeout=10) mở kết nối với thời gian chờ tối đa 10 giây. response.read() đọc byte, decode("utf-8") giải mã và json.loads() phân tích JSON.')
p('Client kiểm tra hai trường là số hợp lệ, độ ẩm nằm trong khoảng 0-100%, sau đó hiển thị với đơn vị. Các nhánh except báo lỗi HTTP, lỗi kết nối và lỗi dữ liệu; khi lỗi, client kết thúc với mã 1.', 'SmallVN')
story.append(PageBreak())

p('6. Ảnh thực hiện chương trình và kết quả', 'VNH')
p('Server và hai client đã được chạy, nhận đúng nhiệt độ 23°C và độ ẩm 33%.', 'SmallVN')
picture('anh_client_web.jpg', '<b>Hình 1.</b> Client trình duyệt gửi GET thật; phản hồi 200 OK và JSON chứa temperature=23, humidity=33.')
picture('anh_client_python.jpg', '<b>Hình 2.</b> Ảnh chụp trang hiển thị đầu ra đã lưu từ lần chạy client Python thực tế và kết quả kiểm tra; không phải ảnh cửa sổ terminal.')
p('<b>Kết luận:</b> Đã hoàn thành ba yêu cầu của Phần 1: server có dữ liệu cảm biến; client gửi GET nhận dữ liệu; client hiển thị kết quả. Kiểm tra thêm đường dẫn sai trả 404 và client báo lỗi đúng.', 'SmallVN')
p('<b>Nguồn yêu cầu:</b> Bài 1. Trao đổi dữ liệu sử dụng HTTP API (VI).pdf, trang 1, mục Phần 1. Mã nguồn đầy đủ và hướng dẫn chạy đi kèm trong file ZIP.', 'SmallVN')

pdf = OUT/'Bao_cao_Bai_1_Phan_1.pdf'
SimpleDocTemplate(str(pdf),pagesize=A4,rightMargin=44,leftMargin=44,topMargin=40,bottomMargin=50,title='Báo cáo Bài 1 - Phần 1 - HTTP API',author='').build(story,onFirstPage=footer,onLaterPages=footer)
md = '''# Báo cáo Bài 1 - Phần 1: Trao đổi dữ liệu sử dụng HTTP API

Nhóm: ...
Lớp: ...
Thành viên: ...

## 1. Mục tiêu

Tạo server có dữ liệu nhiệt độ 23°C, độ ẩm 33%. Client gửi HTTP GET tới server, nhận JSON, phân tích và hiển thị kết quả.

## 2. Thiết kế

Python với thư viện chuẩn, không cần thư viện bên ngoài. API: `GET http://127.0.0.1:8000/api/sensor`. Server trả 200 OK và Content-Type application/json; charset=utf-8.

```json
{"temperature": 23, "humidity": 33}
```

Dữ liệu là mẫu cố định theo ví dụ trong đề; trao đổi HTTP thật trên máy cục bộ, không sử dụng cảm biến vật lý.

## 3. Chạy chương trình

Chạy `python server.py` tại terminal thứ nhất. Chạy `python client.py` tại terminal thứ hai. Để dùng client web, mở http://127.0.0.1:8000/ rồi bấm Gửi GET tới server. Nhấn Ctrl+C để dừng server.

## 4. Mã nguồn chính server

Đây là nhánh API cảm biến; server đầy đủ còn phục vụ giao diện HTML và nhận tùy chọn host/cổng.

```python
'''+server_excerpt+'''
```

SENSOR_DATA lưu thông tin cảm biến. do_GET xử lý GET, json.dumps chuyển dữ liệu sang JSON, encode tạo byte. Server gửi mã 200, header Content-Type/Content-Length, rồi gửi body qua wfile.write. Đường dẫn không tồn tại trả 404. ThreadingHTTPServer và serve_forever giữ server hoạt động.

## 5. Mã nguồn client

```python
'''+(ROOT/'client.py').read_text(encoding='utf-8')+'''
```

Request chỉ định GET; urlopen gửi request với timeout 10 giây; json.loads phân tích phản hồi. Client kiểm tra giá trị rồi in nhiệt độ, độ ẩm. Các nhánh except xử lý HTTP lỗi, kết nối lỗi hoặc dữ liệu sai.

## 6. Ảnh kết quả

![Client web](anh_client_web.jpg)

Hình 1. Client web gửi GET thật, nhận 200 OK, nhiệt độ 23°C và độ ẩm 33%.

![Client Python](anh_client_python.jpg)

Hình 2. Trang hiển thị đầu ra được lưu từ tiến trình chạy client.py thực tế. Đây là ảnh trình duyệt hiển thị log, không phải ảnh terminal.

## 7. Kết luận

Hoàn thành ba yêu cầu của Phần 1. Kiểm tra thêm HTTP 404 và client thoát với mã lỗi 1 khi đường dẫn API sai.

Nguồn yêu cầu: Bài 1. Trao đổi dữ liệu sử dụng HTTP API (VI).pdf, trang 1, Phần 1.
'''
(OUT/'Bao_cao_Bai_1_Phan_1.md').write_text(md,encoding='utf-8')
print(pdf)
