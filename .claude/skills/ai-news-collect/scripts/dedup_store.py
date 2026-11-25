#!/usr/bin/env python3
"""SQLite memory store for AI News Studio (@your_instagram_id).

Manages 30-day news deduplication, execution runs, and idempotent Instagram publishing.
Uses only Python standard library (sqlite3, hashlib, argparse, json).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

SEOUL = timezone(timedelta(hours=9), name="KST")
DEFAULT_DB = Path(__file__).resolve().parents[4] / "data" / "studio.db"


def now_iso() -> str:
    return datetime.now(SEOUL).isoformat(timespec="seconds")


def normalize_title(title: str) -> str:
    """Normalize title for near-duplicate hashing (alnum + Korean syllables only)."""
    return "".join(ch for ch in title.lower() if ch.isalnum())


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def connect_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS collected_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            url_hash TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            title_hash TEXT NOT NULL,
            company TEXT DEFAULT '',
            published_at TEXT DEFAULT '',
            collected_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_collected_title_hash
            ON collected_news(title_hash);

        CREATE TABLE IF NOT EXISTS runs (
            slug TEXT PRIMARY KEY,
            format TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS published_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_slug TEXT NOT NULL UNIQUE,
            instagram_username TEXT NOT NULL,
            post_url TEXT DEFAULT '',
            format TEXT NOT NULL,
            topic TEXT DEFAULT '',
            layout_id TEXT DEFAULT '',
            published_at TEXT NOT NULL
        );
        """
    )
    cols = {row["name"] for row in conn.execute("PRAGMA table_info(published_posts)").fetchall()}
    if "layout_id" not in cols:
        conn.execute("ALTER TABLE published_posts ADD COLUMN layout_id TEXT DEFAULT ''")
    conn.commit()


def cmd_init(args: argparse.Namespace) -> int:
    db_path = Path(args.db)
    with connect_db(db_path) as conn:
        init_schema(conn)
    print(json.dumps({"ok": True, "db": str(db_path)}, ensure_ascii=False))
    return 0


def cmd_check_news(args: argparse.Namespace) -> int:
    db_path = Path(args.db)
    url = args.url.strip()
    title = args.title.strip()
    url_h = sha256_text(url)
    title_h = sha256_text(normalize_title(title))
    cutoff = (datetime.now(SEOUL) - timedelta(days=args.days)).isoformat(timespec="seconds")

    with connect_db(db_path) as conn:
        init_schema(conn)
        rows = conn.execute(
            """
            SELECT url, title, company, published_at, collected_at
            FROM collected_news
            WHERE (url_hash = ? OR title_hash = ?) AND collected_at >= ?
            ORDER BY collected_at DESC
            """,
            (url_h, title_h, cutoff),
        ).fetchall()

    matches = [dict(r) for r in rows]
    result = {
        "duplicate": len(matches) > 0,
        "days": args.days,
        "matches": matches,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_record_news(args: argparse.Namespace) -> int:
    db_path = Path(args.db)
    url = args.url.strip()
    title = args.title.strip()
    url_h = sha256_text(url)
    title_h = sha256_text(normalize_title(title))
    ts = now_iso()

    with connect_db(db_path) as conn:
        init_schema(conn)
        conn.execute(
            """
            INSERT INTO collected_news (url, url_hash, title, title_hash, company, published_at, collected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(url_hash) DO UPDATE SET
                title = excluded.title,
                title_hash = excluded.title_hash,
                company = excluded.company,
                published_at = excluded.published_at,
                collected_at = excluded.collected_at
            """,
            (url, url_h, title, title_h, args.company.strip(), args.published_at.strip(), ts),
        )
        conn.commit()
    print(json.dumps({"ok": True, "url": url, "recorded_at": ts}, ensure_ascii=False))
    return 0


def cmd_start_run(args: argparse.Namespace) -> int:
    db_path = Path(args.db)
    ts = now_iso()
    with connect_db(db_path) as conn:
        init_schema(conn)
        conn.execute(
            """
            INSERT INTO runs (slug, format, status, created_at, updated_at)
            VALUES (?, ?, 'started', ?, ?)
            ON CONFLICT(slug) DO UPDATE SET
                format = excluded.format,
                status = 'started',
                updated_at = excluded.updated_at
            """,
            (args.slug.strip(), args.format.strip(), ts, ts),
        )
        conn.commit()
    print(json.dumps({"ok": True, "slug": args.slug, "format": args.format}, ensure_ascii=False))
    return 0


def cmd_is_published(args: argparse.Namespace) -> int:
    db_path = Path(args.db)
    with connect_db(db_path) as conn:
        init_schema(conn)
        row = conn.execute(
            "SELECT * FROM published_posts WHERE run_slug = ?",
            (args.slug.strip(),),
        ).fetchone()
    out = {"published": row is not None, "record": dict(row) if row else None}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def cmd_mark_published(args: argparse.Namespace) -> int:
    db_path = Path(args.db)
    ts = now_iso()
    slug = args.slug.strip()
    with connect_db(db_path) as conn:
        init_schema(conn)
        existing = conn.execute(
            "SELECT id FROM published_posts WHERE run_slug = ?", (slug,)
        ).fetchone()
        if existing:
            print(
                json.dumps(
                    {"ok": False, "error": f"Run '{slug}' is already marked as published."},
                    ensure_ascii=False,
                ),
                file=sys.stderr,
            )
            return 1
        conn.execute(
            """
            INSERT INTO published_posts (run_slug, instagram_username, post_url, format, topic, layout_id, published_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                slug,
                args.username.strip(),
                args.post_url.strip(),
                args.format.strip(),
                args.topic.strip(),
                args.layout.strip(),
                ts,
            ),
        )
        conn.execute(
            "UPDATE runs SET status = 'published', updated_at = ? WHERE slug = ?",
            (ts, slug),
        )
        conn.commit()
    print(json.dumps({"ok": True, "slug": slug, "layout": args.layout.strip(), "published_at": ts}, ensure_ascii=False))
    return 0


def cmd_last_layout(args: argparse.Namespace) -> int:
    db_path = Path(args.db)
    all_layouts = ["L1", "L2", "L3", "L4", "L5", "L6"]
    with connect_db(db_path) as conn:
        init_schema(conn)
        if args.format:
            rows = conn.execute(
                """
                SELECT run_slug, format, layout_id, published_at
                FROM published_posts
                WHERE layout_id != '' AND format = ?
                ORDER BY published_at DESC LIMIT ?
                """,
                (args.format.strip(), args.limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT run_slug, format, layout_id, published_at
                FROM published_posts
                WHERE layout_id != ''
                ORDER BY published_at DESC LIMIT ?
                """,
                (args.limit,),
            ).fetchall()

    recent = [dict(r) for r in rows]
    last_layout = recent[0]["layout_id"] if recent else ""
    avoid = [last_layout] if last_layout in all_layouts else []
    available = [l for l in all_layouts if l not in avoid]
    out = {
        "last_layout": last_layout,
        "avoid": avoid,
        "available": available,
        "recent": recent,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def cmd_history(args: argparse.Namespace) -> int:
    db_path = Path(args.db)
    with connect_db(db_path) as conn:
        init_schema(conn)
        posts = [
            dict(r)
            for r in conn.execute(
                "SELECT * FROM published_posts ORDER BY published_at DESC LIMIT ?",
                (args.limit,),
            ).fetchall()
        ]
        news = [
            dict(r)
            for r in conn.execute(
                "SELECT title, company, published_at, url, collected_at FROM collected_news ORDER BY collected_at DESC LIMIT ?",
                (args.limit,),
            ).fetchall()
        ]
    print(json.dumps({"published_posts": posts, "recent_news": news}, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="SQLite deduplication & publish memory store")
    ap.add_argument("--db", default=str(DEFAULT_DB), help="SQLite DB file path")
    sub = ap.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Initialize SQLite schema")
    p_init.set_defaults(func=cmd_init)

    p_chk = sub.add_parser("check-news", help="Check if URL or normalized title exists in last N days")
    p_chk.add_argument("--url", required=True)
    p_chk.add_argument("--title", required=True)
    p_chk.add_argument("--days", type=int, default=30)
    p_chk.set_defaults(func=cmd_check_news)

    p_rec = sub.add_parser("record-news", help="Record collected news item")
    p_rec.add_argument("--url", required=True)
    p_rec.add_argument("--title", required=True)
    p_rec.add_argument("--company", default="")
    p_rec.add_argument("--published-at", default="")
    p_rec.set_defaults(func=cmd_record_news)

    p_run = sub.add_parser("start-run", help="Register a pipeline run")
    p_run.add_argument("--slug", required=True)
    p_run.add_argument("--format", default="cardnews")
    p_run.set_defaults(func=cmd_start_run)

    p_ispub = sub.add_parser("is-published", help="Check if run_slug is already published")
    p_ispub.add_argument("--slug", required=True)
    p_ispub.set_defaults(func=cmd_is_published)

    p_pub = sub.add_parser("mark-published", help="Mark run_slug as published (idempotent)")
    p_pub.add_argument("--slug", required=True)
    p_pub.add_argument("--username", default="your_instagram_id")
    p_pub.add_argument("--post-url", default="")
    p_pub.add_argument("--format", default="cardnews")
    p_pub.add_argument("--topic", default="")
    p_pub.add_argument("--layout", default="", help="Layout code or sequence (e.g. L1 or L6,L3,L2,L5,L1)")
    p_pub.set_defaults(func=cmd_mark_published)

    p_lay = sub.add_parser("last-layout", help="Show most recently published layout(s) to avoid repetition")
    p_lay.add_argument("--format", default="", help="Optional format filter (cardnews / webtoon / both)")
    p_lay.add_argument("--limit", type=int, default=5)
    p_lay.set_defaults(func=cmd_last_layout)

    p_hist = sub.add_parser("history", help="Show recent news and published posts")
    p_hist.add_argument("--limit", type=int, default=10)
    p_hist.set_defaults(func=cmd_history)
    return ap


def main(argv: list[str] | None = None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
