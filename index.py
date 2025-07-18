from flask import Flask, request, make_response, abort
from pathlib import Path
import html
import markdown  # pip install markdown

app = Flask(__name__)
NOTES_DIR = Path(__file__).with_suffix('') / 'notes'
NOTES_DIR.mkdir(exist_ok=True)

def note_path(slug: str) -> Path | None:
    if not slug or any(c in slug for c in ('/', '\\')):
        return None
    return NOTES_DIR / f'{slug}.txt'

# ----------------- 编辑器 -----------------
@app.route('/<slug>', methods=['GET'])
def editor(slug):
    p = note_path(slug)
    if p is None:
        return 'Invalid slug', 400
    text = p.read_text(encoding='utf-8') if p.exists() else ''
    return f'''
<!doctype html>
<meta charset="utf-8"/>
<title>{html.escape(slug)}</title>
<style>
 body {{ margin:0; font-family:sans-serif; }}
 textarea {{ width:100%; height:100vh; border:none; outline:none;
             padding:1rem; box-sizing:border-box; resize:none; font-size:1rem; }}
</style>
<textarea id="t" placeholder="开始输入吧，刷新即保存">{html.escape(text)}</textarea>
<script>
const slug = '{html.escape(slug)}';
window.addEventListener('beforeunload', () => {
  navigator.sendBeacon('/' + slug, document.getElementById('t').value);
});
</script>
'''

# ----------------- 保存接口 -----------------
@app.route('/<slug>', methods=['POST'])
def save(slug):
    p = note_path(slug)
    if p is None:
        return 'Invalid slug', 400
    p.write_text(request.get_data(as_text=True), encoding='utf-8')
    return 'ok'

# ------------- Markdown 预览路由 -------------
@app.route('/<slug>.md', methods=['GET'])
def preview(slug):
    p = note_path(slug)
    if p is None:
        abort(404)
    if not p.exists():
        abort(404)
    md_text = p.read_text(encoding='utf-8')
    html_body = markdown.markdown(md_text, extensions=['fenced_code', 'tables'])
    return f'''
<!doctype html>
<meta charset="utf-8"/>
<title>{html.escape(slug)} - preview</title>
<link rel="stylesheet"
 href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.2.0/github-markdown.min.css">
<style>
 .markdown-body {{ box-sizing:border-box; min-width:200px; max-width:980px;
                   margin:0 auto; padding:2rem; }}
</style>
<article class="markdown-body">
{html_body}
</article>
'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
