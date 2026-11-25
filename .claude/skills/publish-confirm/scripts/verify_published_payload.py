#!/usr/bin/env python3
"""Deterministic post-publish auditor for Instagram @your_instagram_id posts.

Compares expected caption/hashtags/format from 02_content.md against live DOM data
extracted from the published Instagram post URL and emits PASS or ALERT_*.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def extract_caption(content_text: str) -> str:
    m = re.search(
        r"##\s*1\.\s*인스타그램[^\n]*\n+```[^\n]*\n(.*?)```",
        content_text,
        re.DOTALL,
    )
    return m.group(1).strip() if m else ""


def compact(text: str) -> str:
    return re.sub(r"\s+", "", text)


def verify_payload(
    content_text: str,
    live: dict,
    fmt: str,
    expected_username: str = "your_instagram_id",
) -> dict:
    issues: list[str] = []
    status = "PASS"

    url = str(live.get("url") or "")
    title = str(live.get("title") or "").strip()
    author = str(live.get("author") or "").strip().lower()
    article_text = str(live.get("articleText") or "")
    meta_desc = str(live.get("metaDesc") or "")
    combined_live = f"{article_text}\n{meta_desc}"
    image_count = int(live.get("imageCount") or 0)
    has_carousel_next = bool(live.get("hasCarouselNext"))

    # 1. Page health
    if title.lower() == "error" or ("/p/" not in url and "/reel/" not in url):
        status = "ALERT_PAGE_ERROR"
        issues.append(f"게시물 페이지가 정상 로드되지 않았습니다 (title='{title}', url='{url}').")

    # 2. Author check
    if expected_username and expected_username.lower() not in (author or url.lower() + " " + article_text.lower()):
        if status == "PASS":
            status = "ALERT_AUTHOR_MISMATCH"
        issues.append(f"게시 계정이 '{expected_username}'와 일치하지 않습니다 (author='{author}').")

    # 3. Caption & hashtags check
    expected_caption = extract_caption(content_text)
    if not expected_caption:
        if status == "PASS":
            status = "ALERT_CAPTION_MISSING"
        issues.append("02_content.md에서 기대 캡션을 읽을 수 없습니다.")
    else:
        first_line = next((ln.strip() for ln in expected_caption.splitlines() if ln.strip()), "")
        hook_probe = compact(first_line)[:15]
        live_compact = compact(combined_live)
        # Strip UI chrome text to detect truly empty caption
        stripped_article = (
            article_text.replace("아직 댓글이 없습니다.", "")
            .replace("댓글을 남겨보세요.", "")
            .replace("인사이트 보기", "")
            .replace("게시물 홍보하기", "")
            .replace(expected_username, "")
            .strip()
        )
        primary_text_compact = compact(article_text) if article_text.strip() else compact(meta_desc)
        probe40 = compact(expected_caption)[:40]
        if not live_compact or (hook_probe and hook_probe not in live_compact) or len(stripped_article) < 20:
            if status == "PASS":
                status = "ALERT_CAPTION_MISSING"
            issues.append(
                "실제 게시물에 원고(캡션)가 누락되었거나 잘렸습니다. ('... → 수정'으로 캡션을 재입력하세요.)"
            )
        elif hook_probe and primary_text_compact.count(hook_probe) > 1 and probe40 and primary_text_compact.count(probe40) > 1:
            if status == "PASS":
                status = "ALERT_CAPTION_DUPLICATED"
            issues.append(
                "실제 게시물 캡션이 중복 입력되었습니다. ('... → 수정'으로 중복된 문단을 정리하세요.)"
            )

        expected_tags = [t.lower() for t in re.findall(r"#[^\s#]+", expected_caption)]
        if expected_tags:
            found_tags = [t for t in expected_tags if t in combined_live.lower()]
            ratio = len(found_tags) / len(expected_tags)
            if ratio < 0.7:
                if status == "PASS":
                    status = "ALERT_CAPTION_MISSING"
                issues.append(
                    f"해시태그 반영률이 부족합니다 ({len(found_tags)}/{len(expected_tags)}개 노출)."
                )

    # 4. Media / carousel check
    if image_count < 1 and status != "ALERT_PAGE_ERROR":
        if status == "PASS":
            status = "ALERT_SLIDE_MISMATCH"
        issues.append("게시물 내 이미지가 감지되지 않았습니다.")
    elif fmt in ("cardnews", "both") and not has_carousel_next and image_count < 2:
        if status == "PASS":
            status = "ALERT_SLIDE_MISMATCH"
        issues.append(
            f"포맷 '{fmt}'는 다중 슬라이드(캐러셀)여야 하지만 다음 슬라이드 컨트롤이 감지되지 않았습니다."
        )

    remediation = (
        "정상 게시 확인 완료. dedup_store.py mark-published로 DB를 확정하세요."
        if not issues
        else "🚨 즉시 사용자에게 보고하고, 우측 상단 '...' → 수정으로 원고를 재입력하거나 게시물 삭제 후 재시도하세요."
    )

    return {
        "passed": len(issues) == 0,
        "status": status,
        "url": url,
        "format": fmt,
        "issue_count": len(issues),
        "issues": issues,
        "remediation": remediation,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Verify published Instagram post matches 02_content.md")
    ap.add_argument("--content", required=True, help="Path to 02_content.md")
    ap.add_argument("--live-json", required=True, help="JSON extracted from live Instagram post")
    ap.add_argument("--format", default="cardnews", choices=["cardnews", "webtoon", "both"])
    ap.add_argument("--expected-username", default="your_instagram_id")
    args = ap.parse_args(argv)

    content_text = Path(args.content).read_text(encoding="utf-8")
    live_data = json.loads(Path(args.live_json).read_text(encoding="utf-8"))
    res = verify_payload(content_text, live_data, args.format, args.expected_username)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0 if res["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
