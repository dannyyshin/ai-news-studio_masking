# 스타일 가이드 ②: 1컷 인포-인스타툰 (3:4 세로형, 동적 레이아웃 선택)

단일 1장면(`images/webtoon_01.png`) 안에 시그니처 마스코트와 뉴스 성격에 맞는 시각 구도를 배치해, **인스타툰의 친근함 + 100~130자 수준의 구체적 뉴스 정보**를 동시에 담아내는 `@your_instagram_id`의 표준 웹툰 스타일이다.

> **레이아웃 선택 규칙**: 매번 `L1(캐릭터 노트)`만 쓰지 않고 `references/layout-library.md`의 `L1~L6` 중 뉴스 유형에 가장 어울리는 레이아웃을 고른다. 작성 전 `dedup_store.py last-layout`으로 직전 발행 레이아웃을 조회해 연속 중복을 피한다. (아래는 종합 스펙 요약형 기본 `L1` 예시)

## 1. 3단 레이아웃 설계 (3:4 세로 비율)
1. **상단 22% (헤더 — WHAT)**:
   - 좌상단 노란 말풍선 태그(`11/24 Claude` 등 날짜·기업) + 흰색 캡슐 훅
   - 대형 굵은 코랄 레드 타이틀 (`14자 이하`) + 아래 한 줄 부제 (`24자 이하`)
2. **중단 36% (시그니처 마스코트 — 감정/반응)**:
   - 고정 마스코트: 작은 다크틸 베레모와 동그란 눈을 가진 통통한 흰 곰 캐릭터(`cute chubby round white bear mascot wearing a small dark-teal beret and tiny round eyes`)
   - 따뜻한 노란 나무 책상 뒤 노트북 앞에서 신나게 반응하며, 옆에 작은 명찰 말풍선(`12자 이하`) 1개 배치
3. **하단 책상 42% (정보 소품 3종 — 구체적 뉴스·수치)**:
   - **메모지 1** (은색 클립 꽂힌 종이): 구체 변화/핵심 팩트 3줄 (`줄당 14자 이하`)
   - **메모지 2** (빨간 집게 꽂힌 종이): 핵심 수치/스펙 비교 3줄 (`줄당 14자 이하`)
   - **체크리스트** (흰 곰 손이 들어 올린 반짝이 종이): `☑` 항목 3~4줄 (`줄당 14자 이하`)
   - 좌하단 작은 브랜드 태그: `@your_instagram_id`

## 2. 한글 선명도 & 잘림 방지 필수 규칙
- **배경 비우기**: 방 가구·책장·복잡한 배경 금지. 깨끗한 미색 배경(`#FFFDF5`)과 손그림 먹선 외곽선 사용.
- **순백 메모지 고정**: 모든 종이 소품 내부는 가로 줄무늬 없이 순백(`SOLID PURE WHITE interiors, NO notebook lines`)으로 그려 작은 한글 획이 뭉개지지 않게 한다.
- **줄바꿈 직접 명시**: 프롬프트 안의 한국어 텍스트는 어절 단위(`7~10자`마다 `\n`)로 줄바꿈을 직접 써준다.
- **안전 여백**: 네 모서리 `8%` 안전 여백(`strict 8% outer safe margin on all four edges`)을 반드시 포함한다.

## 3. 프롬프트 템플릿
> Create a single full-frame 3:4 vertical authentic Korean Instatoon info-poster (NOT a 4-panel grid), inspired by cute Korean Instatoon book-cover design.
> [Art Style] Slightly rough hand-drawn black ink outlines, clean warm off-white background (#FFFDF5), flat pastel accents (coral red, warm yellow desk, sky blue), zero cluttered background room. Keep a strict 8% outer safe margin on all four edges so NO text or paper edge is clipped.
> [Layout — 3 Vertical Zones]
> 1. TOP ZONE (22% height): Small yellow speech-bubble tag "{기업날짜}", white pill "{상단캡슐}", large playful bold coral-red Korean title "{제목}", black sub-caption "{부제}".
> 2. MIDDLE ZONE (36% height): Cute chubby round white bear mascot wearing a small dark-teal beret and tiny round eyes sitting behind a laptop on a warm yellow wooden desk, holding a pen. Tiny neat badge beside bear: "{배지}".
> 3. BOTTOM DESK ZONE (42% height): Three crisp black-bordered papers with SOLID PURE WHITE interiors (NO notebook lines):
> - Left paper with silver paperclip: "{메모1}"
> - Center paper with red binder clip: "{메모2}"
> - Right slanted checklist held by a cute white paw with sparkles: "{체크리스트}"
> - Bottom-left small brand tag: "@your_instagram_id"
> [Typography] Ultra-crisp bold black Korean gothic typography, exact Korean spelling and exact numbers, zero duplicated syllables, zero extra gibberish text.
