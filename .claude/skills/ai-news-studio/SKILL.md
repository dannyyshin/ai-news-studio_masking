---
name: ai-news-studio
description: AI 업계 최신 뉴스 수집부터 @your_instagram_id 인스타그램 원고·프롬프트 작성, 독립 팩트 QC, Gemini 3:4 이미지 제작, 인스타 자동 공유까지 6개 에이전트를 지휘하는 총괄 오케스트레이터 스킬. "/ai-news-studio", "AI 뉴스 인스타 올려줘" 요청에 사용.
allowed-tools: Read, Write, Edit, Glob, Agent, AskUserQuestion, Bash(python3 <PROJECT_ROOT>/.claude/skills/ai-news-collect/scripts/dedup_store.py:*)
---

# AI News Studio 오케스트레이터 (`/ai-news-studio`)

전체 파이프라인과 3개 루프, 2개 휴먼 게이트를 관리한다.

## STEP 0. 사전 확인 (매번 필수)
사용자에게 `AskUserQuestion`으로 아래 3가지를 확인한다.
1. **뉴스 주제/대상**: 기본 전체(Google Gemini · OpenAI ChatGPT · Anthropic Claude · xAI Grok) 또는 특정 이슈 지정
2. **콘텐츠 포맷 선택** (기본값 명시):
   - **① 카드뉴스 (5~6장, 3:4 비율) — 기본값**
   - **② 1컷 웹툰 (단일 1컷, 3:4 비율)**
   - **③ 둘 다 (카드뉴스 + 1컷 웹툰)**
3. **실행 범위**: 전체 자동 진행(Gate 1·2 포함) / 원고·QC까지만 / 취소

확인되면 오늘 날짜 기준 슬러그(`<YYYYMMDD-주제슬러그>`)를 정하고 아래 2개 파일을 생성한다:
- `outputs/<슬러그>/00_input.md` (확정 포맷 `cardnews` | `webtoon` | `both`, 브랜드 톤 A, 계정 `your_instagram_id`, 오늘 날짜)
- `outputs/<슬러그>/state.json` (`{"step": "STEP_1", "format": "...", "taskSpaceId": null, "loop1": 0, "loop2": 0, "loop3": {}}`)
그리고 `dedup_store.py start-run --slug <슬러그> --format <포맷>`으로 DB에 실행을 등록한다.

## STEP 1. 최신 뉴스 수집 (`ai-researcher`)
- `Agent`로 `ai-researcher`를 호출해 `01_news_brief.md`를 생성한다.
- 후보 부족 시 Loop 1(최대 2회)로 기간을 72h → 168h로 확장해 재수집한다.

## STEP 2. 원고 & 프롬프트 제작 (`content-writer`) ⇄ STEP 3. 독립 검수 (`fact-qc`) [Loop 2]
1. `content-writer`를 호출해 `02_content.md` 작성.
2. `fact-qc`를 **새 컨텍스트**로 호출(경로 `00_input.md`, `01_news_brief.md`, `02_content.md`만 전달)해 `03_qc_report.md` 생성.
3. `FAIL ≥ 1` 또는 `MISMATCH ≥ 1`이면 기존 파일을 `02_content_v1.md`로 백업하고 `content-writer`에게 보완 지시 → `fact-qc` 재검수 (**최대 2회**).

## STEP 4. Gate 1 — 콘텐츠·프롬프트 결재 (사용자)
1. `gate1-template.md` 양식으로 `04_gate1_content.md` 초안을 만든다.
2. 원고 요약, 컷별 프롬프트 한글 문구, `03_qc_report.md` 판정을 보여주고 `AskUserQuestion`으로 묻는다:
   - `"이미지 제작 승인"` / `"원고·프롬프트 수정"` / `"중단"`
3. 결정과 시각을 `04_gate1_content.md`에 기록한다. 승인 시에만 STEP 5로 이동한다.

## STEP 5. Gemini 이미지 제작 & 시각 검수 (`image-producer`) [Loop 3]
- `image-producer`를 호출해 `SNS용 웹툰 이미지 생성` 창(`3:4` / `이미지` / `Hydrogen`)에서 이미지를 생성하고 `Read`로 전수 시각 검수한다.
- 불량 컷만 최대 2회 재생성한다(`05_image_qc.md` 기록).
- `handOff()` 보고 시 사용자에게 에고라이트 로그인/확인 완료를 요청한 뒤 재개한다.

## STEP 6. Gate 2 — 최종 발행 결재 (사용자) → 인스타 자동 공유 (`insta-publisher`)
1. `gate2-template.md` 양식으로 `05_gate2_publish.md` 초안을 만들고 생성 이미지 경로·시각 검수 결과·최종 캡션을 보고한다.
2. `AskUserQuestion`으로 묻는다: `"인스타 공유 승인 (완전자동 게시)"` / `"특정 컷 재생성"` / `"캡션 수정"` / `"중단"`
3. 승인 시 `05_gate2_publish.md`에 `결정: 승인`과 `결정 시각:`을 기록한 뒤 `insta-publisher`를 호출해 `@your_instagram_id` 업로드 및 `공유하기` 클릭까지 실행한다.

## STEP 7. 업로드 사후 컨펌 & DB 확정 (`publish-auditor`)
1. `publish-auditor`를 호출해 실제 게시물 URL을 새 탭으로 열어 `verify_published_payload.py`로 캡션·해시태그·슬라이드 수·오류 여부를 검증하고 `07_publish_confirm.md`를 저장한다.
2. **`PASS` 시**: `dedup_store.py mark-published`로 DB 발행 완료를 확정하고 게시 URL·증빙 스크린샷을 보고한다.
3. **`ALERT_*` 시**: DB 완료 기록을 보류하고, 발견된 문제(원고 누락, 슬라이드 불일치 등)와 복구 방법(`게시물 수정` / `삭제 후 재게시`)을 즉시 경보 보고한다.

## 예약 무인 실행 모드 (`--scheduled-auto`, 매일 오전 11시 KST)
- STEP 0 질문을 생략하고 기본값(**포맷: `cardnews` 5장, 3:4 / 최근 72h 미발행 뉴스**)으로 진행한다.
- `validate_contract.py` 통과 + `03_qc_report.md` (`FAIL=0`, `MISMATCH=0`) + `05_image_qc.md` (전 컷 `PASS`)를 모두 충족할 때만 `05_gate2_publish.md`에 `결정: 예약자동승인`과 시각을 기록해 자동 게시하고, STEP 7 `publish-auditor` 통과 후 DB를 확정한다.
- 1일 1회 발행 제한(같은 KST 날짜에 이미 게시물이 있으면 `guard_publish.py`가 차단) 및 로그인·2FA·업로드 경보 발생 시 즉시 보류 보고한다.
