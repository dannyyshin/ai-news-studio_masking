# 인스타그램 업로드 컨펌 보고서 (`07_publish_confirm.md`)

- 프로젝트: <슬러그>
- 검증 대상 URL: <https://www.instagram.com/your_instagram_id/p/.../>
- 검증 시각: YYYY-MM-DD HH:MM KST
- 증빙 스크린샷: `images/07_confirm_screenshot.png`

## 1. 최종 컨펌 결과
- **최종 상태**: <PASS | ALERT_CAPTION_MISSING | ALERT_SLIDE_MISMATCH | ALERT_PAGE_ERROR | ALERT_AUTHOR_MISMATCH>
- **DB 확정 여부**: <기록 완료 | 보류 (문제 발견)>

## 2. 항목별 감사 결과
| 점검 항목 | 기대값 | 실제 확인 결과 | 판정 |
|---|---|---|---|
| 페이지 정상 로드 | 오류 아님, `/p/` URL | | |
| 게시 계정 | `your_instagram_id` | | |
| 캡션 첫 줄 훅 | `02_content.md` 첫 줄 일치 | | |
| 해시태그 반영률 | 기대 태그 70% 이상 노출 | | |
| 이미지 / 캐러셀 | 포맷별 1장 또는 다중 슬라이드 | | |

## 3. 문제 및 복구 권고 (ALERT 시 필수)
- 발견 문제: 
- 권장 조치: 
