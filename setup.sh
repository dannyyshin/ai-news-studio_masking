#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:$PATH"

echo "[1/4] Python 버전 확인..."
python3 --version

echo "[2/4] JSON 설정 파일 문법 검증..."
python3 - <<PY
import json
from pathlib import Path
for p in [
    Path("$ROOT/config/studio.json"),
    Path("$ROOT/.claude/settings.json"),
]:
    json.loads(p.read_text(encoding="utf-8"))
    print("  OK:", p.relative_to("$ROOT"))
PY

echo "[3/4] SQLite DB 초기화 (data/studio.db)..."
python3 "$ROOT/.claude/skills/ai-news-collect/scripts/dedup_store.py" \
  --db "$ROOT/data/studio.db" init

echo "[4/4] ego-browser CLI 확인..."
if command -v ego-browser >/dev/null 2>&1; then
  ego-browser --version
else
  echo "  [주의] ego-browser가 PATH에 없습니다. ~/.local/bin 확인이 필요합니다."
fi

echo "[완료] ai-news-studio 준비가 끝났습니다."
