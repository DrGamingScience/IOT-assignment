from pathlib import Path
p=Path('tmp/pdfs/make_report.py')
s=p.read_text(encoding='utf-8-sig')
s=s.replace('Preformatted(escape(text.rstrip()),', 'Preformatted(text.rstrip(),')
s=s.replace('story.append(Image(str(path), width=width, height=width * size[1] / size[0]))', 'story.append(Image(str(path), width=450, height=450 * size[1] / size[0]))')
old=s[s.index('server_excerpt = '):s.index('\ncode(server_excerpt)')]
new='''server_text = (ROOT/'server.py').read_text(encoding='utf-8')
server_excerpt = server_text[server_text.index('import argparse'):server_text.index('        elif path')] + '        else:\\n            self.send_error(404, "Endpoint not found")\\n            return\\n\\n' + server_text[server_text.index('        self.send_response'):server_text.index('\\n\\ndef main')]'''
s=s.replace(old,new)
s=s.replace("code('\\n'.join(server_lines[49:54]))", "code(server_text[server_text.index('    try:\\n'):server_text.index('    except KeyboardInterrupt')])")
s=s.replace("code('\\n'.join(client_lines[2:]))", "code('import argparse' + (ROOT/'client.py').read_text(encoding='utf-8').split('import argparse',1)[1])")
p.write_text(s,encoding='utf-8')
r=Path('bai1/README.md')
r.write_text(r.read_text(encoding='utf-8').replace('anh_client_web.png','anh_client_web.jpg').replace('anh_client_python.png','anh_client_python.jpg'),encoding='utf-8')
