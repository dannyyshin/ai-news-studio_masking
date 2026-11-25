---
name: publish-confirm
description: 인스타그램에 방금 올라간 게시물 URL을 에고라이트로 열어 원고(캡션)·해시태그·이미지 장수·오류 페이지를 실제 검증하고 문제 시 경보 보고서를 작성하는 업로드 컨펌 스킬. "/publish-confirm", "인스타 업로드 확인해줘" 요청에 사용.
allowed-tools: Read, Write, Glob, Bash(ego-browser:*), Bash(python3 <PROJECT_ROOT>/.claude/skills/publish-confirm/scripts/verify_published_payload.py:*), Bash(python3 <PROJECT_ROOT>/.claude/skills/ai-news-collect/scripts/dedup_store.py:*)
---

# 인스타그램 업로드 컨펌 (`/publish-confirm`)

## 입력 & 출력
- 입력: `outputs/<슬러그>/00_input.md`, `02_content.md`, `06_publish_result.md`
- 출력: `outputs/<슬러그>/live_post.json`, `outputs/<슬러그>/images/07_confirm_screenshot.png`, `outputs/<슬러그>/07_publish_confirm.md` (`template.md` 양식)

## 실행 순서
1. **실제 URL 새 로드 검사 (`ego-browser`)**:
   - `06_publish_result.md`의 게시물 URL(또는 `https://www.instagram.com/your_instagram_id/` 첫 게시물)을 열어 2초 대기 후 아래 데이터를 추출해 `live_post.json`으로 저장한다:
     - `url`, `title`, `author`, `metaDesc`, `articleText`, `imageCount`, `hasCarouselNext`
   - 동시에 `07_confirm_screenshot.png` 스크린샷 저장 후 `await task.finish({ keep: [] })`.
2. **코드 검증 (`verify_published_payload.py`)**:
   ```bash
   python3 <PROJECT_ROOT>/.claude/skills/publish-confirm/scripts/verify_published_payload.py \
     --content <PROJECT_ROOT>/outputs/<슬러그>/02_content.md \
     --live-json <PROJECT_ROOT>/outputs/<슬러그>/live_post.json \
     --format <cardnews|webtoon|both>
   ```
3. **판정 & 사후 처리**:
   - **`PASS` (exit 0)**: `07_publish_confirm.md`에 `최종 상태: PASS` 기록 후 `dedup_store.py mark-published` 실행.
   - **`ALERT_*` (exit 1)**: `07_publish_confirm.md`에 실패 원인과 복구 옵션(`... → 수정`으로 캡션 추가 / 삭제 후 재게시)을 기록하고, DB에 발행 성공으로 기록하지 않은 채 즉시 `director`/사용자에게 경보 보고한다.
