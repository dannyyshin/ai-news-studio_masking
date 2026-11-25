---
name: news-fact-qc
description: 02_content.md의 거짓·할루시네이션·최신성 오류·한글 텍스트 과밀을 코드 검증(validate_contract.py)과 웹 팩트체크로 독립 검수해 03_qc_report.md로 저장하는 스킬. "/news-fact-qc", "원고 팩트 검수해줘" 요청에 사용.
allowed-tools: Read, Write, Glob, WebSearch, WebFetch, Bash(python3 <PROJECT_ROOT>/.claude/skills/news-fact-qc/scripts/validate_contract.py:*)
---

# AI 뉴스 원고 & 프롬프트 독립 QC (`/news-fact-qc`)

## 입력 & 출력
- 입력: `outputs/<슬러그>/00_input.md`, `01_news_brief.md`, `02_content.md`
- 출력: `outputs/<슬러그>/03_qc_report.md` (`template.md` 양식)

## 1단계: 결정론적 코드 계약 검증 (필수)
먼저 아래 스크립트를 실행해 형식·최신성·한글 글자 수 캡을 기계적으로 점검한다.
```bash
python3 <PROJECT_ROOT>/.claude/skills/news-fact-qc/scripts/validate_contract.py \
  --brief <PROJECT_ROOT>/outputs/<슬러그>/01_news_brief.md \
  --content <PROJECT_ROOT>/outputs/<슬러그>/02_content.md \
  --format <cardnews|webtoon|both>
```
스크립트가 반환한 오류(`FAIL`)는 빠짐없이 리포트에 반영한다.

## 2단계: 7대 독립 검수 기준
| ID | 항목 | FAIL / MISMATCH 기준 |
|---|---|---|
| Q1 | **최신성** | 오늘 기준 7일 초과 구버전 뉴스를 최신 신기능처럼 소개 |
| Q2 | **할루시네이션** | `01_news_brief.md` 및 원문에 없는 모델명·수치·가격·기능 추가 |
| Q3 | **웹 팩트 일치** | 원문 URL 재확인 시 수치·버전·대상 요금제가 다름 (`MISMATCH`) |
| Q4 | **과장/단정 차단** | "전부 공짜", "무조건 10배" 등 원문에 없는 과장 표현 |
| Q5 | **한글 텍스트 캡** | 컷당 제목 12자 초과, 본문/말풍선 20자 초과, 3블록 이상 |
| Q6 | **3:4 안전 여백** | 프롬프트에 `3:4` 비율 및 `10% 안전 여백` 지시 누락 |
| Q7 | **톤 & 가독성** | `@your_instagram_id` 톤 A(친근·쉬운 설명) 이탈 또는 전문용어 방치 |

## 3단계: 보고 원칙
- `02_content.md`를 직접 고치지 않는다.
- `FAIL` 또는 `MISMATCH`가 1개라도 있으면 구체적 위치와 수정 지시문을 적어 반환한다.
