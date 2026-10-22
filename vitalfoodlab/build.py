#!/usr/bin/env python3
"""Vital Food Lab 예약 발행 원고 페이지 생성기.

posts/<날짜>.json + posts/<날짜>.body.html  ->  docs/vitalfoodlab/<날짜>.html, index.html
본문 HTML 안의 [[IMG1]] [[IMG2]] [[IMG3]] 는 미리보기에서만 이미지 위치로 표시되고,
복사되는 본문에서는 제거된다.
"""
import html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
POSTS = ROOT / "posts"
OUT = ROOT.parent / "docs" / "vitalfoodlab"
BASE = "https://fitnessmizfit0005-sketch.github.io/naver-blog-daily/vitalfoodlab/"

HUBNAV = (
    '<nav class="hubnav" aria-label="사이트 이동">'
    '<a href="https://fitnessmizfit0005-sketch.github.io/naver-blog-daily/">네이버 블로그</a>'
    '<a href="https://fitnessmizfit0005-sketch.github.io/daangn/">당근 소식</a>'
    '<a href="https://fitnessmizfit0005-sketch.github.io/shopping-shorts/">쇼핑쇼츠</a>'
    '<a href="https://fitnessmizfit0005-sketch.github.io/naver-blog-daily/sb-reels/">스뷰 릴스</a>'
    '<a class="on" aria-current="page" href="' + BASE + '">Vital Food Lab</a>'
    '</nav>'
)

CSS = """
:root{--bg:#faf9f7;--fg:#1c1b19;--muted:#6b6862;--card:#fff;--line:#e6e3dd;--accent:#2f6f4f;--accent-bg:#e8f2ec;--warn:#8a5a00;--warn-bg:#fbefd6;--img-bg:#f1f4f8;--img-line:#c9d3e0}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#17181a;--fg:#e9e7e3;--muted:#9a968e;--card:#212225;--line:#34363a;--accent:#7fd0a6;--accent-bg:#1e2f28;--warn:#e6b566;--warn-bg:#33291a;--img-bg:#1d2530;--img-line:#33465e}}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);font:15px/1.7 -apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Malgun Gothic",sans-serif;margin:0}
.wrap{max-width:860px;margin:0 auto;padding:20px 16px 80px}
h1{font-size:19px;margin:0 0 4px}
.sub{color:var(--muted);font-size:13px;margin-bottom:16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin-bottom:14px}
.card h2{font-size:14px;margin:0 0 8px;color:var(--muted);font-weight:600}
.row{display:flex;gap:10px;align-items:flex-start;padding:6px 0;border-top:1px solid var(--line)}
.row:first-of-type{border-top:0}
.k{flex:0 0 108px;color:var(--muted);font-size:13px;padding-top:2px}
.v{flex:1;min-width:0;word-break:break-word}
@media (max-width:560px){.row{flex-wrap:wrap}.k{flex-basis:100%;padding-top:0}.v{flex-basis:calc(100% - 60px)}}
.v.mono{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:13px}
button.copy{flex:0 0 auto;border:1px solid var(--accent);background:var(--accent-bg);color:var(--accent);border-radius:7px;padding:4px 10px;font-size:12px;cursor:pointer}
button.copy.big{width:100%;padding:11px;font-size:14px;font-weight:700;margin-bottom:6px}
button.copy.done{background:var(--accent);color:#fff}
.notes{background:var(--warn-bg);color:var(--warn);border-radius:8px;padding:8px 12px;font-size:13px;margin-bottom:14px}
.badges{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:14px}
.badge{font-size:12px;padding:4px 9px;border-radius:999px;background:var(--accent-bg);color:var(--accent)}
.badge.warn{background:var(--warn-bg);color:var(--warn)}
.hint{color:var(--muted);font-size:12px;margin:2px 0 4px}
.img{border-top:1px solid var(--line);padding:10px 0}
.img:first-of-type{border-top:0}
.img b{display:block;margin-bottom:6px}
.check label{display:flex;gap:8px;padding:4px 0;font-size:14px;cursor:pointer}
.preview{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:18px}
.preview h2{font-size:18px;margin:28px 0 10px;padding-left:9px;border-left:3px solid var(--accent)}
.preview h3{font-size:15px;margin:18px 0 8px}
.preview table{border-collapse:collapse;width:100%;font-size:14px;margin:8px 0 14px;display:block;overflow-x:auto}
.preview th,.preview td{border:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
.preview th{background:var(--accent-bg)}
.preview a{color:var(--accent)}
.ph{background:var(--img-bg);border:1px dashed var(--img-line);border-radius:8px;padding:14px;text-align:center;color:var(--muted);font-size:13px;margin:14px 0}
ul.list{list-style:none;padding:0;margin:0}
ul.list li{padding:10px 0;border-bottom:1px solid var(--line)}
ul.list a{font-weight:600;text-decoration:none;color:var(--fg)}
.n{color:var(--muted);font-size:13px;margin-left:6px}
.hubnav{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 12px}
.hubnav a{display:inline-block;padding:6px 14px;border-radius:999px;border:1px solid #d9d6cf;background:#fff;color:#2a2826;font:600 14px/1.35 -apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Malgun Gothic",sans-serif;text-decoration:none;white-space:nowrap}
.hubnav a.on{background:#2a2826;border-color:#2a2826;color:#fff}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .hubnav a{background:#26241f;border-color:#3b3934;color:#ece9e3}:root:not([data-theme="light"]) .hubnav a.on{background:#ece9e3;border-color:#ece9e3;color:#1c1b19}}
"""

JS = r"""
function flash(b){b.classList.add('done');var t=b.textContent;b.textContent='복사됨';setTimeout(function(){b.classList.remove('done');b.textContent=t},1400)}
function copyText(b,txt){(navigator.clipboard?navigator.clipboard.writeText(txt):Promise.reject()).then(function(){flash(b)},function(){var a=document.createElement('textarea');a.value=txt;document.body.appendChild(a);a.select();document.execCommand('copy');a.remove();flash(b)})}
document.addEventListener('click',function(e){
  var b=e.target.closest('button.copy');if(!b)return;
  if(b.dataset.src){var s=document.getElementById(b.dataset.src);copyText(b,s.textContent);return}
  if(b.dataset.rich){
    var h=document.getElementById(b.dataset.rich).textContent;
    var tmp=document.createElement('div');tmp.innerHTML=h;var plain=tmp.innerText;
    try{navigator.clipboard.write([new ClipboardItem({'text/html':new Blob([h],{type:'text/html'}),'text/plain':new Blob([plain],{type:'text/plain'})})]).then(function(){flash(b)},function(){fallbackRich(b,h)})}catch(err){fallbackRich(b,h)}
    return}
});
function fallbackRich(b,h){var d=document.createElement('div');d.contentEditable=true;d.innerHTML=h;d.style.position='fixed';d.style.left='-9999px';document.body.appendChild(d);var r=document.createRange();r.selectNodeContents(d);var s=getSelection();s.removeAllRanges();s.addRange(r);document.execCommand('copy');s.removeAllRanges();d.remove();flash(b)}
(function(){var key='vfl-check-'+document.body.dataset.date;var st={};try{st=JSON.parse(localStorage.getItem(key)||'{}')}catch(e){}
document.querySelectorAll('.check input').forEach(function(c,i){c.checked=!!st[i];c.addEventListener('change',function(){st[i]=c.checked;try{localStorage.setItem(key,JSON.stringify(st))}catch(e){}})})})();
"""


def esc(s):
    return html.escape(s, quote=True)


def row(k, v, mono=False):
    i = row.n = getattr(row, "n", 0) + 1
    return (f'<div class="row"><div class="k">{esc(k)}</div>'
            f'<div class="v{" mono" if mono else ""}" id="f{i}">{esc(v)}</div>'
            f'<button class="copy" data-src="f{i}">복사</button></div>')


def build_post(meta):
    body = (POSTS / meta["body_file"]).read_text(encoding="utf-8")
    if "[[IMG3]]" not in body:
        body = body.replace("<h2>Frequently Asked Questions</h2>", "[[IMG3]]\n\n<h2>Frequently Asked Questions</h2>", 1)
    clean = re.sub(r"\s*\[\[IMG\d\]\]\s*", "\n\n", body).strip()
    clean = re.sub(r"\n{3,}", "\n\n", clean)
    preview = body
    for i, im in enumerate(meta["images"], 1):
        preview = preview.replace(f"[[IMG{i}]]", f'<div class="ph">🖼️ Image {i} 위치 · {esc(im["filename"])}</div>')

    text = re.sub(r"<[^>]+>", " ", clean)
    words = len(text.split())
    kw = meta["focus_keyword"].lower()
    first_p = re.search(r"<p>(.*?)</p>", clean, re.S)
    intro2 = " ".join(re.findall(r"<p>(.*?)</p>", clean, re.S)[:2]).lower()
    internal = len(re.findall(r'href="https://vitalfoodlab\.com/', clean))
    sources = len(re.findall(r"pubmed\.ncbi\.nlm\.nih\.gov", clean))
    ko = bool(re.search(r"[가-힣]", text))
    md_len = len(meta["meta_description"])
    banned = bool(re.search(r"<h2>\s*(Introduction|Conclusion)\s*</h2>", clean))
    badges = [
        (f"단어 {words:,}", words >= 700),
        (f"메타 설명 {md_len}자", 120 <= md_len <= 160),
        ("키워드: 제목", kw in meta["title"].lower()),
        ("키워드: 메타", kw in meta["meta_description"].lower()),
        ("키워드: 도입부", kw in intro2),
        (f"링크 {internal}개 (내부1+관련3)", internal >= 4),
        (f"출처 {sources}개", sources >= 2),
        ("한국어 0자", not ko),
        ("Intro/Conclusion 헤딩 없음", not banned),
    ]
    badge_html = "".join(f'<span class="badge{"" if ok else " warn"}">{"✓" if ok else "!"} {esc(t)}</span>' for t, ok in badges)

    row.n = 0
    meta_rows = "".join([
        row("제목", meta["title"]),
        row("Slug", meta["slug"], True),
        row("Focus Keyword", meta["focus_keyword"]),
        row("Meta Description", meta["meta_description"]),
        row("카테고리", meta["category"]),
        row("태그", ", ".join(meta["tags"])),
        row("예약 (UTC)", meta["schedule_utc"], True),
    ])
    imgs = []
    for im in meta["images"]:
        imgs.append('<div class="img"><b>' + esc(im["label"]) + '</b>' + row("Prompt", im["prompt"]) + row("Filename", im["filename"], True) + row("ALT · Title", im["alt"]) + '</div>')
    checklist = [
        "제목 입력", f"Slug: {meta['slug']}", f"카테고리: {meta['category']}", "태그 입력",
        "본문 붙여넣기 → H2/H3 헤딩·표·링크 확인", "Image 1 삽입 + ALT·Title 입력", "Image 2 삽입 + ALT·Title 입력",
        "Image 3 삽입 + ALT·Title 입력", "Featured Image 설정 (Image 1과 동일)",
        f"Rank Math Focus Keyword: {meta['focus_keyword']}", "Rank Math Meta Description 입력",
        f"예약 발행: {meta['schedule_utc']} UTC ({meta['schedule_kst']})", "미리보기로 링크·표 확인 후 예약",
    ]
    check_html = "".join(f'<label><input type="checkbox"> {esc(c)}</label>' for c in checklist)

    page = f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(meta['date'])} · {esc(meta['title'])}</title><style>{CSS}</style></head>
<body data-date="{esc(meta['date'])}"><div class="wrap">
{HUBNAV}
<p class="sub"><a href="index.html">← Vital Food Lab 목록</a></p>
<h1>{esc(meta['title'])}</h1>
<p class="sub">{esc(meta['schedule_kst'])} 발행 · {esc(meta['category'])} · {esc(meta['format'])}</p>
<div class="notes">{esc(meta.get('notes',''))}<br>{esc(meta.get('sources_checked',''))}</div>
<div class="badges">{badge_html}</div>
<div class="card"><h2>① 글 정보 (Rank Math · 발행 설정)</h2>{meta_rows}</div>
<div class="card"><h2>② 본문</h2>
<button class="copy big" data-rich="bodyhtml">본문 복사 · 서식 유지 (블록 편집기에 그대로 붙여넣기)</button>
<button class="copy big" data-src="bodyhtml">HTML 코드 복사 (코드 편집기용)</button>
<p class="hint">이미지 자리는 복사되지 않아요. 아래 ③ 이미지 위치를 보고 직접 넣어주세요. 이탤릭 없음.</p>
<script type="text/plain" id="bodyhtml">{clean.replace('</script', '<\\/script')}</script></div>
<div class="card"><h2>③ 이미지 가이드 (Title과 ALT에 같은 문구 입력)</h2>{''.join(imgs)}</div>
<div class="card check"><h2>④ 발행 체크리스트</h2>{check_html}</div>
<h2 style="font-size:15px;color:var(--muted)">미리보기</h2>
<div class="preview"><h1 style="font-size:24px">{esc(meta['title'])}</h1>{preview}</div>
</div><script>{JS}</script></body></html>"""
    (OUT / f"{meta['date']}.html").write_text(page, encoding="utf-8")
    return meta, words


def build_index(items):
    lis = "".join(
        f'<li><a href="{esc(m["date"])}.html">{esc(m["date"])} · {esc(m["title"])}</a>'
        f'<span class="n">{esc(m["category"])} · {esc(m["format"])} · {w:,} words</span></li>'
        for m, w in sorted(items, key=lambda x: x[0]["date"], reverse=True))
    page = f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Vital Food Lab 발행 원고</title><style>{CSS}</style></head><body><div class="wrap">
{HUBNAV}
<h1>Vital Food Lab 예약 발행 원고</h1>
<p class="sub">하루 1개 · 12:00 UTC (한국 21:00) · 날짜를 눌러 원고를 열고 복사해서 워드프레스에 붙여넣으세요.</p>
<ul class="list">{lis}</ul></div></body></html>"""
    (OUT / "index.html").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    items = [build_post(json.loads(p.read_text(encoding="utf-8"))) for p in sorted(POSTS.glob("*.json"))]
    build_index(items)
    for m, w in items:
        print(m["date"], m["slug"], w, "words")
