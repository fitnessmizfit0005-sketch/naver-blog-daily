"""GPT 번들을 블로그 3개씩 2개 페이지로 나눈다.

날짜 페이지(docs/YYYY-MM-DD.html)의 '📦 GPT 번들' 탭 내용을 읽어서
  docs/YYYY-MM-DD-gpt1.html : 진트쌤 · 모찌코치 · 오늘뭐지
  docs/YYYY-MM-DD-gpt2.html : 스뷰김천 · 은이 · 제시카 (그 외 블로그 전부)
를 만든다. 포스팅 번호(이미지18-01 등 이름 규칙)는 원래 번호 그대로 둔다.
날짜 페이지의 GPT 번들 탭 맨 위에는 두 페이지로 가는 링크를 끼워 넣는다.

배포(Deploy Pages) 때 자동 실행되므로 생성기(generate.py)는 고칠 필요 없음.
사용: python tools/split_gpt_bundle.py [docs 폴더]
"""
import html
import pathlib
import re
import sys

GROUP1 = ["진트쌤", "모찌코치", "오늘뭐지"]
GROUP1_LABEL = "진트쌤·모찌코치·오늘뭐지"
GROUP2_LABEL = "스뷰김천·은이·제시카"
LINK_MARK = "<!-- gpt-split-links -->"

POST_HEAD = re.compile(r"^=== 포스팅 (\d+) : (\S+) .*===\s*$", re.M)
DATE_FILE = re.compile(r"^\d{4}-\d{2}-\d{2}\.html$")

PAGE = """<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{date} GPT 번들 {n}/2 · {label} · {count}개</title>
<style>
body{{font:15px/1.7 -apple-system,"Malgun Gothic","Apple SD Gothic Neo",sans-serif;margin:0;background:#faf9f7;color:#1c1b19}}
.wrap{{max-width:860px;margin:0 auto;padding:20px 16px 80px}}
h1{{font-size:18px;margin:0 0 6px}}
.sub{{color:#6b6862;font-size:13px;margin-bottom:12px}}
.sub a{{color:#2f6f4f}}
button{{border:1px solid #2f6f4f;background:#e8f2ec;color:#2f6f4f;border-radius:8px;padding:10px 16px;font-size:15px;font-weight:600;cursor:pointer;margin-bottom:12px}}
pre{{white-space:pre-wrap;word-break:break-all;background:#fff;border:1px solid #e6e3dd;border-radius:10px;padding:14px;font-size:13px}}
</style>
</head><body><div class="wrap">
<h1>📦 {date} GPT 번들 {n}/2 — {label} ({count}개 포스팅)</h1>
<div class="sub">다른 번들: <a href="{other_href}">GPT 번들 {other_n}/2 ({other_label})</a> · <a href="{date}.html">원고 페이지로</a></div>
<button id="cp">📋 GPT 번들 {n}/2 전체 복사</button>
<pre id="bundle">{text}</pre>
</div>
<script>
document.getElementById('cp').addEventListener('click',async function(){{
  var t=document.getElementById('bundle').textContent, b=this, old=b.textContent;
  try{{await navigator.clipboard.writeText(t);}}catch(e){{
    var ta=document.createElement('textarea');ta.value=t;document.body.appendChild(ta);ta.select();document.execCommand('copy');ta.remove();}}
  b.textContent='복사됨 ✓ ('+t.length+'자)';setTimeout(function(){{b.textContent=old;}},1500);
}});
</script>
</body></html>
"""


def extract_bundle(page: str):
    """GPT 번들 탭의 <pre> 텍스트를 꺼낸다. 없으면 None."""
    m = re.search(r'data-i="(\d+)">📦 GPT 번들', page)
    if not m:
        return None, None
    start = page.find(f'<section class="pane" id="pane-{m.group(1)}"')
    if start < 0:
        return None, None
    pre = re.search(r"<pre>(.*?)</pre>", page[start:], re.S)
    if not pre:
        return None, None
    return html.unescape(pre.group(1)), start


def split(text: str):
    heads = list(POST_HEAD.finditer(text))
    if not heads:
        return None
    intro = text[: heads[0].start()]
    g1, g2 = [], []
    for k, h in enumerate(heads):
        end = heads[k + 1].start() if k + 1 < len(heads) else len(text)
        block = text[h.start(): end]
        (g1 if h.group(2) in GROUP1 else g2).append(block)
    return intro, g1, g2


def build(date, n, label, intro, blocks, other_label):
    note = (f"※ 이 번들은 {n}/2 — {label} 포스팅만 들어 있습니다. "
            "포스팅 번호와 이미지 이름은 원래 번호 그대로입니다.\n\n")
    text = note + intro + "".join(blocks)
    other_n = 2 if n == 1 else 1
    return PAGE.format(
        date=date, n=n, label=label, count=len(blocks),
        other_n=other_n, other_label=other_label,
        other_href=f"{date}-gpt{other_n}.html",
        text=html.escape(text, quote=False),
    )


def inject_links(page: str, sec_start: int, date: str, c1: int, c2: int) -> str:
    if LINK_MARK in page:
        return page
    links = (f'{LINK_MARK}<div class="notes" style="margin-bottom:12px">'
             f'GPT용 나눈 번들: <a href="{date}-gpt1.html">📦 1/2 {GROUP1_LABEL} ({c1}개)</a>'
             f' · <a href="{date}-gpt2.html">📦 2/2 {GROUP2_LABEL} ({c2}개)</a></div>')
    gt = page.find(">", sec_start) + 1
    return page[:gt] + "\n  " + links + page[gt:]


def main(docs="docs"):
    docs = pathlib.Path(docs)
    made = 0
    for f in sorted(docs.iterdir()):
        if not DATE_FILE.match(f.name):
            continue
        page = f.read_text(encoding="utf-8")
        text, sec_start = extract_bundle(page)
        if text is None:
            continue
        parts = split(text)
        if parts is None:
            continue
        intro, g1, g2 = parts
        date = f.stem
        (docs / f"{date}-gpt1.html").write_text(
            build(date, 1, GROUP1_LABEL, intro, g1, GROUP2_LABEL), encoding="utf-8")
        (docs / f"{date}-gpt2.html").write_text(
            build(date, 2, GROUP2_LABEL, intro, g2, GROUP1_LABEL), encoding="utf-8")
        f.write_text(inject_links(page, sec_start, date, len(g1), len(g2)), encoding="utf-8")
        made += 1
    print(f"GPT 번들 분할: {made}일치")


if __name__ == "__main__":
    main(*sys.argv[1:])
