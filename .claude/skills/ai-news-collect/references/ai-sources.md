# AI 업계 신뢰 소스 가이드 (1차 공식 출처 우선)

최신 버전·신기능 소식은 2차 루머나 블로그 요약보다 **반드시 아래 1차 공식 채널**에서 발행일과 모델명을 교차 확인한다.

## 1. 4대 핵심 AI 기업 1차 채널
| 기업 / 제품 | 공식 뉴스룸 / 블로그 / 릴리스 노트 | 주요 확인 포인트 |
|---|---|---|
| **Google (Gemini)** | `https://blog.google/technology/ai/`<br>`https://deepmind.google/discover/blog/`<br>`https://gemini.google.com/updates` | Gemini 모델 버전, 앱/웹 신기능, 무료/Pro 제공 범위 |
| **OpenAI (ChatGPT)** | `https://openai.com/news/`<br>`https://help.openai.com/en/articles/6825453-chatgpt-release-notes` | GPT 모델 업데이트, ChatGPT 기능 출시, 요금제별 오픈 일정 |
| **Anthropic (Claude)** | `https://www.anthropic.com/news`<br>`https://docs.anthropic.com/en/release-notes/overview` | Claude 모델, Claude Code, Artifacts/Skills/MCP 업데이트 |
| **xAI (Grok)** | `https://x.ai/news`<br>`https://docs.x.ai/docs/release-notes` | Grok 신규 모델, X 연동 기능, 이미지/추론 기능 |

## 2. 보조 테크 전문지 (1차 출처 교차용)
- **해외**: TechCrunch AI (`https://techcrunch.com/category/artificial-intelligence/`), The Verge AI (`https://www.theverge.com/ai-artificial-intelligence`), Ars Technica
- **국내**: AI타임스 (`https://www.aitimes.com/`), 지디넷코리아, 전자신문

## 3. 수집 필터 규칙
- **반드시 제외**: 발행일이 7일(168h)을 넘은 구버전 소식, "출시 예정 루머"만 있는 미확인 트윗, 출처 URL이 불명확한 요약글.
- **에고라이트(`ego-browser`) 활용 시점**: 동적 JS로 막혀 `WebFetch`가 본문을 못 가져오는 페이지(특히 Release Notes, x.ai, X 공식 계정 포스트)는 `ego-browser nodejs`로 직접 렌더링해 `page.evaluate()`로 제목·날짜·본문을 추출한다.
