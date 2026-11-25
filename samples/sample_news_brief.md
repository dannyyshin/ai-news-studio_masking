# AI 업계 최신 뉴스 브리핑 (`01_news_brief.md`)

- 수집 기준일: 2026-11-25
- 탐색 기간: 최근 72시간
- 대상 기업: Google (Gemini) / OpenAI (ChatGPT) / Anthropic (Claude) / xAI (Grok)
- SQLite 중복 체크: 통과 (신규 1건)

## 1. 오늘의 메인 뉴스 (SNS 제작 대상)
- **뉴스 제목**: Claude Code, 스킬·서브에이전트·훅 기반 팀 오케스트레이션 표준 공개
- **기업 / 제품**: Anthropic / Claude Code
- **발행일**: 2026-11-24
- **1차 출처 URL**: https://docs.anthropic.com/en/docs/claude-code/overview
- **핵심 팩트 요약 (원문 확인 완료)**:
  1. `CLAUDE.md`, `.claude/skills/`, `.claude/agents/`, `PreToolUse` 훅을 프로젝트 폴더 단위로 묶어 팀 공유 가능.
  2. 서브에이전트는 독립 컨텍스트로 동작해 자기검증 편향을 줄이고 병렬 실행을 지원함.
  3. 훅(Hook)은 모델 판단과 무관하게 실행 직전 규칙 위반 명령을 차단함.
- **일반 사용자·실무자 체감 포인트 (왜 중요한가?)**:
  - AI에게 매번 같은 프롬프트를 복붙하지 않고, 회사 매뉴얼 폴더처럼 팀원에게 그대로 넘겨 쓸 수 있게 됨.

## 3. 검증용 원문 팩트 테이블 (QC-B 대조 기준)
| ID | 주장 / 수치 / 버전명 | 원문 근거 문장 | 출처 URL |
|---|---|---|---|
| F1 | 폴더 단위 스킬·서브에이전트 공유 | 프로젝트 `.claude/` 폴더로 팀 공유 | https://docs.anthropic.com/en/docs/claude-code/overview |
| F2 | 훅 기반 실행 전 차단 | PreToolUse 훅으로 명령 실행 전 검증 | https://docs.anthropic.com/en/docs/claude-code/hooks |
