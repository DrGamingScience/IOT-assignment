from pathlib import Path
from zipfile import ZipFile
from lxml import etree

root = Path(r'D:\IOT-asm')
source = root / 'tmp/review-bai2/source-for-captions.docx'
target = root / 'bai2/output/NguyenTriHieu_202416203_HoanThien.docx'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
ns = {'w': W}
q = lambda name: '{' + W + '}' + name
captions = [
    'Hình 1. Kết quả chạy Python gửi dữ liệu bằng GET, POST JSON và đọc hai bản ghi mới nhất.',
    'Hình 2. Gửi nhiệt độ 20°C và độ ẩm 33% bằng GET trên Postman; nhận entry_id = 15061.',
    'Hình 3. Gửi nhiệt độ 20°C và độ ẩm 33% bằng POST JSON trên Postman; nhận entry_id = 15066.',
    'Hình 4. Đọc hai bản ghi mới nhất của channel bằng GET trên Postman với tham số results=2.',
]

with ZipFile(source) as zin:
    tree = etree.fromstring(zin.read('word/document.xml'))
    body = tree.find('w:body', ns)
    for p in list(body.findall('w:p', ns)):
        text = ''.join(p.xpath('.//w:t/text()', namespaces=ns))
        if text.startswith('Hình 3 Request POST'):
            body.remove(p)
    pictures = [p for p in body.findall('w:p', ns) if p.find('.//w:drawing', ns) is not None]
    assert len(pictures) == 4, len(pictures)
    for picture, text in zip(pictures, captions):
        image_props = picture.find('w:pPr', ns)
        if image_props is None:
            image_props = etree.Element(q('pPr'))
            picture.insert(0, image_props)
        if image_props.find('w:keepNext', ns) is None:
            etree.SubElement(image_props, q('keepNext'))
        p = etree.Element(q('p'))
        props = etree.SubElement(p, q('pPr'))
        etree.SubElement(props, q('pStyle')).set(q('val'), 'Caption')
        etree.SubElement(props, q('keepLines'))
        spacing = etree.SubElement(props, q('spacing'))
        for k,v in {'before':'100','after':'120','line':'240','lineRule':'auto'}.items():
            spacing.set(q(k), v)
        etree.SubElement(props, q('jc')).set(q('val'), 'center')
        run = etree.SubElement(p, q('r'))
        rprops = etree.SubElement(run, q('rPr'))
        fonts = etree.SubElement(rprops, q('rFonts'))
        for k in ('ascii','hAnsi','cs'):
            fonts.set(q(k), 'Times New Roman')
        etree.SubElement(rprops, q('i'))
        etree.SubElement(rprops, q('color')).set(q('val'), '000000')
        etree.SubElement(rprops, q('sz')).set(q('val'), '22')
        etree.SubElement(rprops, q('szCs')).set(q('val'), '22')
        etree.SubElement(run, q('t')).text = text
        picture.addnext(p)
    xml = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)
    with ZipFile(target, 'w') as zout:
        for info in zin.infolist():
            zout.writestr(info, xml if info.filename == 'word/document.xml' else zin.read(info.filename))

with ZipFile(target) as result:
    output_xml = etree.fromstring(result.read('word/document.xml'))
    texts = [''.join(p.xpath('.//w:t/text()', namespaces=ns)) for p in output_xml.findall('.//w:body/w:p', ns)]
    assert [t for t in texts if t.startswith('Hình ')] == captions
    assert len(output_xml.findall('.//w:drawing', ns)) == 4
print(target)
print('Verified 4 captions and 4 original images.')
