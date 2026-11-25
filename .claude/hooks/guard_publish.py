#!/usr/bin/env python3
"""Physical PreToolUse Hook & CLI guard for Instagram publishing (@your_instagram_id).

Blocks Instagram upload/share commands unless Gate 2 is explicitly approved
(either interactive `결정: 승인` or unattended `결정: 예약자동승인`),
QC has no unresolved FAIL/MISMATCH, images exist, and idempotency/daily limits hold.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

SEOUL = timezone(timedelta(hours=9), name="KST")
STUDIO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = STUDIO_ROOT / "data" / "studio.db"
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
PLACEHOLDERS = ("TODO", "TBD", "확인 필요", "<슬러그>", "<대기")


def is_instagram_publish_command(command: str) -> bool:
    """Detect whether a Bash command is attempting Instagram publishing."""
    if "INSTA_PUBLISH_RUN_DIR" in command:
        return True
    low = command.lower()
    if "instagram.com" in low and any(
        kw in low for kw in ("setinputfiles", "공유하기", "share", "waitforfilechooser", "insta-publish")
    ):
        return True
    return False


def extract_run_dir(command: str) -> Path | None:
    m = re.search(r'INSTA_PUBLISH_RUN_DIR\s*=\s*"([^"]+)"', command)
    if not m:
        m = re.search(r"INSTA_PUBLISH_RUN_DIR\s*=\s*'([^']+)'", command)
    if not m:
        m = re.search(r"INSTA_PUBLISH_RUN_DIR\s*=\s*(\S+)", command)
    if m:
        return Path(m.group(1))
    env_val = os.environ.get("INSTA_PUBLISH_RUN_DIR")
    return Path(env_val) if env_val else None


def check_run(run_dir: Path, db_path: Path = DEFAULT_DB, *, today_kst: str | None = None) -> list[str]:
    errors: list[str] = []
    if not run_dir.is_dir():
        return [f"실행 폴더가 존재하지 않습니다: {run_dir}"]

    gate2 = run_dir / "05_gate2_publish.md"
    scheduled_auto = False
    gate2_text = ""
    if not gate2.is_file():
        errors.append("Gate 2 파일(05_gate2_publish.md)이 없습니다. 먼저 사용자 최종 결재를 받으세요.")
    else:
        gate2_text = gate2.read_text(encoding="utf-8")
        dec_m = re.search(r"^-\s*결정\s*:\s*(승인|예약자동승인)\s*$", gate2_text, re.MULTILINE)
        if not dec_m:
            errors.append("Gate 2가 승인되지 않았습니다. '결정: 승인' 또는 '결정: 예약자동승인'이 필요합니다.")
        else:
            scheduled_auto = dec_m.group(1) == "예약자동승인"
        time_m = re.search(r"^-\s*결정 시각\s*:\s*(.+)$", gate2_text, re.MULTILINE)
        if not time_m or not time_m.group(1).strip() or time_m.group(1).strip().startswith("<"):
            errors.append("Gate 2의 '결정 시각'이 비어 있습니다.")

    exception_ok = bool(re.search(r"^-\s*예외 승인\s*:\s*예\s*$", gate2_text, re.MULTILINE))
    if scheduled_auto and exception_ok:
        errors.append("예약자동승인 모드에서는 '예외 승인: 예'가 허용되지 않습니다.")

    qc_path = run_dir / "03_qc_report.md"
    if not qc_path.is_file():
        errors.append("QC 검수 리포트(03_qc_report.md)가 없습니다.")
    elif scheduled_auto or not exception_ok:
        qc_text = qc_path.read_text(encoding="utf-8")
        fail_m = re.search(r"FAIL\s*:\s*(\d+)", qc_text)
        mis_m = re.search(r"MISMATCH\s*:\s*(\d+)", qc_text)
        if fail_m and int(fail_m.group(1)) > 0:
            errors.append(f"03_qc_report.md에 미해결 FAIL({fail_m.group(1)}건)이 남아 있습니다.")
        if mis_m and int(mis_m.group(1)) > 0:
            errors.append(f"03_qc_report.md에 미해결 MISMATCH({mis_m.group(1)}건)이 남아 있습니다.")

    if scheduled_auto:
        img_qc_path = run_dir / "05_image_qc.md"
        if not img_qc_path.is_file():
            errors.append("예약자동승인 모드에서는 이미지 시각 검수 기록(05_image_qc.md)이 필수입니다.")
        else:
            img_qc_text = img_qc_path.read_text(encoding="utf-8")
            if re.search(r"\bFAIL\b", img_qc_text):
                errors.append("05_image_qc.md에 FAIL 판정이 있어 예약자동발행을 차단합니다.")

    content_path = run_dir / "02_content.md"
    if not content_path.is_file():
        errors.append("콘텐츠 원고(02_content.md)가 없습니다.")
    else:
        c_text = content_path.read_text(encoding="utf-8")
        for ph in PLACEHOLDERS:
            if ph in c_text:
                errors.append(f"02_content.md에 미완성 자리표시자('{ph}')가 남아 있습니다.")
                break

    images_dir = run_dir / "images"
    valid_imgs = (
        [
            p
            for p in images_dir.iterdir()
            if p.is_file()
            and p.suffix.lower() in IMAGE_EXTS
            and p.stat().st_size > 0
            and not p.name.startswith("06_publish_")
        ]
        if images_dir.is_dir()
        else []
    )
    if not valid_imgs:
        errors.append("images/ 폴더에 업로드할 유효 이미지 파일이 없습니다.")

    if db_path.is_file():
        with sqlite3.connect(str(db_path)) as conn:
            tbl = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='published_posts'"
            ).fetchone()
            if tbl:
                row = conn.execute(
                    "SELECT published_at, post_url FROM published_posts WHERE run_slug = ?",
                    (run_dir.name,),
                ).fetchone()
                if row:
                    errors.append(
                        f"이미 발행 완료된 프로젝트('{run_dir.name}', {row[0]})입니다. 중복 게시를 차단합니다."
                    )
                if scheduled_auto:
                    kst_date = today_kst or datetime.now(SEOUL).strftime("%Y-%m-%d")
                    daily_row = conn.execute(
                        "SELECT run_slug, published_at FROM published_posts WHERE substr(published_at, 1, 10) = ?",
                        (kst_date,),
                    ).fetchone()
                    if daily_row:
                        errors.append(
                            f"오늘({kst_date}) 이미 발행된 게시물('{daily_row[0]}')이 있어 1일 1회 예약자동발행을 차단합니다."
                        )

    return errors


def handle_stdin_hook() -> int:
    raw = sys.stdin.read().strip()
    if not raw:
        return 0
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    tool_input = payload.get("tool_input") or {}
    command = str(tool_input.get("command") or "")
    if not is_instagram_publish_command(command):
        return 0

    run_dir = extract_run_dir(command)
    if run_dir is None:
        print(
            "[guard_publish BLOCKED] 인스타그램 발행 명령에는 INSTA_PUBLISH_RUN_DIR=\"<실행폴더 절대경로>\"를 지정해야 합니다.",
            file=sys.stderr,
        )
        return 2

    errors = check_run(run_dir, DEFAULT_DB)
    if errors:
        print("[guard_publish BLOCKED] 인스타그램 자동 발행 조건 미충족:", file=sys.stderr)
        for err in errors:
            print(f" - {err}", file=sys.stderr)
        return 2
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Gate 2 physical publish guard")
    ap.add_argument("--check-run", help="Check a specific outputs/<slug> directory directly")
    ap.add_argument("--db", default=str(DEFAULT_DB), help="SQLite DB path override")
    ap.add_argument("--today", help="Override KST YYYY-MM-DD for testing daily rate limit")
    args = ap.parse_args(argv)

    if args.check_run:
        errors = check_run(Path(args.check_run), Path(args.db), today_kst=args.today)
        out = {"allowed": len(errors) == 0, "errors": errors}
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0 if not errors else 2

    return handle_stdin_hook()


if __name__ == "__main__":
    raise SystemExit(main())
