# naver-blog-daily

네이버 다계정 블로그(진트쌤·모찌코치·오늘뭐지) 일일 발행 원고 검토용 탭 HTML.

- `docs/<날짜>.html` — 그날 발행분. 탭 하나 = 포스팅 하나.
  본문 복사 버튼(서식 없는 텍스트) · 글자수/키워드 체크 · 이미지 프롬프트 목록.
- `docs/index.html` — 날짜별 목록.
- 생성기: `ClaudeCode/.claude/skills/tab-html/generate.py` (`tab-html` 스킬)

공개 URL: https://fitnessmizfit0005-sketch.github.io/naver-blog-daily/

> 네이버 에디터 조작은 100% 수동. 이 페이지는 복붙용 참고 자료.

## 애드센스 (Vital Food Lab, 영문 워드프레스 블로그)

- 원고 파일: `docs/vitalfoodlab/posts/<날짜>.md` (맨 위 `---` 글 정보, 본문 HTML, `=== IMAGES ===` 이미지 3장)
- 페이지: `docs/vitalfoodlab/index.html` (목록 + 새 원고 올리기), `post.html?d=<날짜>` (복사 버튼·이미지 가이드·체크리스트·자동 점검)
- 빌드 과정 없음: 깃허브에 원고 파일만 저장하면 페이지가 그 파일을 읽어서 화면을 만든다.
- 공개 URL: https://fitnessmizfit0005-sketch.github.io/naver-blog-daily/vitalfoodlab/
