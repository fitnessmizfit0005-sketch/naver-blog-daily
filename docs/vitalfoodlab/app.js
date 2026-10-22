/* 애드센스(Vital Food Lab) 원고 뷰어: posts/<날짜>.md 를 읽어서 복사용 화면을 만든다. */
var REPO = 'fitnessmizfit0005-sketch/naver-blog-daily';
var POSTS_DIR = 'docs/vitalfoodlab/posts';

function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}

function parsePost(txt){
  txt = txt.replace(/\r\n/g,'\n').replace(/^﻿/,'');
  var m = txt.match(/^\s*---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if(!m) throw new Error('맨 위에 --- 로 감싼 글 정보가 없어요.');
  var meta = {};
  m[1].split('\n').forEach(function(l){var i=l.indexOf(':');if(i>0)meta[l.slice(0,i).trim()]=l.slice(i+1).trim()});
  var rest = m[2], imgs = [], body = rest;
  var k = rest.indexOf('=== IMAGES ===');
  if(k>=0){body = rest.slice(0,k); imgs = parseImages(rest.slice(k+14));}
  meta.body = body.trim(); meta.images = imgs;
  meta.tags = (meta.tags||'').split(',').map(function(t){return t.trim()}).filter(Boolean);
  return meta;
}
function parseImages(t){
  var out=[], cur=null;
  t.split('\n').forEach(function(l){
    var s=l.trim(); if(!s){return}
    var mm=s.match(/^(Prompt|Filename|ALT(?:\s*\/\s*Title)?|Title)\s*:\s*(.*)$/i);
    if(mm && cur){var key=mm[1].toLowerCase().indexOf('prompt')===0?'prompt':mm[1].toLowerCase().indexOf('file')===0?'filename':'alt'; cur[key]=(cur[key]?cur[key]+' ':'')+mm[2];}
    else if(/^Image\s*\d/i.test(s)){cur={label:s,prompt:'',filename:'',alt:''};out.push(cur)}
    else if(cur){var last=cur.alt?'alt':cur.filename?'filename':'prompt';cur[last]+=' '+s}
  });
  return out;
}

function words(html){var d=document.createElement('div');d.innerHTML=html;return (d.textContent||'').split(/\s+/).filter(Boolean).length}
function checks(p){
  var b=p.body, kw=(p.focus_keyword||'').toLowerCase(), plain=b.replace(/<[^>]+>/g,' ');
  var ps=(b.split(/<h2/i)[0].match(/<p[^>]*>[\s\S]*?<\/p>/gi)||[]).slice(0,2).join(' ').toLowerCase();
  var w=words(b), md=(p.meta_description||'').length;
  var internal=(b.match(/href="https:\/\/vitalfoodlab\.com\//g)||[]).length;
  var src=(b.match(/pubmed\.ncbi\.nlm\.nih\.gov\/\d+/g)||[]).length;
  return [
    ['단어 '+w.toLocaleString(), w>=800],
    ['메타 설명 '+md+'자', md>=120&&md<=160],
    ['키워드: 제목', kw&&(p.title||'').toLowerCase().indexOf(kw)>=0],
    ['키워드: 메타', kw&&(p.meta_description||'').toLowerCase().indexOf(kw)>=0],
    ['키워드: 도입부', kw&&ps.indexOf(kw)>=0],
    ['링크 '+internal+'개 (내부1+관련3)', internal>=4],
    ['PubMed 출처 '+src+'개', src>=2],
    ['한국어 0자', !/[가-힣]/.test(plain)],
    ['Intro/Conclusion 헤딩 없음', !/<h2[^>]*>\s*(Introduction|Conclusion)\s*<\/h2>/i.test(b)],
    ['이미지 '+p.images.length+'장', p.images.length===3]
  ];
}

function row(k,v,mono){var id='f'+(row.n=(row.n||0)+1);return '<div class="row"><div class="k">'+esc(k)+'</div><div class="v'+(mono?' mono':'')+'" id="'+id+'">'+esc(v)+'</div><button class="copy" data-src="'+id+'">복사</button></div>'}

function previewHtml(p){
  var h=p.body, ph=function(i){var im=p.images[i-1]||{};return '<div class="ph">🖼️ Image '+i+' 위치 · '+esc(im.filename||'')+'</div>'};
  // Image 1: 첫 H2 바로 앞
  h=h.replace(/<h2/i, ph(1)+'<h2');
  // Image 2: 라벨에 따옴표로 적힌 제목 앞, 없으면 가운데 H2 앞
  var lab=(p.images[1]||{}).label||'', q=lab.match(/["“]([^"”]+)["”]/), done=false;
  if(q){var re=new RegExp('<h2[^>]*>\\s*'+q[1].replace(/[.*+?^${}()|[\]\\]/g,'\\$&'),'i');if(re.test(h)){h=h.replace(re,function(x){return ph(2)+x});done=true}}
  if(!done){var hs=h.match(/<h2/gi)||[];var mid=Math.floor(hs.length/2),c=0;h=h.replace(/<h2/gi,function(x){c++;return c===mid+1?ph(2)+x:x})}
  // Image 3: FAQ 성격 H2 앞
  var re3=/<h2[^>]*>[^<]*Questions[^<]*<\/h2>/i;
  if(re3.test(h)) h=h.replace(re3,function(x){return ph(3)+x}); else h=h.replace(/<h2[^>]*>\s*Related Articles/i,function(x){return ph(3)+x});
  return h;
}

function renderPost(p, date){
  var b=checks(p).map(function(c){return '<span class="badge'+(c[1]?'':' warn')+'">'+(c[1]?'✓ ':'! ')+esc(c[0])+'</span>'}).join('');
  row.n=0;
  var meta=[row('제목',p.title),row('Slug',p.slug,1),row('Focus Keyword',p.focus_keyword),row('Meta Description',p.meta_description),row('카테고리',p.category),row('태그',p.tags.join(', ')),row('예약 (UTC)',p.schedule_utc,1)].join('');
  var imgs=p.images.map(function(im){return '<div class="img"><b>'+esc(im.label)+'</b>'+row('Prompt',im.prompt)+row('Filename',im.filename,1)+row('ALT · Title',im.alt)+'</div>'}).join('');
  var list=['제목 입력','Slug: '+p.slug,'카테고리: '+p.category,'태그 입력','본문 붙여넣기 → H2/H3·표·링크 확인','Image 1 삽입 + ALT·Title','Image 2 삽입 + ALT·Title','Image 3 삽입 + ALT·Title','Featured Image = Image 1','Rank Math Focus Keyword: '+p.focus_keyword,'Rank Math Meta Description','예약 발행: '+p.schedule_utc+' UTC ('+(p.schedule_kst||'')+')','미리보기로 링크·표 확인 후 예약'];
  var edit='https://github.com/'+REPO+'/edit/main/'+POSTS_DIR+'/'+date+'.md';
  document.title=date+' · '+(p.title||'');
  document.getElementById('app').innerHTML=
   '<h1>'+esc(p.title)+'</h1><p class="sub">'+esc(p.schedule_kst||p.schedule_utc)+' 발행 · '+esc(p.category)+' · '+esc(p.format||'')+' · <a href="'+edit+'" target="_blank" rel="noopener">원고 파일 고치기</a></p>'+
   (p.notes?'<div class="notes">'+esc(p.notes)+'</div>':'')+
   '<div class="badges">'+b+'</div>'+
   '<div class="card"><h2>① 글 정보 (Rank Math · 발행 설정)</h2>'+meta+'</div>'+
   '<div class="card"><h2>② 본문</h2><button class="copy big" data-rich="1">본문 복사 · 서식 유지 (블록 편집기에 그대로 붙여넣기)</button><button class="copy big" data-html="1">HTML 코드 복사 (코드 편집기용)</button><p class="hint">이미지는 복사되지 않아요. ③을 보고 직접 넣어주세요.</p></div>'+
   '<div class="card"><h2>③ 이미지 가이드 (Title과 ALT에 같은 문구)</h2>'+(imgs||'<p class="err">이미지 정보가 없어요.</p>')+'</div>'+
   '<div class="card check"><h2>④ 발행 체크리스트</h2>'+list.map(function(c){return '<label><input type="checkbox"> '+esc(c)+'</label>'}).join('')+'</div>'+
   '<h2 style="font-size:15px;color:var(--muted)">미리보기</h2><div class="preview"><h1 style="font-size:24px">'+esc(p.title)+'</h1>'+previewHtml(p)+'</div>';
  window.__body=p.body;
  var key='vfl-check-'+date, st={};try{st=JSON.parse(localStorage.getItem(key)||'{}')}catch(e){}
  document.querySelectorAll('.check input').forEach(function(c,i){c.checked=!!st[i];c.addEventListener('change',function(){st[i]=c.checked;try{localStorage.setItem(key,JSON.stringify(st))}catch(e){}})});
}

function flash(b){b.classList.add('done');var t=b.textContent;b.textContent='복사됨';setTimeout(function(){b.classList.remove('done');b.textContent=t},1400)}
function copyText(b,txt){(navigator.clipboard?navigator.clipboard.writeText(txt):Promise.reject()).then(function(){flash(b)},function(){var a=document.createElement('textarea');a.value=txt;document.body.appendChild(a);a.select();document.execCommand('copy');a.remove();flash(b)})}
function copyRich(b,h){var d=document.createElement('div');d.innerHTML=h;var plain=d.innerText;
  try{navigator.clipboard.write([new ClipboardItem({'text/html':new Blob([h],{type:'text/html'}),'text/plain':new Blob([plain],{type:'text/plain'})})]).then(function(){flash(b)},function(){fb()})}catch(e){fb()}
  function fb(){var x=document.createElement('div');x.contentEditable=true;x.innerHTML=h;x.style.position='fixed';x.style.left='-9999px';document.body.appendChild(x);var r=document.createRange();r.selectNodeContents(x);var s=getSelection();s.removeAllRanges();s.addRange(r);document.execCommand('copy');s.removeAllRanges();x.remove();flash(b)}}
document.addEventListener('click',function(e){var b=e.target.closest('button.copy');if(!b)return;
  if(b.dataset.src){copyText(b,document.getElementById(b.dataset.src).textContent)}
  else if(b.dataset.html){copyText(b,window.__body)}
  else if(b.dataset.rich){copyRich(b,window.__body)}});

function fetchPost(date){return fetch('posts/'+date+'.md?t='+Date.now(),{cache:'no-store'}).then(function(r){if(!r.ok)throw new Error(date+'.md 파일을 못 찾았어요. (올린 직후라면 1~2분 뒤 새로고침)');return r.text()})}

function initPost(){
  var date=new URLSearchParams(location.search).get('d')||'';
  if(!/^\d{4}-\d{2}-\d{2}$/.test(date)){document.getElementById('app').innerHTML='<p class="err">주소에 날짜(?d=2026-10-23)가 없어요.</p>';return}
  fetchPost(date).then(function(t){renderPost(parsePost(t),date)}).catch(function(e){document.getElementById('app').innerHTML='<p class="err">'+esc(e.message)+'</p><p><a href="index.html">목록으로</a></p>'});
}

function initIndex(){
  var el=document.getElementById('list');
  fetch('https://api.github.com/repos/'+REPO+'/contents/'+POSTS_DIR+'?ref=main',{cache:'no-store'}).then(function(r){if(!r.ok)throw new Error('목록을 불러오지 못했어요 ('+r.status+')');return r.json()})
  .then(function(files){
    var dates=files.map(function(f){return f.name}).filter(function(n){return /^\d{4}-\d{2}-\d{2}\.md$/.test(n)}).map(function(n){return n.slice(0,10)}).sort().reverse();
    if(!dates.length){el.innerHTML='<li>아직 원고가 없어요.</li>';return}
    el.innerHTML=dates.map(function(d){return '<li id="d'+d+'"><a href="post.html?d='+d+'">'+d+'</a><span class="n">불러오는 중…</span></li>'}).join('');
    dates.forEach(function(d){fetchPost(d).then(function(t){var p=parsePost(t);var li=document.getElementById('d'+d);li.querySelector('a').textContent=d+' · '+p.title;li.querySelector('.n').textContent=(p.category||'')+' · '+(p.format||'')+' · '+words(p.body).toLocaleString()+' words'}).catch(function(){var li=document.getElementById('d'+d);li.querySelector('.n').textContent='페이지 반영 대기 중 (1~2분 뒤 새로고침)'})});
  }).catch(function(e){el.innerHTML='<li class="err">'+esc(e.message)+'</li>'});
  var inp=document.getElementById('newdate');
  var t=new Date(Date.now()+9*3600e3);inp.value=t.toISOString().slice(0,10);
  document.getElementById('newbtn').addEventListener('click',function(){
    var d=inp.value;if(!/^\d{4}-\d{2}-\d{2}$/.test(d))return;
    window.open('https://github.com/'+REPO+'/new/main/'+POSTS_DIR+'?filename='+d+'.md','_blank','noopener');
  });
}
