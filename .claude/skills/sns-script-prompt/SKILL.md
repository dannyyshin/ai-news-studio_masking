---
name: sns-script-prompt
description: 01_news_brief.md를 바탕으로 @your_instagram_id 톤 A 인스타그램 캡션과 Gemini 3:4 한글 포함 인스타툰/카드뉴스 프롬프트를 작성해 02_content.md로 저장하는 스킬. "/sns-script-prompt", "인스타 원고 써줘" 요청에 사용.
allowed-tools: Read, Write, Glob
---

# SNS 원고 & Gemini 프롬프트 작성 (`/sns-script-prompt`)

## 입력 & 출력
- 입력: `outputs/<슬러그>/00_input.md`, `outputs/<슬러그>/01_news_brief.md` (+ 재작성 시 `03_qc_report.md`)
- 출력: `outputs/<슬러그>/02_content.md` (`template.md` 양식)

## 1단계: 포맷별 스타일 가이드 & 6종 레이아웃 로드
`00_input.md`의 포맷을 확인하고 아래 가이드를 반드시 읽는다:
- **공통 필수**: `references/layout-library.md` (6종 레이아웃 `L1~L6` 라우팅 표 및 다양성 규칙)
- `cardnews` (기본값, 5~6장): `references/style-cardnews.md`
- `webtoon` (고밀도 1컷 인스타툰): `references/style-webtoon.md` (직전 발행 레이아웃 중복 회피를 위해 `dedup_store.py last-layout` 확인)
- `both` (둘 다): 두 가이드를 모두 읽어 `card_01~06` + `webtoon_01`로 분리 작성

## 2단계: @your_instagram_id 톤 A 원고 작성 규칙
- **첫 줄 훅**: 스크롤을 멈추는 한 줄 (예: `"오늘 AI 업계 난리 난 이유 30초 정리 👇"`)
- **쉬운 비유**: 전문 용어는 일상 비유로 바로 풀어준다.
- **팩트 고정**: `01_news_brief.md`에 없는 버전명·수치·요금·날짜는 절대 쓰지 않는다.
- **분량**: 캡션 전체 2,200자 이내, 해시태그 5~12개.

## 3단계: Gemini 다중 레이아웃 한글 프롬프트 규칙
1. **레이아웃 다양성 강제 (`L1~L6`)**:
   - 모든 컷에 `- 레이아웃: L1|L2|L3|L4|L5|L6`를 반드시 명시한다.
   - `cardnews`는 **서로 다른 레이아웃 3종 이상**을 조합하고, **연속된 두 컷에 같은 레이아웃 사용을 금지**한다.
2. **비율·여백 고정**: `3:4 vertical`, `8% outer safe margin`을 모든 컷에 포함한다.
3. **컨테이너 분산 & 줄바꿈 강제**:
   - **컷당 제목 `14자 이하`, 부제 `24자 이하`**, 레이아웃에 맞는 정보 컨테이너(`메모지 1/2`, `비교표`, `스텝`, `지시선`, `체크리스트`, `텍스트 블록 1~3` — 각 3~4줄, 줄당 `14자 이하`, `/` 또는 `\n`로 줄 구분)로 정보를 분산한다.
   - 모든 정보 카드·종이 소품은 `SOLID PURE WHITE interiors (NO notebook lines)`로 지정해 한글 깨짐을 방지한다.
4. **재작성 시**: 기존 `02_content.md`를 `02_content_v1.md`로 백업한 뒤 수정한다.
