# AI News Studio (`@your_instagram_id`) — 공통 팀 사규

7개 전담 에이전트(`director` → `ai-researcher` → `content-writer` ⇄ `fact-qc` → `image-producer` → `insta-publisher` → `publish-auditor`)가 최신 AI 업계 뉴스를 수집·검증해 인스타그램(`your_instagram_id`)에 발행·사후 컨펌하는 오케스트레이션이다.

## 1. 브랜드 & 포맷 기본값
- **인스타그램 계정**: `your_instagram_id`
- **기본 톤(A안)**: 친근하고 위트 있는 AI 큐레이터 ("오늘 AI 업계 난리 난 이유 30초 정리")
- **포맷 선택**: 매번 STEP 0에서 사용자에게 묻되, 기본값은 **① 카드뉴스 (5~6장, 3:4)**이며 ② 1컷 웹툰(3:4), ③ 둘 다를 지원한다.
- **이미지 생성 설정**: Gemini `SNS용 웹툰 이미지 생성` 창(`3:4` · `이미지` · `Hydrogen` 모델)에서 한글 텍스트를 직접 생성한다.

## 2. 데이터 계약 (`outputs/<YYYYMMDD-슬러그>/`)
모든 단계는 고정된 파일명으로 이어달린다. 앞 단계 파일이 없으면 지어내지 말고 선행 스킬 실행을 안내한다.

| 파일 | 담당 | 내용 |
|---|---|---|
| `state.json` | 공통 | 현재 단계, 포맷, `taskSpaceId`, 루프 횟수 |
| `00_input.md` | director | STEP 0 확정 조건 (타깃, 포맷, 톤) |
| `01_news_brief.md` | ai-researcher | 72h 이내 미발행 AI 뉴스 + 1차 출처 URL + 발행일 |
| `02_content.md` | content-writer | 인스타 캡션/해시태그 + 3:4 이미지 프롬프트 (수정 시 `_v1` 백업) |
| `03_qc_report.md` | fact-qc | 독립 팩트·할루시네이션·최신성·한글 캡 검수 결과 |
| `04_gate1_content.md` | director | Gate 1 원고·프롬프트 사용자 결재 |
| `images/*.png` | image-producer | 생성된 3:4 PNG 파일 (`card_01.png`~, `webtoon_01.png`) |
| `05_image_qc.md` | image-producer | 컷별 시각/한글 깨짐/잘림 검수 기록 |
| `05_gate2_publish.md` | director | Gate 2 최종 발행 결재 (PreToolUse Hook 잠금 대상) |
| `06_publish_result.md` | insta-publisher | 게시 URL + 완료 스크린샷 경로 |
| `07_publish_confirm.md` | publish-auditor | 실제 게시물 URL 원고·슬라이드 사후 컨펌 보고 |

## 3. 절대 규칙 (Hallucination & Safety)
1. **근거 없는 수치·기능 창작 금지**: 모든 AI 모델명·버전·가격·출시일은 `01_news_brief.md`의 1차 출처 URL과 발행일(`YYYY-MM-DD`)에 근거한다.
2. **6종 동적 레이아웃(`L1~L6`) & 한글 가독성 규칙**: 뉴스 성격에 맞춰 `layout-library.md`의 6종 레이아웃을 조합하며(카드뉴스 최소 3종 이상 · 연속 중복 금지), 미색 배경(`#FFFDF5`), 순백 카드(`NO notebook lines`), 제목 `14자 이하`, 부제 `24자 이하`, 컨테이너 줄당 `14자 이하`(`\n` 명시), `8%` 안전 여백을 지킨다.
3. **에고라이트(`ego-browser`) 절대 경로 규칙**: `ego-browser nodejs`는 셸 작업 폴더와 환경변수를 상속하지 않으므로 모든 파일 경로는 `<PROJECT_ROOT>/...` 절대경로를 사용한다.
4. **로그인/2FA/CAPTCHA 우회 금지**: 문제 시 즉시 `await task.handOff()` 후 사용자에게 직접 조작을 요청한다.
5. **이중 게이트 준수**: Gate 1 승인 없이 이미지 제작 금지, Gate 2(`결정: 승인` 또는 예약 무인 실행 시 무결점 조건의 `결정: 예약자동승인`) 없이 인스타그램 업로드·공유 금지(`guard_publish.py` Hook이 물리 차단).
6. **매일 오전 11시 예약 모드 (`--scheduled-auto`)**: 카드뉴스 5장(3:4) 기본, 1일 1회 제한, `FAIL=0 / MISMATCH=0 / 이미지 FAIL=0`인 경우에만 `예약자동승인`으로 자동 게시하고 이상 시 보류한다.
7. **문체**: 보고서·결과 파일은 한국어 평서문, 인스타 캡션은 톤 A 구어체 큐레이션으로 작성한다.
