#!/bin/bash
# shark-scout.sh — persistent Shark scout runner (launchd-driven, no session needed).
# SCOUT ONLY: scans + checks inbox + reports. NEVER sends messages (S3). Full
# autonomous negotiation = burner account + "go autonomous", post-van-sale + NYC.
#
# HONEST CAVEATS (read before enabling):
#  - Each run invokes `claude -p` headless = spends API tokens. 4×/day = ~120 runs/mo.
#  - Whether headless `claude -p` can drive the claude-in-chrome extension is
#    UNVERIFIED — the extension pairs with interactive Chrome. Verify on the first
#    real run at NYC; if it can't drive the browser, fall back to session triggers.
#  - Enable at NYC:  launchctl load ~/Library/LaunchAgents/com.ben.shark-scout.plist
#    Disable:        launchctl unload ~/Library/LaunchAgents/com.ben.shark-scout.plist

export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
DIR="$HOME/fb-marketplace-shark"
LOG="$DIR/scout.log"
ts() { date "+%Y-%m-%d %H:%M:%S"; }

# --health: verify plumbing without spending tokens or running a scan.
if [ "$1" = "--health" ]; then
  echo "[$(ts)] health: claude=$(command -v claude || echo MISSING) chrome=$([ -d '/Applications/Google Chrome.app' ] && echo ok || echo MISSING) deals=$([ -f "$DIR/deals.json" ] && echo ok || echo MISSING)"
  exit 0
fi

echo "[$(ts)] scout run starting" >> "$LOG"
# ensure Chrome is up (the extension needs it)
open -ga "Google Chrome" 2>/dev/null
sleep 3

PROMPT='SHARK SCOUT (scan + inbox-check, NO sends — S3 lists-only). Follow ~/obsidian-vault/projects/fb-marketplace-shark/AUTONOMY-SPEC.md + CONTEXT.md. Scan priority categories (P0 golf local, P1 Apple incl. latest MacBook Pro want), score vs eBay-SOLD comp + walk math, capture listing_url+thumbnail via extract.js, stage to deals.json. Check FB Messenger inbox for replies on active negotiations and REPORT them. DO NOT send any message, DO NOT click Buy/Pay. Then: from ~/fb-marketplace-shark git add/commit/push deals.json, and run notify.py --deals. If Chrome not logged in or extension not connected, log it and stop. Two failures on any step = stop.'

claude -p "$PROMPT" >> "$LOG" 2>&1
echo "[$(ts)] scout run finished (exit $?)" >> "$LOG"
