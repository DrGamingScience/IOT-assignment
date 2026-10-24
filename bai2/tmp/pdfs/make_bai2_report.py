from pathlib import Path
from textwrap import wrap
from xml.sax.saxutils import escape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted, PageBreak

root = Path(r'D:/IOT-asm/bai2')
for name, file in [('VN', 'arial.ttf'), ('Bold', 'arialbd.ttf'), ('Code', 'consola.ttf')]:
    pdfmetrics.registerFont(TTFont(name, 'C:/Windows/Fonts/' + file))
pdfmetrics.registerFontFamily('VN', normal='VN', bold='Bold')
styles = {
    'title': ParagraphStyle('title', fontName='Bold', fontSize=17, leading=23, spaceAfter=10),
    'heading': ParagraphStyle('heading', fontName='Bold', fontSize=12, leading=17, spaceBefore=8, spaceAfter=8),
    'body': ParagraphStyle('body', fontName='VN', fontSize=10, leading=15, spaceAfter=8),
    'code': ParagraphStyle('code', fontName='Code', fontSize=7, leading=9.5, spaceAfter=9),
}
story = []
def p(text, kind='body'):
    story.append(Paragraph(text, styles[kind]))
def code(text, width=130):
    lines = []
    for line in text.splitlines():
        lines.extend(wrap(line, width, replace_whitespace=False, drop_whitespace=False) or [''])
    story.append(Preformatted('\n'.join(lines), styles['code']))
def footer(canvas, doc):
    canvas.setFont('VN', 8)
    canvas.drawString(44, 28, 'Bài tập về nhà (cá nhân) - HTTP API / ThingSpeak')
    canvas.drawRightString(A4[0]-44, 28, str(doc.page))
source = (root / 'main.py').read_text(encoding='utf-8')
p('BÀI TẬP VỀ NHÀ (CÁ NHÂN)', 'title')
p('Trao đổi dữ liệu sử dụng HTTP API - ThingSpeak', 'heading')
p('Họ tên: ...................................... &nbsp; MSSV: ........................<br/>Lớp: ..........................................')
p('<b>Trạng thái:</b> Mã nguồn đã được tạo và chạy. Cần bổ sung ảnh màn hình kết quả trên ThingSpeak trước khi nộp.')
p('1. Mục tiêu và cách thực hiện', 'heading')
p('Dùng Python và thư viện chuẩn để gửi field1 = 20 (nhiệt độ), field2 = 33 (độ ẩm) bằng GET query string và POST JSON. Chờ 16 giây giữa hai lần gửi. Sau đó GET hai bản ghi mới nhất và hiển thị hai trường trong mảng feeds.')
p('2. Mã nguồn chính: cấu hình và gửi dữ liệu', 'heading')
code(source[source.index('WRITE_API_KEY ='):source.index('def read_data():')].strip())
p('urlencode() đóng gói tham số URL. Với POST, json.dumps() tạo body UTF-8 và header application/json. Phản hồi được chuyển thành entry_id; giá trị 0 được báo là thất bại.')
story.append(PageBreak())
p('3. Mã nguồn chính: đọc dữ liệu và thực thi', 'heading')
code(source[source.index('def read_data():'):].strip())
p('json.loads() phân tích JSON; vòng lặp đọc từng phần tử feeds để lấy field1 và field2. Giá trị null được hiển thị là không có dữ liệu. Chương trình báo lỗi HTTP/kết nối và vẫn thực hiện các yêu cầu tiếp theo.')
p('Chạy chương trình', 'heading')
code('cd D:/IOT-asm/bai2\npython main.py')
p('Mặc định dùng API key và Channel ID ví dụ trong đề. Nếu dùng channel của cá nhân, cấu hình THINGSPEAK_WRITE_API_KEY và THINGSPEAK_CHANNEL_ID; channel riêng tư cần thêm THINGSPEAK_READ_API_KEY. Chi tiết có trong README.md.')
story.append(PageBreak())
p('4. Kết quả thực thi và ảnh cần bổ sung', 'heading')
p('Đã chạy main.py trong môi trường hiện tại. Cả ba request đều bị hệ điều hành chặn kết nối mạng (WinError 10013); chưa có phản hồi từ ThingSpeak. Vì vậy chưa xác nhận gửi hoặc đọc thành công, chưa xác nhận API key/channel ví dụ còn hoạt động.')
p('Log thực thi thật (không phải ảnh màn hình):')
code((root / 'output/ket-qua-chay.txt').read_text(encoding='utf-8'), width=88)
p('Bước 2: thực hiện bằng Postman', 'heading')
p('Import ThingSpeak.postman_collection.json, cập nhật Variables theo channel sử dụng. Gửi request GET /update, chờ tối thiểu 15 giây, gửi POST /update với body JSON, rồi gửi GET /channels/{channel_id}/feeds.json?results=2. Channel riêng tư cần thêm Read API Key vào request đọc.')
p('Ảnh màn hình cần bổ sung trước khi nộp', 'heading')
p('1. Terminal: hai lần gửi có entry_id khác 0 và kết quả đọc field1, field2.<br/>2. Postman: GET gửi query string và phản hồi.<br/>3. Postman: POST, header application/json, body hai trường và phản hồi.<br/>4. Postman: GET đọc dữ liệu và JSON trong feeds.')
p('HTTP 200 kèm body 0 vẫn là cập nhật thất bại. Khi chạy lại hoặc gửi từ Postman, giữ khoảng cách tối thiểu 15 giây giữa các lần cập nhật.')
p('Tài liệu tham khảo', 'heading')
p('Đề bài: Phần 2, trang 1-4 của PDF đã cung cấp.<br/>MathWorks: <link href="https://www.mathworks.com/help/thingspeak/writedata.html">Write Data</link>; <link href="https://www.mathworks.com/help/thingspeak/readdata.html">Read Data</link>.')
SimpleDocTemplate(str(root / 'output/bao-cao.pdf'), pagesize=A4, leftMargin=44, rightMargin=44, topMargin=40, bottomMargin=45).build(story, onFirstPage=footer, onLaterPages=footer)
print(root / 'output/bao-cao.pdf')
