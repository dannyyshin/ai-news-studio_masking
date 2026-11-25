---
name: ai-news-collect
description: Google(Gemini), OpenAI(ChatGPT), Anthropic(Claude), xAI(Grok) 등의 최신 AI 업데이트·버전·신기능을 에고라이트(ego-browser)와 웹으로 수집하고 SQLite 중복 제거 후 01_news_brief.md로 저장하는 스킬. "/ai-news-collect", "AI 최신 뉴스 모아줘" 요청에 사용.
allowed-tools: Read, Write, Glob, WebSearch, WebFetch, Bash(ego-browser:*), Bash(python3 <PROJECT_ROOT>/.claude/skills/ai-news-collect/scripts/dedup_store.py:*)
---

# AI 업계 최신 뉴스 수집 (`/ai-news-collect`)

## 입력 & 출력
- 입력: `outputs/<슬러그>/00_input.md` (없으면 기본값: 4대 AI 기업, 최근 72시간, 오늘 날짜)
- 출력: `outputs/<슬러그>/01_news_brief.md` (`template.md` 양식)

## 실행 순서
1. **공식 소스 로드**: `references/ai-sources.md`를 읽고 타깃 기업별 1차 공식 채널 URL을 확인한다.
2. **에고라이트 + 웹 수집**:
   - `WebSearch`와 `ego-browser nodejs`를 병행해 최근 **72시간 이내** 업데이트·신규 버전·신기능·가격/정책 변화를 수집한다.
   - 반드시 원문 페이지에 접속해 **정확한 발행일(`YYYY-MM-DD`)**, **공식 버전/모델명**, **핵심 팩트 3~5개**, **실제 URL(`https://...`)**을 확인한다.
   - 에고라이트 로그인이 필요한 사이트나 봇 차단이 뜨면 우회하지 말고 공식 블로그/다른 1차 출처를 이용하거나 `handOff()`한다.
3. **SQLite 30일 중복 검사 (필수)**:
   후보마다 `dedup_store.py`를 호출해 이미 다룬 뉴스/발행된 주제는 제외한다.
   ```bash
   python3 <PROJECT_ROOT>/.claude/skills/ai-news-collect/scripts/dedup_store.py check-news --url "<URL>" --title "<제목>"
   ```
4. **Loop 1 (후보 부족 보강)**:
   신규 핵심 소식이 1건도 없으면 검색 기간을 7일(168h)로 넓히거나 커뮤니티/전문매체 교차 검색을 최대 2회 수행한다.
5. **저장 및 DB 기록**:
   - `template.md` 형식에 맞춰 `01_news_brief.md`를 저장한다.
   - 선정한 뉴스는 `dedup_store.py record-news`로 DB에 기록한다.
