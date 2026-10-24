"""Use packaged DOCX rasterizer with native Word PDF fallback on Windows.
The runtime manifest contains no LibreOffice build for Windows.
"""
from pathlib import Path
import importlib.util
import os
import sys

skill = Path(r'C:\Users\nguye\.codex\plugins\cache\openai-primary-runtime\documents\26.1020.11127\skills\documents\render_docx.py')
pdf = Path(r'D:\IOT-asm\tmp\bai3_report\render\report.pdf')
docx = Path(r'D:\IOT-asm\bai3\bai3_1\Bao_cao_Bai3_Phan1_Nhom16.docx')
assert pdf.stat().st_mtime >= docx.stat().st_mtime, 'Refresh Word PDF before rasterizing'
poppler = r'C:\Users\nguye\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin'
os.environ['PATH'] = poppler + os.pathsep + os.environ['PATH']
spec = importlib.util.spec_from_file_location('docx_renderer', skill)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.convert_to_pdf = lambda *args, **kwargs: (str(pdf), 'Native Word PDF fallback')
sys.argv = [str(skill), str(docx), '--output_dir', str(pdf.parent), '--width', '1600', '--height', '2200']
# Keep the packaged converter defaults; only conversion to PDF changes.
paths = module.rasterize(str(docx), str(pdf.parent), dpi=150, verbose=False, emit_pdf=False)
print('\n'.join(paths))
