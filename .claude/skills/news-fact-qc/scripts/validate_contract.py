#!/usr/bin/env python3
"""Deterministic contract validator for 01_news_brief.md and 02_content.md.

Checks freshness, URLs, format slide counts, Korean text character caps for Gemini
(including high-density Instatoon memo/checklist containers), 3:4 aspect ratio
instructions, Instagram caption limits, and unresolved placeholders.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

SEOUL = timezone(timedelta(hours=9), name="KST")

TITLE_MAX_CHARS = 14
BODY_MAX_CHARS = 24
CONTAINER_LINE_MAX_CHARS = 14
CONTAINER_MAX_LINES = 4
MAX_TEXT_BLOCKS = 5
CAPTION_MAX_CHARS = 2200
HASHTAG_MIN = 5
HASHTAG_MAX = 12
VALID_LAYOUTS = ("L1", "L2", "L3", "L4", "L5", "L6")
MIN_DISTINCT_CARDNEWS_LAYOUTS = 3

PLACEHOLDERS = ("TODO", "TBD", "확인 필요", "<슬러그>", "YYYY-MM-DD", "<대사>", "<제목>")


def parse_cuts(content_text: str) -> list[dict]:
    """Parse ### [컷 N] sections from 02_content.md."""
    pattern = re.compile(r"^###\s*\[([^\]]+)\]\s*(.*)$", re.MULTILINE)
    matches = list(pattern.finditer(content_text))
    cuts: list[dict] = []
    for idx, m in enumerate(matches):
        start = m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(content_text)
        body = content_text[start:end]
        cuts.append({"header": m.group(1).strip(), "target": m.group(2).strip(), "body": body})
    return cuts


def extract_caption(content_text: str) -> str:
    """Extract caption block under '## 1. 인스타그램 게시 캡션'."""
    m = re.search(
        r"##\s*1\.\s*인스타그램[^\n]*\n+```[^\n]*\n(.*?)```",
        content_text,
        re.DOTALL,
    )
    if m:
        return m.group(1).strip()
    return ""


def extract_prompt_block(cut_body: str) -> str:
    m = re.search(r"```[^\n]*\n(.*?)```", cut_body, re.DOTALL)
    return m.group(1).strip() if m else ""


def extract_labeled_text(cut_body: str, prefix_regex: str) -> str | None:
    m = re.search(rf"^-\s*{prefix_regex}[^:]*:\s*(.*)$", cut_body, re.MULTILINE)
    if not m:
        return None
    return m.group(1).strip().strip('"').strip("'")


def split_container_lines(raw_text: str) -> list[str]:
    """Split memo/checklist lines by literal \\n or ' / ' separator."""
    normalized = raw_text.replace("\\n", "\n")
    if "\n" in normalized:
        parts = [p.strip() for p in normalized.splitlines() if p.strip()]
    else:
        parts = [p.strip() for p in normalized.split("/") if p.strip()]
    return parts


def check_brief(brief_text: str, today: datetime, max_age_hours: int) -> list[str]:
    issues: list[str] = []
    for req in ("## 1.", "## 3."):
        if req not in brief_text:
            issues.append(f"01_news_brief.md: 필수 섹션 '{req}' 누락")

    urls = re.findall(r"https?://[^\s)\]>]+", brief_text)
    if not urls:
        issues.append("01_news_brief.md: 1차 출처 URL(https://...)이 하나도 없습니다.")

    pub_match = re.search(r"발행일\*{0,2}\s*:\s*(\d{4}-\d{2}-\d{2})", brief_text)
    if not pub_match:
        issues.append("01_news_brief.md: 메인 뉴스 '발행일: YYYY-MM-DD' 형식이 없습니다.")
    else:
        try:
            pub_dt = datetime.strptime(pub_match.group(1), "%Y-%m-%d").replace(tzinfo=SEOUL)
            age = today.replace(hour=0, minute=0, second=0, microsecond=0) - pub_dt
            if age < timedelta(days=-1):
                issues.append(f"01_news_brief.md: 발행일({pub_match.group(1)})이 미래 날짜입니다.")
            elif age > timedelta(hours=max_age_hours):
                issues.append(
                    f"01_news_brief.md: 발행일({pub_match.group(1)})이 허용 기간({max_age_hours}h)을 초과했습니다."
                )
        except ValueError:
            issues.append(f"01_news_brief.md: 발행일 파싱 실패 ({pub_match.group(1)})")

    for ph in PLACEHOLDERS:
        if ph in brief_text:
            issues.append(f"01_news_brief.md: 미완성 자리표시자 '{ph}'가 남아 있습니다.")
    return issues


def extract_layout_code(cut_body: str) -> str | None:
    """Extract layout code L1..L6 from '- 레이아웃: L6 (...)' line."""
    raw = extract_labeled_text(cut_body, r"레이아웃")
    if not raw:
        return None
    m = re.match(r"^(L[1-6])\b", raw.strip().upper())
    return m.group(1) if m else raw.strip()


def check_content(content_text: str, fmt: str) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    parsed_layouts: list[str] = []

    caption = extract_caption(content_text)
    if not caption:
        issues.append("02_content.md: '## 1. 인스타그램 게시 캡션' 코드 블록을 찾을 수 없습니다.")
    else:
        if len(caption) > CAPTION_MAX_CHARS:
            issues.append(f"02_content.md: 캡션 길이 {len(caption)}자 > 상한 {CAPTION_MAX_CHARS}자")
        hashtags = re.findall(r"#[^\s#]+", caption)
        if not (HASHTAG_MIN <= len(hashtags) <= HASHTAG_MAX):
            issues.append(
                f"02_content.md: 해시태그 {len(hashtags)}개 (권장 {HASHTAG_MIN}~{HASHTAG_MAX}개)"
            )

    if "## 3. 팩트 근거 매핑" not in content_text:
        issues.append("02_content.md: '## 3. 팩트 근거 매핑' 표가 누락되었습니다.")

    cuts = parse_cuts(content_text)
    expected = {"cardnews": (5, 6), "webtoon": (1, 1), "both": (6, 7)}
    if fmt not in expected:
        issues.append(f"지원하지 않는 포맷 '{fmt}' (cardnews / webtoon / both 중 선택)")
    else:
        lo, hi = expected[fmt]
        if not (lo <= len(cuts) <= hi):
            issues.append(
                f"02_content.md: 포맷 '{fmt}'는 {lo}~{hi}컷이어야 하는데 현재 {len(cuts)}컷입니다."
            )

    if fmt == "both":
        targets = " ".join(c["target"] for c in cuts)
        if "card_" not in targets or "webtoon_" not in targets:
            issues.append("02_content.md: 'both' 포맷은 card_*.png와 webtoon_*.png를 모두 포함해야 합니다.")

    card_layouts: list[tuple[str, str]] = []
    for cut in cuts:
        label = cut["header"]
        target = cut["target"]
        body = cut["body"]

        layout_code = extract_layout_code(body)
        if layout_code is None:
            issues.append(f"[{label}] '- 레이아웃: L1~L6' 명세가 누락되었습니다.")
        elif layout_code not in VALID_LAYOUTS:
            issues.append(
                f"[{label}] 지원하지 않는 레이아웃 '{layout_code}' ({', '.join(VALID_LAYOUTS)} 중 선택)"
            )
        else:
            parsed_layouts.append(layout_code)
            if fmt == "cardnews" or (fmt == "both" and "card_" in target):
                card_layouts.append((label, layout_code))

        title_txt = extract_labeled_text(body, r"한글\s*제목")
        sub_txt = extract_labeled_text(body, r"한글\s*(?:부제|대사|말풍선)")
        memo1 = extract_labeled_text(body, r"메모지\s*1")
        memo2 = extract_labeled_text(body, r"메모지\s*2")
        compare_tbl = extract_labeled_text(body, r"비교표")
        steps_blk = extract_labeled_text(body, r"스텝")
        callout_blk = extract_labeled_text(body, r"지시선")
        checklist = extract_labeled_text(body, r"체크리스트")
        text_blk1 = extract_labeled_text(body, r"텍스트\s*블록\s*1")
        text_blk2 = extract_labeled_text(body, r"텍스트\s*블록\s*2")
        text_blk3 = extract_labeled_text(body, r"텍스트\s*블록\s*3")
        extra_txt = extract_labeled_text(body, r"추가\s*텍스트")

        containers = (
            ("메모지 1", memo1, 3),
            ("메모지 2", memo2, 3),
            ("비교표", compare_tbl, CONTAINER_MAX_LINES),
            ("스텝", steps_blk, CONTAINER_MAX_LINES),
            ("지시선", callout_blk, CONTAINER_MAX_LINES),
            ("체크리스트", checklist, CONTAINER_MAX_LINES),
            ("텍스트 블록 1", text_blk1, CONTAINER_MAX_LINES),
            ("텍스트 블록 2", text_blk2, CONTAINER_MAX_LINES),
            ("텍스트 블록 3", text_blk3, CONTAINER_MAX_LINES),
        )
        blocks = [t for t in (title_txt, sub_txt, extra_txt, *(c[1] for c in containers)) if t]
        if len(blocks) > MAX_TEXT_BLOCKS:
            issues.append(f"[{label}] 텍스트 블록 {len(blocks)}개 > 최대 {MAX_TEXT_BLOCKS}개")

        if title_txt is None and sub_txt is None:
            issues.append(f"[{label}] 한글 제목/부제(또는 말풍선) 명세가 없습니다.")
        if title_txt and len(title_txt) > TITLE_MAX_CHARS:
            issues.append(
                f"[{label}] 한글 제목 '{title_txt}' {len(title_txt)}자 > {TITLE_MAX_CHARS}자 이하로 줄여 주세요."
            )
        if sub_txt and len(sub_txt) > BODY_MAX_CHARS:
            issues.append(
                f"[{label}] 한글 부제/말풍선 '{sub_txt}' {len(sub_txt)}자 > {BODY_MAX_CHARS}자 이하로 줄여 주세요."
            )

        for cname, cval, max_lines in containers:
            if not cval:
                continue
            lines = split_container_lines(cval)
            if len(lines) > max_lines:
                issues.append(f"[{label}] {cname} {len(lines)}줄 > 최대 {max_lines}줄")
            for ln in lines:
                if len(ln) > CONTAINER_LINE_MAX_CHARS:
                    issues.append(
                        f"[{label}] {cname} 줄 '{ln}' {len(ln)}자 > {CONTAINER_LINE_MAX_CHARS}자 이하로 줄여 주세요."
                    )

        prompt = extract_prompt_block(body)
        if not prompt:
            issues.append(f"[{label}] Gemini 입력 프롬프트 블록이 비어 있습니다.")
        else:
            if "3:4" not in prompt:
                issues.append(f"[{label}] 프롬프트에 '3:4' 비율 지시가 누락되었습니다.")
            if not any(k in prompt.lower() for k in ("safe margin", "안전 여백", "margin")):
                issues.append(f"[{label}] 프롬프트에 가장자리 안전 여백(safe margin) 지시가 누락되었습니다.")

    if fmt in ("cardnews", "both") and len(card_layouts) >= 2:
        distinct = {code for _, code in card_layouts}
        if len(distinct) < MIN_DISTINCT_CARDNEWS_LAYOUTS:
            issues.append(
                f"02_content.md: 카드뉴스 레이아웃 다양성 부족 — 현재 {len(distinct)}종({', '.join(sorted(distinct))}), 최소 {MIN_DISTINCT_CARDNEWS_LAYOUTS}종 이상 조합해야 합니다."
            )
        for idx in range(1, len(card_layouts)):
            prev_lbl, prev_code = card_layouts[idx - 1]
            curr_lbl, curr_code = card_layouts[idx]
            if curr_code == prev_code:
                issues.append(
                    f"02_content.md: 연속된 컷 [{prev_lbl}]→[{curr_lbl}]에 동일한 레이아웃 '{curr_code}'가 중복 배치되었습니다."
                )

    for ph in PLACEHOLDERS:
        if ph in content_text:
            issues.append(f"02_content.md: 미완성 자리표시자 '{ph}'가 남아 있습니다.")
    return issues, parsed_layouts


def validate(
    brief_path: Path,
    content_path: Path,
    fmt: str,
    today: datetime,
    max_age_hours: int,
) -> dict:
    issues: list[str] = []
    layouts: list[str] = []
    if not brief_path.is_file():
        issues.append(f"파일 없음: {brief_path}")
    else:
        issues.extend(check_brief(brief_path.read_text(encoding="utf-8"), today, max_age_hours))

    if not content_path.is_file():
        issues.append(f"파일 없음: {content_path}")
    else:
        content_issues, layouts = check_content(content_path.read_text(encoding="utf-8"), fmt)
        issues.extend(content_issues)

    return {
        "passed": len(issues) == 0,
        "format": fmt,
        "layouts": layouts,
        "issue_count": len(issues),
        "issues": issues,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate 01_news_brief.md and 02_content.md contracts")
    ap.add_argument("--brief", required=True, help="Path to 01_news_brief.md")
    ap.add_argument("--content", required=True, help="Path to 02_content.md")
    ap.add_argument("--format", default="cardnews", choices=["cardnews", "webtoon", "both"])
    ap.add_argument("--max-age-hours", type=int, default=168)
    ap.add_argument("--today", help="Override today YYYY-MM-DD (for deterministic testing)")
    args = ap.parse_args(argv)

    today = (
        datetime.strptime(args.today, "%Y-%m-%d").replace(tzinfo=SEOUL)
        if args.today
        else datetime.now(SEOUL)
    )
    res = validate(Path(args.brief), Path(args.content), args.format, today, args.max_age_hours)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0 if res["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
