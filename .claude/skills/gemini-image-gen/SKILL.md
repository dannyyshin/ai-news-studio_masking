---
name: gemini-image-gen
description: Gate 1 승인 후 에고라이트(ego-browser)로 Gemini 'SNS용 웹툰 이미지 생성' 창(3:4, 이미지, Hydrogen)에 접속해 이미지를 생성·저장하고 PNG를 직접 읽어 한글 깨짐·잘림을 검수하는 스킬. "/gemini-image-gen", "제미나이 이미지 만들어줘" 요청에 사용.
allowed-tools: Read, Write, Glob, Bash(ego-browser:*)
---

# Gemini 이미지 제작 & 시각 검수 (`/gemini-image-gen`)

## 입력 & 출력
- 입력: `outputs/<슬러그>/02_content.md`, `outputs/<슬러그>/04_gate1_content.md` (`결정: 승인` 필수)
- 출력: `outputs/<슬러그>/images/card_01.png`~ (또는 `webtoon_01.png`), `outputs/<슬러그>/05_image_qc.md`

## 실행 전 확인
1. `04_gate1_content.md`의 `결정:`이 `승인`인지 확인한다. 미승인이면 중단한다.
2. `references/gemini-ego-playbook.md`를 읽고 최신 `ego-browser nodejs` 절차와 선택자 규칙을 따른다.

## 작업 절차
1. **TaskSpace 재사용/생성**: `outputs/<슬러그>/state.json`의 `taskSpaceId`를 확인한다. 없으면 새 `taskSpace("ai-news-studio")`를 만들고 ID를 `state.json`에 저장한다.
2. **전용 Gemini 채팅 열기**: `https://gemini.google.com/app/<YOUR_CHAT_ID>` (`SNS용 웹툰 이미지 생성`)으로 이동한다.
   - 미로그인 또는 보안 확인이 뜨면 `await task.handOff()` 후 사용자에게 로그인 완료를 요청한다.
3. **3종 옵션 검증 (매 컷 전 확인)**:
   - 비율: **`3:4`** / 형식: **`이미지`** / 모델: **`Hydrogen`**
4. **순차 생성 & 절대경로 저장**:
   - `02_content.md`의 컷별 프롬프트를 `keyboard.paste()`로 입력(한글 보존) → 전송 → 생성 완료 대기 → 다운로드 버튼(`waitForEvent("download")` + `download.saveAs(...)`) 또는 이미지 `page.fetch(src, { saveAs })`로 `<PROJECT_ROOT>/outputs/<슬러그>/images/<파일명>.png`에 저장한다.
5. **시각 검수 루프 (Loop 3)**:
   - 저장된 **모든 PNG를 `Read` 도구로 열어** 한글 깨짐·중복 음절·상단 말풍선 잘림·3:4 비율을 확인한다.
   - 불량 컷만 한글 문구를 더 짧게 다듬어 최대 2회 재생성하고 결과를 `05_image_qc.md`에 기록한다.
