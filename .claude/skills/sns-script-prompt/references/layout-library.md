# 6종 동적 레이아웃 라이브러리 (`L1`~`L6`)

`@your_instagram_id`의 모든 이미지는 **브랜드 정체성(고정 4요소)**은 유지하되, **시각 구도(`L1`~`L6`)**는 리서치 뉴스 성격과 슬라이드 역할에 따라 동적으로 선택한다. 매번 똑같은 책상 메모장 구도만 반복되는 단조로움을 구조적으로 방지한다.

## 1. 브랜드 고정 4요소 (전 레이아웃 공통)
- **마스코트**: 작은 다크틸 베레모와 동그란 눈을 가진 통통한 흰 곰 (`cute chubby round white bear mascot wearing a small dark-teal beret and tiny round eyes`)
- **화풍·배경**: 손그림 먹선 외곽선 (`slightly rough hand-drawn black ink outlines`), 깨끗한 미색 배경 (`#FFFDF5`), 방 가구·복잡한 배경 패턴 금지
- **정보 컨테이너**: 검은 테두리 + 순백 내부 (`SOLID PURE WHITE interiors, NO notebook lines`)로 한글 선명도 보장
- **안전 여백·태그**: `3:4 vertical`, `strict 8% outer safe margin on all four edges`, 좌하단 `@your_instagram_id`

## 2. 6종 레이아웃 라우팅 표 (뉴스 유형·슬라이드 역할별)
| 코드 | 레이아웃 이름 | 핵심 시각 구도 | 적합한 뉴스/슬라이드 유형 |
|---|---|---|---|
| **L1** | 캐릭터 노트 | 책상 위 클립 메모지 2장 + 체크리스트 1장 | 종합 스펙 요약, 1컷 포스터, 마무리 요약 |
| **L2** | VS 비교·차트 보드 | 좌(기존/타사) vs 우(신규) 2열 비교표 + 상승 화살표/막대 그래프 + 깜짝 놀란 곰 | 벤치마크·속도·가격·모델 비교 |
| **L3** | Before / After 2단 컷 | 상단(회색빛 불편·멘붕 곰) vs 하단(밝은 해결 곰 + 효과 칩 2개) | 불편 해소, 작업 시간 단축, 워크플로 혁신 |
| **L4** | 3단계 스텝 흐름 | `STEP 1 → STEP 2 → STEP 3` 화살표 연결 카드 + 지시봉 든 곰 | 사용법, 설치 방법, 실무 적용·자동화 절차 |
| **L5** | 대형 UI 화면 + 지시선 | 중앙 스마트폰/노트북 목업 화면 + 돋보기·화살표 지시선 2~3개 + 가리키는 곰 | 앱/웹 UI 개편, 신규 메뉴·버튼 출시 |
| **L6** | 대형 훅 + 리액션 컷 | 순백 여백 + 대형 볼드 코랄/네이비 훅 + 빼꼼/환호 곰 + 집중선 | 1장 표지(시선 강탈), 마지막 저장/댓글 CTA |

## 3. 다양성 강제 규칙 (`validate_contract.py` 코드 검증 대상)
1. **카드뉴스 (`cardnews` 5~6장)**:
   - 모든 컷에 `- 레이아웃: L1|L2|L3|L4|L5|L6`를 반드시 명시한다.
   - 한 게시물 내 **서로 다른 레이아웃 최소 3종 이상**을 사용한다 (`distinct >= 3`).
   - **연속된 두 컷에 동일한 레이아웃 배치 금지** (`cut[i] != cut[i-1]`).
   - 권장 5장 조합 예시:
     - **모델 출시/성능 발표**: `L6(표지) → L3(불편 해소) → L2(벤치마크 비교) → L5(UI 변화) → L1(핵심 체크리스트)`
     - **신기능/사용법 안내**: `L6(표지) → L5(신규 화면) → L4(3단계 사용법) → L3(전후 비교) → L1(저장 요약)`
     - **정책/요금/업데이트**: `L6(표지) → L2(요금·스펙 비교) → L4(적용 절차) → L1(체크리스트) → L6(CTA)`
2. **1컷 웹툰 (`webtoon` 1장)**:
   - 작성 전 `dedup_store.py last-layout`으로 직전 발행 레이아웃을 확인하고, 뉴스 성격에 맞는 **다른 레이아웃**을 우선 선택한다.

## 4. 레이아웃별 영문 프롬프트 골격

### `L1` — 캐릭터 노트 (메모지 2 + 체크리스트 1)
> Create a single full-frame 3:4 vertical authentic Korean Instatoon info-poster (Layout L1: Character Desk Notes). Slightly rough hand-drawn black ink outlines, clean warm off-white background (#FFFDF5), flat pastel accents, strict 8% outer safe margin.
> 1. TOP ZONE (22%): Yellow tag "{태그}", white pill "{캡슐}", bold coral-red title "{제목}", black sub-caption "{부제}".
> 2. MIDDLE ZONE (36%): Cute chubby round white bear mascot wearing a small dark-teal beret behind a laptop on a warm yellow wooden desk. Small badge: "{배지}".
> 3. BOTTOM ZONE (42%): Three black-bordered papers with SOLID PURE WHITE interiors (NO notebook lines): left paperclip note "{메모1}", center binder-clip note "{메모2}", right paw-held checklist "{체크리스트}". Footer "@your_instagram_id".

### `L2` — VS 비교·차트 보드 (좌우 비교 + 막대 그래프)
> Create a single full-frame 3:4 vertical authentic Korean Instatoon comparison board (Layout L2: VS Chart Board). Slightly rough hand-drawn black ink outlines, clean warm off-white background (#FFFDF5), strict 8% outer safe margin.
> 1. TOP ZONE (22%): Bold coral-red title "{제목}", crisp black subtitle "{부제}".
> 2. MIDDLE ZONE (54%): Two side-by-side black-bordered SOLID PURE WHITE comparison cards (NO notebook lines) separated by a bright yellow "VS" badge — Left muted-gray header card "{비교 좌}", Right sky-blue/coral highlight card "{비교 우}" with simple upward bar chart arrow.
> 3. BOTTOM ZONE (24%): Cute chubby round white bear mascot wearing a small dark-teal beret gasping in amazement while pointing at the winning right card, holding a small white summary pill "{요약}". Footer "@your_instagram_id".

### `L3` — Before / After 2단 컷 (상단 불편 → 하단 해결)
> Create a single full-frame 3:4 vertical authentic Korean Instatoon 2-tier transformation card (Layout L3: Before & After). Slightly rough hand-drawn black ink outlines, clean warm off-white background (#FFFDF5), strict 8% outer safe margin.
> 1. TOP HEADER (18%): Bold coral-red title "{제목}", black subtitle "{부제}".
> 2. UPPER PANEL — BEFORE (36%): Soft muted-gray box with SOLID PURE WHITE inner card (NO notebook lines), small gray badge "BEFORE", dizzy stressed white bear mascot wearing a small dark-teal beret tangled in icons, text "{이전 상태}".
> 3. LOWER PANEL — AFTER (46%): Bright pastel-yellow/mint box with SOLID PURE WHITE inner card (NO notebook lines), coral badge "AFTER", happy sparkling white bear mascot giving thumbs-up, text "{이후 변화}" plus 2 neat white benefit pills. Footer "@your_instagram_id".

### `L4` — 3단계 스텝 흐름 (`STEP 1 → 2 → 3`)
> Create a single full-frame 3:4 vertical authentic Korean Instatoon step-by-step guide (Layout L4: 3-Step Flow). Slightly rough hand-drawn black ink outlines, clean warm off-white background (#FFFDF5), strict 8% outer safe margin.
> 1. TOP HEADER (20%): Bold coral-red title "{제목}", black subtitle "{부제}".
> 2. MIDDLE FLOW (58%): Three vertically stacked black-bordered SOLID PURE WHITE step cards (NO notebook lines) connected by bold coral downward arrows:
> - Coral badge "STEP 1": "{스텝1}"
> - Yellow badge "STEP 2": "{스텝2}"
> - Sky-blue badge "STEP 3": "{스텝3}"
> 3. BOTTOM ACCENT (22%): Cute chubby round white bear mascot wearing a small dark-teal beret holding a wooden pointer beside STEP 3 with a cheerful speech badge "{한줄팁}". Footer "@your_instagram_id".

### `L5` — 대형 UI 화면 + 지시선 컷 (기기 목업 + 콜아웃)
> Create a single full-frame 3:4 vertical authentic Korean Instatoon UI spotlight card (Layout L5: Device UI Callout). Slightly rough hand-drawn black ink outlines, clean warm off-white background (#FFFDF5), strict 8% outer safe margin.
> 1. TOP HEADER (20%): Bold coral-red title "{제목}", black subtitle "{부제}".
> 2. CENTER DEVICE (56%): Large clean hand-drawn smartphone or laptop mockup with simplified minimal UI screen, highlighted with 2~3 bold black-bordered SOLID PURE WHITE callout bubbles (NO notebook lines) connected by red arrows: "{지시선1}", "{지시선2}".
> 3. BOTTOM CORNER (24%): Cute chubby round white bear mascot wearing a small dark-teal beret peeking beside the device holding a magnifying glass. Footer "@your_instagram_id".

### `L6` — 대형 훅 + 리액션 컷 (표지 / 마지막 CTA)
> Create a single full-frame 3:4 vertical authentic Korean Instatoon cover/CTA poster (Layout L6: Hero Hook & Reaction). Slightly rough hand-drawn black ink outlines, clean warm off-white background (#FFFDF5), generous breathing whitespace, strict 8% outer safe margin.
> 1. TOP ZONE (45%): Small yellow news tag "{태그}", huge ultra-bold coral-red & navy Korean headline "{제목}", crisp black subtitle "{부제}" inside a neat SOLID PURE WHITE pill (NO notebook lines).
> 2. BOTTOM ZONE (55%): Large expressive cute chubby round white bear mascot wearing a small dark-teal beret peeking over a laptop or cheering with comic speed-lines and sparkles, plus a short speech bubble "{말풍선}". Footer "@your_instagram_id".
