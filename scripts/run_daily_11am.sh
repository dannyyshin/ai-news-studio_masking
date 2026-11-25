#!/usr/bin/env bash
# Daily 11:00 AM KST runner for Claude Code CLI (standalone cron / launchd helper)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:$PATH"
cd "$ROOT"

mkdir -p "$ROOT/outputs/cron-logs"
LOG="$ROOT/outputs/cron-logs/daily_$(date +%Y%m%d_%H%M%S).log"

if ! command -v claude >/dev/null 2>&1; then
  echo "[ERROR] claude CLI not found in PATH" | tee -a "$LOG"
  exit 1
fi

claude -p "/ai-news-studio --scheduled-auto: 오늘 날짜 기준 최근 72시간 내 미발행 AI 뉴스 1건을 선정해 @your_instagram_id 톤 A 카드뉴스 5장(3:4)을 제작하고, 무결점 QC 통과 시 Gate 2를 예약자동승인으로 기록해 인스타그램(@your_instagram_id) 공유까지 완료하라. 로그인/2FA 필요 시 절대 우회하지 말고 중단 보고하라." \
  2>&1 | tee -a "$LOG"
