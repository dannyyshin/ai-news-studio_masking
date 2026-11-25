# 인스타그램(@your_instagram_id) 원고 & 이미지 프롬프트 (`02_content.md`)

- 프로젝트: 20261125-claude-orchestration
- 포맷: cardnews
- 브랜드 톤: A (친근하고 위트 있는 AI 큐레이터)
- 기반 뉴스: `01_news_brief.md` (발행일: 2026-11-24)

## 1. 인스타그램 게시 캡션
```text
오늘 AI 업계 난리 난 이유 30초 정리 👇

맨날 똑같은 프롬프트 복붙하던 시절, 진짜 끝났습니다.
클로드 코드가 아예 '업무 매뉴얼 + 검수팀 + 안전잠금'을 폴더 하나에 묶는 구조를 공개했거든요!

비유하자면 똑똑한 인턴 1명한테 다 시키는 게 아니라,
1) 자료 찾는 리서처
2) 원고 쓰는 작가
3) 팩트체크만 하는 깐깐한 데스크
이렇게 역할 나눠서 굴리는 팀을 폴더째 복제하는 느낌이에요.

여러분 업무에서 가장 먼저 자동화하고 싶은 반복 작업은 뭔가요? 댓글로 남겨주세요 💬

#AI뉴스 #클로드 #업무자동화 #AI에이전트 #AI큐레이션 #일잘러
```

## 2. Gemini 이미지 프롬프트 (`3:4` · `이미지` · `Hydrogen`)

### [컷 1] `images/card_01.png`
- 레이아웃: L6
- 한글 제목: 프롬프트 복붙 끝!
- 한글 부제: AI 팀을 폴더로 만드는 법
- Gemini 입력 프롬프트:
```text
Create a 3:4 vertical authentic Korean Instatoon cover poster (Layout L6). Clean warm off-white background (#FFFDF5), hand-drawn black ink outlines, keep a generous 8% empty safe margin on all edges. Render crisp bold Korean sans-serif typography with exact spelling: Top headline "프롬프트 복붙 끝!", bottom subtitle "AI 팀을 폴더로 만드는 법".
```

### [컷 2] `images/card_02.png`
- 레이아웃: L3
- 한글 제목: 혼자 일하면 생기는 일
- 한글 부제: 대충 넘어가고 실수도 해요
- Gemini 입력 프롬프트:
```text
Create a 3:4 vertical authentic Korean Instatoon Before/After 2-tier card (Layout L3). Clean warm off-white background (#FFFDF5), hand-drawn black ink outlines, keep a generous 8% empty safe margin on all edges. Render crisp bold Korean sans-serif typography with exact spelling: Top headline "혼자 일하면 생기는 일", bottom subtitle "대충 넘어가고 실수도 해요".
```

### [컷 3] `images/card_03.png`
- 레이아웃: L4
- 한글 제목: 핵심 1. 스킬 매뉴얼
- 한글 부제: 자주 쓰는 절차를 파일로 저장
- Gemini 입력 프롬프트:
```text
Create a 3:4 vertical authentic Korean Instatoon 3-step flow card (Layout L4). Clean warm off-white background (#FFFDF5), hand-drawn black ink outlines, keep a generous 8% empty safe margin on all edges. Render crisp bold Korean sans-serif typography with exact spelling: Top headline "핵심 1. 스킬 매뉴얼", bottom subtitle "자주 쓰는 절차를 파일로 저장".
```

### [컷 4] `images/card_04.png`
- 레이아웃: L2
- 한글 제목: 핵심 2. 독립 검수팀
- 한글 부제: 쓴 사람 모르게 팩트만 체크!
- Gemini 입력 프롬프트:
```text
Create a 3:4 vertical authentic Korean Instatoon VS comparison board (Layout L2). Clean warm off-white background (#FFFDF5), hand-drawn black ink outlines, keep a generous 8% empty safe margin on all edges. Render crisp bold Korean sans-serif typography with exact spelling: Top headline "핵심 2. 독립 검수팀", bottom subtitle "쓴 사람 모르게 팩트만 체크!".
```

### [컷 5] `images/card_05.png`
- 레이아웃: L1
- 한글 제목: 핵심 3. 훅 안전장치
- 한글 부제: 내 허락 없인 절대 발행 금지
- Gemini 입력 프롬프트:
```text
Create a 3:4 vertical authentic Korean Instatoon character desk notes card (Layout L1). Clean warm off-white background (#FFFDF5), hand-drawn black ink outlines, keep a generous 8% empty safe margin on all edges. Render crisp bold Korean sans-serif typography with exact spelling: Top headline "핵심 3. 훅 안전장치", bottom subtitle "내 허락 없인 절대 발행 금지".
```

## 3. 팩트 근거 매핑
| 원고/슬라이드 핵심 주장 | `01_news_brief.md` 근거 ID |
|---|---|
| 폴더 단위 스킬·서브에이전트 공유 | F1 |
| 훅 기반 실행 전 차단 | F2 |
