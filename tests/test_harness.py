"""Offline unit tests for ai-news-studio Python harness components."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEDUP_SCRIPT = ROOT / ".claude/skills/ai-news-collect/scripts/dedup_store.py"
VALIDATOR_SCRIPT = ROOT / ".claude/skills/news-fact-qc/scripts/validate_contract.py"
GUARD_SCRIPT = ROOT / ".claude/hooks/guard_publish.py"
AUDIT_SCRIPT = ROOT / ".claude/skills/publish-confirm/scripts/verify_published_payload.py"


class TestHarness(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_dir = Path(self.tmp.name)
        self.db_path = self.tmp_dir / "test_studio.db"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def run_py(self, script: Path, args: list[str], stdin_text: str | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(script), *args],
            input=stdin_text,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_dedup_store_lifecycle(self) -> None:
        r_init = self.run_py(DEDUP_SCRIPT, ["--db", str(self.db_path), "init"])
        self.assertEqual(r_init.returncode, 0, r_init.stderr)

        r_chk1 = self.run_py(
            DEDUP_SCRIPT,
            ["--db", str(self.db_path), "check-news", "--url", "https://example.com/a", "--title", "OpenAI GPT-5 출시"],
        )
        self.assertFalse(json.loads(r_chk1.stdout)["duplicate"])

        r_rec = self.run_py(
            DEDUP_SCRIPT,
            [
                "--db", str(self.db_path),
                "record-news",
                "--url", "https://example.com/a",
                "--title", "OpenAI GPT-5 출시",
                "--company", "OpenAI",
                "--published-at", "2026-11-24",
            ],
        )
        self.assertEqual(r_rec.returncode, 0)

        # Same title with spacing difference should be detected as duplicate
        r_chk2 = self.run_py(
            DEDUP_SCRIPT,
            ["--db", str(self.db_path), "check-news", "--url", "https://other.test/b", "--title", "OpenAI GPT5 출시!"],
        )
        self.assertTrue(json.loads(r_chk2.stdout)["duplicate"])

        # Idempotent publishing check + layout tracking
        self.run_py(DEDUP_SCRIPT, ["--db", str(self.db_path), "start-run", "--slug", "20261125-test", "--format", "webtoon"])
        r_pub1 = self.run_py(
            DEDUP_SCRIPT,
            [
                "--db", str(self.db_path),
                "mark-published",
                "--slug", "20261125-test",
                "--format", "webtoon",
                "--layout", "L1",
                "--post-url", "https://instagram.com/p/123",
            ],
        )
        self.assertEqual(r_pub1.returncode, 0)
        r_pub2 = self.run_py(
            DEDUP_SCRIPT,
            ["--db", str(self.db_path), "mark-published", "--slug", "20261125-test"],
        )
        self.assertNotEqual(r_pub2.returncode, 0)

        r_lay = self.run_py(DEDUP_SCRIPT, ["--db", str(self.db_path), "last-layout", "--format", "webtoon"])
        self.assertEqual(r_lay.returncode, 0, r_lay.stderr)
        lay_data = json.loads(r_lay.stdout)
        self.assertEqual(lay_data["last_layout"], "L1")
        self.assertNotIn("L1", lay_data["available"])
        self.assertIn("L2", lay_data["available"])

    def test_validator_accepts_valid_and_rejects_broken(self) -> None:
        r_ok = self.run_py(
            VALIDATOR_SCRIPT,
            [
                "--brief", str(ROOT / "samples/sample_news_brief.md"),
                "--content", str(ROOT / "samples/valid_content.md"),
                "--format", "cardnews",
                "--today", "2026-11-25",
            ],
        )
        self.assertEqual(r_ok.returncode, 0, r_ok.stdout)
        self.assertTrue(json.loads(r_ok.stdout)["passed"])

        r_bad = self.run_py(
            VALIDATOR_SCRIPT,
            [
                "--brief", str(ROOT / "samples/sample_news_brief.md"),
                "--content", str(ROOT / "samples/broken_content.md"),
                "--format", "cardnews",
                "--today", "2026-11-25",
            ],
        )
        self.assertEqual(r_bad.returncode, 1)
        data = json.loads(r_bad.stdout)
        joined = "\n".join(data["issues"])
        self.assertIn("5~6컷", joined)
        self.assertIn("14자 이하", joined)
        self.assertIn("24자 이하", joined)
        self.assertIn("3:4", joined)

    def test_high_density_instatoon_validation(self) -> None:
        r_ok = self.run_py(
            VALIDATOR_SCRIPT,
            [
                "--brief", str(ROOT / "samples/sample_news_brief.md"),
                "--content", str(ROOT / "samples/valid_instatoon_b.md"),
                "--format", "webtoon",
                "--today", "2026-11-25",
            ],
        )
        self.assertEqual(r_ok.returncode, 0, r_ok.stdout)
        data = json.loads(r_ok.stdout)
        self.assertTrue(data["passed"])
        self.assertEqual(data["layouts"], ["L1"])

    def test_layout_diversity_rules(self) -> None:
        base_text = (ROOT / "samples/valid_content.md").read_text(encoding="utf-8")

        # 1. Monotonous L1 x 5 must be rejected
        mono_text = base_text
        for code in ("L6", "L3", "L4", "L2"):
            mono_text = mono_text.replace(f"- 레이아웃: {code}", "- 레이아웃: L1")
        mono_path = self.tmp_dir / "mono_content.md"
        mono_path.write_text(mono_text, encoding="utf-8")
        r_mono = self.run_py(
            VALIDATOR_SCRIPT,
            [
                "--brief", str(ROOT / "samples/sample_news_brief.md"),
                "--content", str(mono_path),
                "--format", "cardnews",
                "--today", "2026-11-25",
            ],
        )
        self.assertEqual(r_mono.returncode, 1)
        mono_issues = "\n".join(json.loads(r_mono.stdout)["issues"])
        self.assertIn("다양성 부족", mono_issues)
        self.assertIn("연속된 컷", mono_issues)

        # 2. Adjacent duplicate (L6, L2, L2, L4, L1) has 4 distinct layouts but still fails adjacent rule
        adj_text = base_text.replace("- 레이아웃: L3", "- 레이아웃: L2").replace("- 레이아웃: L4", "- 레이아웃: L2", 1)
        # Ensure L6 -> L2 -> L2 -> L4 -> L1
        adj_lines = []
        seq = iter(["L6", "L2", "L2", "L4", "L1"])
        for line in base_text.splitlines():
            if line.startswith("- 레이아웃: "):
                adj_lines.append(f"- 레이아웃: {next(seq)}")
            else:
                adj_lines.append(line)
        adj_path = self.tmp_dir / "adj_content.md"
        adj_path.write_text("\n".join(adj_lines), encoding="utf-8")
        r_adj = self.run_py(
            VALIDATOR_SCRIPT,
            [
                "--brief", str(ROOT / "samples/sample_news_brief.md"),
                "--content", str(adj_path),
                "--format", "cardnews",
                "--today", "2026-11-25",
            ],
        )
        self.assertEqual(r_adj.returncode, 1)
        adj_issues = "\n".join(json.loads(r_adj.stdout)["issues"])
        self.assertIn("연속된 컷", adj_issues)

    def test_verify_published_payload_catches_missing_caption_and_errors(self) -> None:
        content_file = ROOT / "samples/valid_content.md"
        live_json = self.tmp_dir / "live.json"

        # 1. Valid cardnews carousel post passes
        live_json.write_text(
            json.dumps({
                "url": "https://www.instagram.com/your_instagram_id/p/TestOk123/",
                "title": "Instagram",
                "author": "your_instagram_id",
                "articleText": "your_instagram_id 오늘 AI 업계 난리 난 이유 30초 정리 👇 클로드 코드 #AI뉴스 #클로드 #업무자동화 #AI에이전트 #AI큐레이션 #일잘러",
                "metaDesc": "",
                "imageCount": 5,
                "hasCarouselNext": True,
            }, ensure_ascii=False),
            encoding="utf-8",
        )
        r_pass = self.run_py(AUDIT_SCRIPT, ["--content", str(content_file), "--live-json", str(live_json), "--format", "cardnews"])
        self.assertEqual(r_pass.returncode, 0, r_pass.stdout)
        self.assertEqual(json.loads(r_pass.stdout)["status"], "PASS")

        # 2. Missing caption (reproducing TestMissingCap bug) triggers ALERT_CAPTION_MISSING
        live_json.write_text(
            json.dumps({
                "url": "https://www.instagram.com/your_instagram_id/p/TestMissingCap/",
                "title": "Instagram",
                "author": "your_instagram_id",
                "articleText": "your_instagram_id\n아직 댓글이 없습니다.\n댓글을 남겨보세요.\n인사이트 보기\n게시물 홍보하기",
                "metaDesc": "",
                "imageCount": 1,
                "hasCarouselNext": True,
            }, ensure_ascii=False),
            encoding="utf-8",
        )
        r_cap = self.run_py(AUDIT_SCRIPT, ["--content", str(content_file), "--live-json", str(live_json), "--format", "cardnews"])
        self.assertEqual(r_cap.returncode, 1)
        self.assertEqual(json.loads(r_cap.stdout)["status"], "ALERT_CAPTION_MISSING")

        # 3. Single image uploaded instead of cardnews carousel triggers ALERT_SLIDE_MISMATCH
        live_json.write_text(
            json.dumps({
                "url": "https://www.instagram.com/your_instagram_id/p/TestSingle/",
                "title": "Instagram",
                "author": "your_instagram_id",
                "articleText": "your_instagram_id 오늘 AI 업계 난리 난 이유 30초 정리 👇 #AI뉴스 #클로드 #업무자동화 #AI에이전트 #AI큐레이션 #일잘러",
                "metaDesc": "",
                "imageCount": 1,
                "hasCarouselNext": False,
            }, ensure_ascii=False),
            encoding="utf-8",
        )
        r_slide = self.run_py(AUDIT_SCRIPT, ["--content", str(content_file), "--live-json", str(live_json), "--format", "cardnews"])
        self.assertEqual(r_slide.returncode, 1)
        self.assertEqual(json.loads(r_slide.stdout)["status"], "ALERT_SLIDE_MISMATCH")

        # 4. Deleted/Error page triggers ALERT_PAGE_ERROR
        live_json.write_text(
            json.dumps({
                "url": "https://www.instagram.com/your_instagram_id/p/Missing/",
                "title": "Error",
                "author": "",
                "articleText": "",
                "metaDesc": "",
                "imageCount": 0,
                "hasCarouselNext": False,
            }, ensure_ascii=False),
            encoding="utf-8",
        )
        r_err = self.run_py(AUDIT_SCRIPT, ["--content", str(content_file), "--live-json", str(live_json), "--format", "cardnews"])
        self.assertEqual(r_err.returncode, 1)
        self.assertEqual(json.loads(r_err.stdout)["status"], "ALERT_PAGE_ERROR")

    def _make_run_dir(
        self,
        name: str,
        *,
        decision: str = "승인",
        fail_count: int = 0,
        with_image: bool = True,
        with_image_qc: bool = True,
        image_qc_fail: bool = False,
    ) -> Path:
        run_dir = self.tmp_dir / name
        (run_dir / "images").mkdir(parents=True, exist_ok=True)
        (run_dir / "02_content.md").write_text(
            (ROOT / "samples/valid_content.md").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        (run_dir / "03_qc_report.md").write_text(
            f"# QC\n- 논리: PASS: 7 / WARN: 0 / FAIL: {fail_count}\n- 팩트: MATCH: 2 / PARTIAL: 0 / MISMATCH: 0\n",
            encoding="utf-8",
        )
        (run_dir / "05_gate2_publish.md").write_text(
            f"# Gate 2\n- 결정: {decision}\n- 예외 승인: 아니오\n- 결정 시각: 2026-11-25 11:00\n",
            encoding="utf-8",
        )
        if with_image_qc:
            verdict = "FAIL" if image_qc_fail else "PASS"
            (run_dir / "05_image_qc.md").write_text(f"# Image QC\n| 1 | card_01.png | {verdict} |\n", encoding="utf-8")
        if with_image:
            (run_dir / "images/card_01.png").write_bytes(b"\x89PNG\r\n\x1a\nfake")
        return run_dir

    def test_guard_publish_cli_and_hook(self) -> None:
        # 1. Valid run passes
        ok_dir = self._make_run_dir("20261125-ok", decision="승인", fail_count=0, with_image=True)
        r_ok = self.run_py(GUARD_SCRIPT, ["--check-run", str(ok_dir), "--db", str(self.db_path)])
        self.assertEqual(r_ok.returncode, 0, r_ok.stdout)

        # 2. Unapproved Gate 2 blocks
        bad_gate = self._make_run_dir("20261125-badgate", decision="대기")
        r_gate = self.run_py(GUARD_SCRIPT, ["--check-run", str(bad_gate), "--db", str(self.db_path)])
        self.assertEqual(r_gate.returncode, 2)

        # 3. Unresolved QC FAIL blocks
        bad_qc = self._make_run_dir("20261125-badqc", decision="승인", fail_count=1)
        r_qc = self.run_py(GUARD_SCRIPT, ["--check-run", str(bad_qc), "--db", str(self.db_path)])
        self.assertEqual(r_qc.returncode, 2)

        # 4. Missing images blocks
        no_img = self._make_run_dir("20261125-noimg", decision="승인", with_image=False)
        r_img = self.run_py(GUARD_SCRIPT, ["--check-run", str(no_img), "--db", str(self.db_path)])
        self.assertEqual(r_img.returncode, 2)

        # 5. Scheduled auto-approve passes when zero-defect and no post today
        sched_ok = self._make_run_dir("20261125-sched-ok", decision="예약자동승인")
        r_sched_ok = self.run_py(GUARD_SCRIPT, ["--check-run", str(sched_ok), "--db", str(self.db_path), "--today", "2026-11-26"])
        self.assertEqual(r_sched_ok.returncode, 0, r_sched_ok.stdout)

        # 6. Scheduled auto-approve blocks when 05_image_qc.md is missing or FAIL
        sched_no_iqc = self._make_run_dir("20261125-sched-noiqc", decision="예약자동승인", with_image_qc=False)
        self.assertEqual(self.run_py(GUARD_SCRIPT, ["--check-run", str(sched_no_iqc), "--db", str(self.db_path), "--today", "2026-11-26"]).returncode, 2)
        sched_fail_iqc = self._make_run_dir("20261125-sched-failiqc", decision="예약자동승인", image_qc_fail=True)
        self.assertEqual(self.run_py(GUARD_SCRIPT, ["--check-run", str(sched_fail_iqc), "--db", str(self.db_path), "--today", "2026-11-26"]).returncode, 2)

        # 7. PreToolUse stdin mode: non-instagram command passes untouched
        hook_other = json.dumps({"tool_name": "Bash", "tool_input": {"command": "ego-browser nodejs -e 'console.log(1)'"}})
        r_other = self.run_py(GUARD_SCRIPT, [], stdin_text=hook_other)
        self.assertEqual(r_other.returncode, 0)

        # 8. PreToolUse stdin mode: instagram command without INSTA_PUBLISH_RUN_DIR blocks
        hook_missing_env = json.dumps({
            "tool_name": "Bash",
            "tool_input": {"command": "ego-browser nodejs -e 'page.goto(\"https://instagram.com\"); page.click(\"공유하기\")'"},
        })
        r_missing = self.run_py(GUARD_SCRIPT, [], stdin_text=hook_missing_env)
        self.assertEqual(r_missing.returncode, 2)

        # 9. PreToolUse stdin mode: approved run passes
        hook_ok = json.dumps({
            "tool_name": "Bash",
            "tool_input": {"command": f'INSTA_PUBLISH_RUN_DIR="{ok_dir}" ego-browser nodejs <<EOF\nEOF'},
        })
        r_hook_ok = self.run_py(GUARD_SCRIPT, [], stdin_text=hook_ok)
        self.assertEqual(r_hook_ok.returncode, 0, r_hook_ok.stderr)

        # 10. Already published in SQLite blocks same slug & blocks scheduled_auto on same day
        self.run_py(DEDUP_SCRIPT, ["--db", str(self.db_path), "init"])
        self.run_py(DEDUP_SCRIPT, ["--db", str(self.db_path), "mark-published", "--slug", ok_dir.name])
        r_dup = self.run_py(GUARD_SCRIPT, ["--check-run", str(ok_dir), "--db", str(self.db_path)])
        self.assertEqual(r_dup.returncode, 2)
        # Same-day rate limit check for scheduled_auto (today_date extracted from ok_dir's published_at)
        r_daily_cap = self.run_py(GUARD_SCRIPT, ["--check-run", str(sched_ok), "--db", str(self.db_path)])
        self.assertEqual(r_daily_cap.returncode, 2)


if __name__ == "__main__":
    unittest.main()
