# 인스타그램(@your_instagram_id) 원고 & 이미지 프롬프트 (`02_content.md`)

- 프로젝트: 20261125-sample-instatoon-b
- 포맷: webtoon
- 브랜드 톤: A (친근하고 위트 있는 AI 큐레이터)
- 기반 뉴스: `01_news_brief.md` (발행일: 2026-11-24)

## 1. 인스타그램 게시 캡션
```text
오늘 AI 업계 난리 난 이유 30초 정리 👇

클로드가 만들어준 아티팩트를 이제 내 PC 앱으로 바로 설치할 수 있어요!
채팅방 스크롤 지옥 없이 바탕화면에서 바로 실행하는 시대가 열렸습니다.

여러분은 어떤 미니 앱을 제일 먼저 깔아두고 싶나요? 💬

#AI뉴스 #클로드 #아티팩트 #업무자동화 #AI큐레이션
```

## 2. Gemini 이미지 프롬프트 (`3:4` · `이미지` · `Hydrogen`)

### [컷 1] `images/webtoon_01.png`
- 레이아웃: L1
- 한글 제목: 아티팩트 앱 설치!
- 한글 부제: Mac · Windows 데스크톱 베타
- 메모지 1: 클로드가 만든 / 내 업무 도구를 / 바탕화면 앱으로!
- 메모지 2: 브라우저 안 켜도 / 전용 창과 아이콘 / 일반 앱처럼 실행
- 체크리스트: ☑ Mac·Win 지원 / ☑ 독 아이콘 고정 / ☑ OS 기능 연동 / 내 전용 앱 뚝딱!
- Gemini 입력 프롬프트:
```text
Create a single full-frame 3:4 vertical authentic Korean Instatoon info-poster (NOT a 4-panel grid), inspired by cute Korean Instatoon book-cover design. Slightly rough hand-drawn black ink outlines, clean warm off-white background (#FFFDF5), flat pastel accents, strict 8% outer safe margin.
1. TOP ZONE (22%): Yellow tag "11/24 Claude", white pill "스크롤 지옥 끝!", coral-red title "아티팩트 앱 설치!", black sub-caption "Mac · Windows 데스크톱 베타".
2. MIDDLE ZONE (36%): Cute chubby round white bear mascot wearing a small dark-teal beret behind a laptop on a warm yellow desk. Badge: "바탕화면에 쏙!".
3. BOTTOM DESK ZONE (42%): Three black-bordered papers with SOLID PURE WHITE interiors (NO notebook lines):
- Left paperclip paper: "클로드가 만든\n내 업무 도구를\n바탕화면 앱으로!"
- Center binder-clip paper: "브라우저 안 켜도\n전용 창과 아이콘\n일반 앱처럼 실행"
- Right paw-held checklist: "☑ Mac·Win 지원\n☑ 독 아이콘 고정\n☑ OS 기능 연동\n내 전용 앱 뚝딱!"
- Footer: "@your_instagram_id"
```

## 3. 팩트 근거 매핑
| 원고/슬라이드 핵심 주장 | `01_news_brief.md` 근거 ID |
|---|---|
| 폴더 단위 스킬·서브에이전트 및 데스크톱 앱 실행 | F1 |
| 전용 창·아이콘 및 OS 상호작용 | F2 |
