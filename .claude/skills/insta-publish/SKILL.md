---
name: insta-publish
description: Gate 2 승인 후 에고라이트에 로그인된 인스타그램(@your_instagram_id)에 이미지 업로드, 비율 선택, 캡션 입력(React 상태 커밋 검증), 실제 포인터 공유하기 클릭까지 실행하는 스킬. "/insta-publish", "인스타에 올려줘" 요청에 사용.
allowed-tools: Read, Write, Glob, Bash(INSTA_PUBLISH_RUN_DIR=* ego-browser:*)
---

# 인스타그램(@your_instagram_id) 자동 발행 (`/insta-publish`)

## 입력 & 출력
- 입력: `outputs/<슬러그>/05_gate2_publish.md` (`결정: 승인` 또는 `예약자동승인` 필수), `02_content.md`, `images/*.png`
- 출력: `outputs/<슬러그>/06_publish_result.md`, `outputs/<슬러그>/images/06_publish_screenshot.png`

## Hook 잠금 계약 (필수)
`.claude/hooks/guard_publish.py`가 `PreToolUse` Hook으로 실행을 감시한다.
발행용 `ego-browser` 명령에는 반드시 `INSTA_PUBLISH_RUN_DIR`을 절대경로로 지정한다.

## 실행 절차 (`references/insta-ego-playbook.md` 엄수)
1. **계정 검증**: `https://www.instagram.com/` 로그인 계정이 **`your_instagram_id`**인지 확인 (불일치/2FA 시 `handOff()`).
2. **다중/단일 업로드 & 비율**: `새로운 게시물` → `게시물` → `setInputFiles` → **`원본`(3:4)** 또는 **`4:5`** 선택 → `다음` 2회.
3. **캡션 커밋 5단계 (원고 누락·중복 차단)**:
   - 기존 내용 비우기(`ControlOrMeta+A` + `Backspace`) → `keyboard.paste(CAPTION + " ")` (`Escape` 금지) → 모달 제목(`heading "새 게시물 만들기"`) 클릭으로 강제 `blur` → **`N / 2200` 카운터가 `0`이 아니고 중복 입력되지 않았는지 확인** (0이면 `insertText` 폴백).
4. **실제 포인터 `공유하기` 클릭**: `page.evaluate(() => el.click())` 금지. 반드시 스냅샷 `@ref`에 `page.click()`으로 1회 클릭 → `"게시물이 공유되었습니다"` 확인 및 스크린샷 저장.
5. **URL 확보 & Agent 7 인계**: 프로필 최신 글 URL을 `06_publish_result.md`에 적은 뒤 `/publish-confirm`(`publish-auditor`) 검증을 요청한다.
