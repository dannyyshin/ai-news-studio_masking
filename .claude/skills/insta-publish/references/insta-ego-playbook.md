# 인스타그램 `@your_instagram_id` (`ego-browser v2.2.1`) 자동 업로드 & 공유 플레이북

> **보안 & 잠금 안내**: 발행 명령은 반드시 `INSTA_PUBLISH_RUN_DIR="/abs/path/outputs/<슬러그>"` 접두사를 붙여 실행해야 `guard_publish.py` Hook을 통과한다. Gate 2 미승인 시 Hook이 실행을 차단한다.

## 1. 로그인 & 계정(`your_instagram_id`) 확인
- `https://www.instagram.com/` 이동 → 스냅샷에 로그인 폼, 2FA, 보안 확인이 뜨거나 `your_instagram_id`가 보이지 않으면 즉시 `await task.handOff()` 후 사용자에게 요청한다.
- `"알림 설정"` 팝업(`button "나중에 하기"`)이 뜨면 먼저 클릭해 닫는다.

## 2. 이미지 업로드 & `원본(3:4)` / `4:5` 비율 선택 (실측 셀렉터)
1. 좌측 메뉴 **`새로운 게시물`**(`a:has-text("새로운 게시물")`) 클릭 → 하위 메뉴 **`게시물`**(`a:has-text("게시물") >> nth=-1`) 클릭해 `"새 게시물 만들기"` 모달을 연다.
2. `input[type=file]`은 `display: none` 상태이므로 `waitForSelector` 없이 절대경로 배열(단일 1장 또는 다중 5~6장)을 넣는다.
3. `"자르기"` 모달에서 **`자르기 선택`** 클릭 → **`원본`**(3:4 유지, 없을 시 `4:5`) 클릭 → 모달 상단 **`다음`** 클릭.
4. `"편집"` 모달이 뜨면 스냅샷에서 `dialog "편집"` 안의 **`다음`** `@ref`를 클릭하고, `"캡션 추가..."`가 뜰 때까지 `waitForFunction`으로 대기한다.

## 3. 캡션 입력 & React 상태 커밋 (원고 누락·중복 방지 핵심 절차!)
> **원인 교정 규칙**: Instagram 웹 에디터(Lexical `[contenteditable="true"]`)는 붙여넣기 후 끝이 `#해시태그`로 끝나거나 포커스 이탈(`blur`) 없이 `element.click()`으로 공유하면 React 상태에 캡션이 저장되지 않고 빈 글로 올라갈 수 있다. 반대로 `Escape` 키를 누르면 `"게시물을 삭제하시겠어요?"` 창이 뜨므로 **절대 `Escape`를 누르지 말고** 아래 5단계를 지킨다.

1. `css=[role="dialog"] [contenteditable="true"]`를 클릭한 뒤 `ControlOrMeta+A` + `Backspace`로 비우고 `await page.keyboard.paste(CAPTION_TEXT + " ");`
2. **해시태그 토큰 확정**: 마지막 해시태그 뒤에 공백 1칸(`" "`)만 붙인다 (`Escape` 금지).
3. **강제 `blur`로 React 상태 커밋**: 모달 상단 비활성 제목(`heading "새 게시물 만들기"`) 좌표를 실제 포인터(`page.mouse.click`)로 클릭해 에디터 포커스를 뺀다.
4. **React 글자 수 카운터 이중 검증 (필수)**:
   - `[contenteditable="true"].innerText.trim().length`와 다이얼로그 내부 `N / 2200` 카운터가 **`0 / 2200`이 아니고 기대 길이의 1.3배를 넘지 않는지(중복 붙여넣기 방지)** 확인한다.
   - 카운터가 `0`이면 비우고 `keyboard.insertText(CAPTION_TEXT + " ")` + heading blur로 1회 폴백한다.
5. **실제 포인터로만 `공유하기` 클릭 (금지: `page.evaluate(() => shareBtn.click())`)**:
   - 반드시 `공유하기` 버튼 좌표를 구해 `await page.mouse.click(x, y, { label: "click Instagram share button" })` 또는 스냅샷 `@ref`에 `page.click()`으로 **1회만** 클릭한다.
   - `"게시물이 공유되었습니다"` 확인 후 `06_publish_screenshot.png` 저장.

## 4. 게시물 URL 확보 & 감사 에이전트(`publish-auditor`) 인계
1. `https://www.instagram.com/your_instagram_id/`로 이동해 첫 번째 게시물 URL(`a[href*="/p/"], a[href*="/reel/"]`)을 확보하고 `06_publish_result.md`에 기록한다.
2. `await task.finish({ keep: [] });`로 종료 후, 반드시 **Agent 7(`publish-auditor` / `/publish-confirm`)**에게 실제 URL 검증을 넘긴다. (`dedup_store.py mark-published`는 컨펌 통과 후 확정한다.)
