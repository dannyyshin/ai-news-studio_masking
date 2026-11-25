# 🤖 데일리 AI 인스타 카드뉴스 자동화 에이전트

Google(Gemini) · OpenAI(ChatGPT) · Anthropic(Claude) · xAI(Grok) 등 최신 AI 뉴스를 매일 수집해 **독립 팩트 QC → 6종 인스타툰 제작 → 인스타그램(`@your_instagram_id`) 발행 → 사후 컨펌**까지 자동 수행하는 **7-에이전트 × 7-스킬 오케스트레이션**입니다.

- **대상 계정**: `@your_instagram_id` (브랜드 톤 A: 친근·위트 AI 큐레이터)
- **기본 포맷**: `3:4` 세로형 인스타툰 카드뉴스 5~6장 (1컷 웹툰·둘 다 지원)
- **자동 스케줄**: 매일 오전 `11:00` (`Asia/Seoul`) 무인 예약 실행 지원

---

## 📁 폴더 구성

```text
ai-news-studio_masking/
├── CLAUDE.md              # 공통 팀 사규 & 데이터 계약
├── README.md              # 프로젝트 가이드
├── setup.sh               # 환경 점검 & SQLite 초기화
├── config/studio.json     # 계정·Gemini·레이아웃 설정
├── scripts/
│   └── run_daily_11am.sh  # 매일 11시 crontab 실행 스크립트
├── .claude/
│   ├── settings.json      # PreToolUse Hook 등록
│   ├── agents/            # 전담 에이전트 7종 (.md)
│   ├── hooks/             # guard_publish.py (물리 차단)
│   └── skills/            # 스킬 7종 + 스크립트 + 가이드
├── samples/               # 정상·오류 테스트 샘플 4종
├── tests/test_harness.py  # 오프라인 단위 테스트 6종
├── data/studio.db         # SQLite 중복 제거·발행 이력
└── outputs/<YYYYMMDD-슬러그>/  # 실행별 산출물 & 이미지
```

---

## 🔄 진행 순서

```text
[STEP 0] director
  포맷(카드뉴스/웹툰/둘다)·톤 확정 → 00_input.md
    ↓
[STEP 1] ai-researcher (Loop 1: 최대 2회)
  72h 공식 뉴스 수집 + 30일 중복 제거 → 01_news_brief.md
    ↓
[STEP 2~3] content-writer ⇄ fact-qc (Loop 2: 최대 2회)
  6종 레이아웃 원고·프롬프트 + 코드·웹 팩트 검수
  → 02_content.md, 03_qc_report.md
    ↓
[Gate 1] 사용자 원고·프롬프트 결재 → 04_gate1_content.md
    ↓
[STEP 5] image-producer (Loop 3: 컷당 최대 2회)
  Gemini 3:4 생성 + Read 시각 검수 → images/*.png
    ↓
[Gate 2] 최종 발행 결재 → 05_gate2_publish.md
  🔒 PreToolUse Hook (guard_publish.py 물리 잠금)
    ↓
[STEP 6] insta-publisher
  인스타 업로드·캡션 검증·공유 → 06_publish_result.md
    ↓
[STEP 7] publish-auditor
  실제 URL 새 탭 사후 컨펌 → 07_publish_confirm.md
```

---

## 🚀 사용방법

### 1) 초기 설정 & 단위 테스트
`config/studio.json`에서 계정명(`your_instagram_id`)과 Gemini 채팅 ID(`<YOUR_CHAT_ID>`)를 본인 값으로 바꾼 뒤 실행합니다.
```bash
cd ai-news-studio_masking
bash setup.sh
python3 -m unittest discover -s tests -v
```

### 2) 대화형 실행 (Claude Code)
프로젝트 폴더에서 `claude` 실행 후 슬래시 명령 입력:
- `/ai-news-studio` : STEP 0~7 전체 파이프라인 실행
- `/ai-news-collect` : 최신 뉴스 수집만 단독 실행
- `/sns-script-prompt` : 원고·프롬프트 작성만 단독 실행
- `/news-fact-qc` : 팩트·글자수·다양성 검수만 단독 실행
- `/gemini-image-gen` : Gemini 3:4 이미지 제작만 단독 실행
- `/insta-publish` : Gate 2 승인본 업로드만 단독 실행
- `/publish-confirm` : 실제 게시 URL 사후 컨펌만 단독 실행

### 3) 매일 오전 11시 무인 예약 (`Asia/Seoul`)
```bash
# crontab -e 등록 예시
CRON_TZ=Asia/Seoul
0 11 * * * /path/to/scripts/run_daily_11am.sh
```
- **무결점 조건**(`QC FAIL=0`, `MISMATCH=0`, `이미지 PASS`, `1일 1회`) 충족 시에만 `예약자동승인`으로 자동 게시하며, 이상 시 즉시 보류합니다.

---

## 💡 쉬운 예제 설명

처음 실행할 때 실제로 어떤 일이 벌어지는지 1분 흐름으로 살펴보면 다음과 같습니다.

### 1. 한 줄로 시작하기
```text
사용자: /ai-news-studio
에이전트: 포맷을 선택해 주세요 (1. 카드뉴스 5~6장 / 2. 1컷 웹툰 / 3. 둘 다)
사용자: 1번 (카드뉴스 5장)
```

### 2. AI 팀이 알아서 이어달리기 (자동 처리)
- **리서처(`ai-researcher`)**: OpenAI·Google·Anthropic 공식 블로그에서 최근 72시간 내 새 소식 1건(예: `신규 모델 출시`)을 찾고, 30일 내 올린 적 없는지 DB로 확인합니다.
- **작가(`content-writer`)**: 뉴스 성격에 맞춰 5장 구도를 자동 배정합니다.
  - 1장 `L6` 대형 훅 표지 → 2장 `L3` 전/후 비교 → 3장 `L2` 수치 비교 → 4장 `L5` UI 지시선 → 5장 `L1` 요약 체크리스트
- **팩트 검수(`fact-qc`)**: 지어낸 수치가 없는지, 제목 `14자`·부제 `24자` 이내인지, 연속 중복 구도는 없는지 코드와 웹으로 재검증합니다.

### 3. 사람은 딱 2번만 OK (이중 게이트)
- **Gate 1 (원고 확인)**: "이 캡션과 5장 기획안으로 이미지 만들까요?" → **승인**
- **이미지 제작(`image-producer`)**: Gemini에서 3:4 인스타툰 PNG 5장을 생성하고, 한글 깨짐이 없는지 직접 눈으로(`Read`) 검수합니다.
- **Gate 2 (발행 확인)**: 완성된 이미지 5장을 보고 "인스타에 올릴까요?" → **승인**

### 4. 자동 업로드 + 사후 컨펌까지 끝!
- **발행(`insta-publisher`)**: 인스타에 5장 업로드 → 원고 붙여넣기 → 글자수 카운터 확인 후 공유.
- **감사(`publish-auditor`)**: 방금 올라간 실제 게시물 링크를 새 탭으로 열어 **원고·해시태그·5장 슬라이드가 정상 노출**됐는지 확인하고 완료 보고합니다.

---

## 👥 에이전트 소개 (7종)

| 에이전트 | 핵심 역할 |
|---|---|
| **1. director** | STEP 0 조건 확정, 전체 흐름 지휘, Gate 1·2 결재 관리 |
| **2. ai-researcher** | 공식 1차 출처 72h 뉴스 수집 및 30일 중복 필터링 |
| **3. content-writer** | 톤 A 캡션 + 6종 레이아웃(`L1~L6`) 3:4 프롬프트 작성 |
| **4. fact-qc** | 독립 팩트·최신성·글자수·레이아웃 다양성 검수 |
| **5. image-producer** | Gemini 3:4 이미지 생성·추출 및 한글 깨짐 시각 검수 |
| **6. insta-publisher** | 인스타 업로드, 캡션 커밋(`N/2200`) 검증 및 공유 |
| **7. publish-auditor** | 실제 URL 새 탭 재검증, 원고·슬라이드 누락 시 경보 |

---

## 🧩 스킬 소개 (7종)

| 스킬 명령 | 핵심 기능 및 내장 리소스 |
|---|---|
| `/ai-news-studio` | 7단계 오케스트레이션, Gate 1·2 템플릿 |
| `/ai-news-collect` | `ai-sources.md`, `dedup_store.py` (SQLite 중복·레이아웃) |
| `/sns-script-prompt` | `layout-library.md`(`L1~L6`), 카드뉴스·웹툰 가이드 |
| `/news-fact-qc` | `validate_contract.py` (글자수·여백·다양성 코드 검증) |
| `/gemini-image-gen` | `gemini-ego-playbook.md` (`Hydrogen` 3:4 PNG 추출) |
| `/insta-publish` | `insta-ego-playbook.md` (Lexical 캡션 커밋·포인터 클릭) |
| `/publish-confirm` | `verify_published_payload.py` (사후 URL 감사·경보) |

---

## 📦 결과 파일 (`outputs/<YYYYMMDD-슬러그>/`)

| 파일명 | 생성 주체 & 내용 |
|---|---|
| `state.json` | 현재 단계, 포맷, 루프 횟수, 브라우저 세션 ID |
| `00_input.md` | STEP 0 확정 타깃·포맷·톤 조건 |
| `01_news_brief.md` | 72h 미발행 뉴스 요약 + 1차 출처 URL + 발행일 |
| `02_content.md` | 인스타 캡션 + 컷별 레이아웃·3:4 Gemini 프롬프트 |
| `03_qc_report.md` | 코드 검증 + 독립 웹 팩트체크 결과 |
| `04_gate1_content.md` | Gate 1 원고·프롬프트 결재 기록 |
| `images/*.png` | Gemini `896×1200` (`3:4`) 최종 PNG 이미지 |
| `05_image_qc.md` | 컷별 한글 깨짐·잘림 시각 검수 결과 |
| `05_gate2_publish.md` | Gate 2 최종 발행 결재 (Hook 잠금 대상) |
| `06_publish_result.md` | 게시 URL + 발행 완료 스크린샷 |
| `07_publish_confirm.md` | 실제 URL 사후 컨펌 판정 + 확인 스크린샷 |

---

## 🧠 하네스 지침과 기억

### 지침 계층 (Harness Instructions)
- **`CLAUDE.md` (35줄)**: 전 에이전트 공통 사규, 파일 계약, 이중 게이트, 절대 경로 규칙 고정.
- **권한 격리**: `content-writer`는 검색·브라우저 도구 없이 `01_news_brief.md`만 참조해 창작 할루시네이션 원천 차단.
- **6종 동적 레이아웃 (`L1~L6`)**: 고정 마스코트(다크틸 베레모 흰 곰) + `#FFFDF5` 배경 + 순백 컨테이너(`NO notebook lines`) 위에 `L1`(캐릭터 노트), `L2`(VS 비교·차트), `L3`(Before/After), `L4`(3단계 스텝), `L5`(대형 UI+지시선), `L6`(대형 훅+리액션)을 뉴스 성격에 맞춰 조합.

### 영구 기억 (SQLite Memory — `data/studio.db`)
- **`collected_news`**: URL·정규화 제목 SHA-256 해시로 최근 **30일 중복 뉴스 자동 차단**.
- **`runs`**: 파이프라인 실행 슬러그·포맷·상태 추적.
- **`published_posts`**: 발행 완료 슬러그 멱등성 보장, 1일 1회 제한, 직전 `layout_id` 기록(`last-layout`으로 연속 구도 중복 방지).

---

## 🔒 하네스 훅 (PreToolUse Hook)

`.claude/settings.json`에 등록된 `guard_publish.py`가 인스타그램 업로드 `Bash` 명령 실행 직전 아래 5가지를 **물리적으로 검사**해 하나라도 미달하면 실행을 차단(exit 2)합니다.

1. `INSTA_PUBLISH_RUN_DIR` 대상 폴더 지정 여부
2. `05_gate2_publish.md`의 `결정: 승인` (또는 무결점 `예약자동승인`) 여부
3. `03_qc_report.md` 미해결 `FAIL` / `MISMATCH` 0건 여부
4. `images/*.png` 파일 존재 및 예약 시 `05_image_qc.md` 전 컷 `PASS` 여부
5. `studio.db` 중복 발행 및 예약 모드 1일 1회 상한 초과 여부

---

## 🛠️ 도구 툴 (Tools & Scripts)

- **Python 3 표준 라이브러리 전용** (외부 패키지 설치 불필요):
  - `dedup_store.py` : 30일 중복 제거, 멱등 발행, 직전 레이아웃 조회
  - `validate_contract.py` : 발행일·URL·한글 글자수(`14자/24자`)·`8%` 여백·카드뉴스 레이아웃 다양성(`3종 이상`, 연속 중복 금지) 검증
  - `guard_publish.py` : Gate 2 물리 잠금 훅
  - `verify_published_payload.py` : 게시 후 캡션 누락·중복·슬라이드 불일치 자동 경보
- **브라우저 자동화 (`ego-browser`)**: 로그인 세션 유지 상태로 Gemini `Hydrogen`(`3:4`) 이미지 생성 및 인스타그램 업로드·사후 컨펌 수행 (2FA/CAPTCHA 시 즉시 `handOff`).

---

## 🔌 확장 플러그인 & 연동

- **Antigravity 스케줄 자동화**: 매일 오전 11시(`CRON_TZ=Asia/Seoul 0 11 * * *`) 무인 실행 예약 연동.
- **Ego Browser (`ego-lite`)**: 로그인 세션 기반 Gemini 웹 & Instagram 웹 자동화.
- **확장 포인트**: `config/studio.json` 수정만으로 타깃 AI 기업, 브랜드 톤, 6종 레이아웃 다양성 규칙, 계정명, 예약 시각을 코드 수정 없이 교체 가능.

---

## 📌 참고 (실전 검증 및 트러블슈팅)

- **오프라인 테스트**: `tests/test_harness.py` 단위 테스트 6종 상시 검증 (`dedup`, `validator`, `layout diversity`, `guard_publish`, `verify_published_payload`).
- **핵심 실전 트러블슈팅 반영**:
  - Gemini 다운로드 버튼 가림 → `<canvas>` 기반 원본 `896×1200` PNG 직접 추출
  - 인스타 합성 클릭 시 캡션 누락 → `비우기 → paste+공백 → heading blur → N/2200 카운터 확인 → 실제 포인터 클릭` (모달 내 `Escape` 금지)
  - 사후 업로드 누락 방지 → Agent 7(`publish-auditor`) 신설 및 실제 URL 자동 재검증
