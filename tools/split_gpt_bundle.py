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
TOP_MARK = "<!-- gpt-txt-top -->"
BASE_URL = "https://fitnessmizfit0005-sketch.github.io/naver-blog-daily/"
TXT_MAX_POSTS = 7        # txt 파일 하나에 넣을 최대 포스팅 수
TXT_MAX_BYTES = 45000    # txt 파일 하나의 최대 크기(대략) — 넘으면 다음 파일로

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


def split_txt(blocks):
    """포스팅 블록들을 TXT_MAX_POSTS / TXT_MAX_BYTES 기준으로 묶는다."""
    groups, cur, size = [], [], 0
    for b in blocks:
        bs = len(b.encode("utf-8"))
        if cur and (len(cur) >= TXT_MAX_POSTS or size + bs > TXT_MAX_BYTES):
            groups.append(cur)
            cur, size = [], 0
        cur.append(b)
        size += bs
    if cur:
        groups.append(cur)
    return groups


def write_txt(docs, date, intro, blocks):
    """GPT 전용 순수 텍스트 파일(펼침·스크립트 없음): YYYY-MM-DD-gpt-1.txt … + YYYY-MM-DD-gpt-index.txt.
    각 파일 맨 끝 줄은 '=== END N건 ==='. index는 가장 마지막에 쓴다(배포는 한꺼번에 올라가지만 순서도 지킴)."""
    for old in docs.glob(f"{date}-gpt-*.txt"):
        old.unlink()
    groups = split_txt(blocks)
    total = len(groups)
    nums = lambda g: [int(POST_HEAD.match(b).group(1)) for b in g]
    lines = [f"{date} GPT 원고 텍스트 목록 — 파일 {total}개 · 포스팅 합계 {len(blocks)}건", ""]
    for k, g in enumerate(groups, 1):
        n = nums(g)
        blogs = []
        for b in g:
            bl = POST_HEAD.match(b).group(2)
            if bl not in blogs:
                blogs.append(bl)
        head = (f"### {date} GPT 원고 파일 {k}/{total} · 포스팅 {n[0]}~{n[-1]}번 · {len(g)}건 "
                f"({'·'.join(blogs)})\n"
                "### 포스팅 번호와 이미지 이름은 원래 번호 그대로입니다. 맨 끝 END 줄까지 읽혀야 정상입니다.\n\n")
        body = head + intro + "".join(g).rstrip() + f"\n\n=== END {len(g)}건 ===\n"
        name = f"{date}-gpt-{k}.txt"
        (docs / name).write_text(body, encoding="utf-8")
        lines.append(f"{k}. {BASE_URL}{name}  — 포스팅 {n[0]}~{n[-1]}번 · {len(g)}건 · {len(body)}자")
    lines += ["", f"=== END 파일 {total}개 · 포스팅 {len(blocks)}건 ==="]
    (docs / f"{date}-gpt-index.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return total


def inject_top(page, date, n_files):
    """원고 페이지 맨 위(숨겨지지 않은 곳)에 GPT용 txt 주소를 글자 그대로 적는다."""
    if TOP_MARK in page:
        page = re.sub(re.escape(TOP_MARK) + r".*?" + re.escape(TOP_MARK + "-end"), "", page, flags=re.S)
    # 2026-11-27: 원고를 볼 때 화면을 밀어내지 않도록 한 줄(가로 스크롤)로 표시.
    # 주소는 숨기지 않고 글자 그대로 둔다(GPT가 페이지 글자에서 주소를 읽음) — display:none·details 접기 금지
    urls = " | ".join(f"{BASE_URL}{date}-gpt-{k}.txt" for k in range(1, n_files + 1))
    block = (f'{TOP_MARK}<div style="padding:3px 10px;margin:4px 8px;border:1px solid #cfe0d6;border-radius:6px;'
             f'background:#f3f8f5;color:#557;font-size:11px;line-height:1.5;white-space:nowrap;overflow-x:auto">'
             f'GPT용 원고 텍스트(파일 {n_files}개) — 목록: {BASE_URL}{date}-gpt-index.txt | {urls}</div>{TOP_MARK}-end')
    m = re.search(r"<body[^>]*>", page)
    if not m:
        return page
    return page[:m.end()] + "\n" + block + page[m.end():]


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
        n_files = write_txt(docs, date, intro, g1 + g2)
        page = inject_links(page, sec_start, date, len(g1), len(g2))
        f.write_text(inject_top(page, date, n_files), encoding="utf-8")
        made += 1
    print(f"GPT 번들 분할: {made}일치 (html 2개 + txt 여러 개 + index)")


if __name__ == "__main__":
    main(*sys.argv[1:])
