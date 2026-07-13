#!/usr/bin/env python3
"""notify.py — local alert for the Marketplace Shark.

Fires a native macOS notification when the scout stages a deal that clears the
score threshold, so Ben only looks when there's a live winner. Keyless + no ban
risk (local only). Telegram/push is an optional upgrade (needs a bot token — see
--telegram stub).

Usage:
    python3 notify.py "2 new deals cleared" "Opus wedges $195 · PXG driver $175"
    python3 notify.py --deals            # summarize awaiting/new deals from deals.json
"""
import sys, json, subprocess, os

HERE = os.path.dirname(os.path.abspath(__file__))
CRM = "https://benjchapman3-cmd.github.io/fb-marketplace-shark/"

def mac_notify(title, message):
    # osascript = native macOS notification. Escape double-quotes.
    t = title.replace('"', '\\"'); m = message.replace('"', '\\"')
    subprocess.run(["osascript", "-e",
        f'display notification "{m}" with title "🦈 {t}" sound name "Ping"'],
        check=False)

def deals_summary():
    try:
        with open(os.path.join(HERE, "deals.json")) as f:
            data = json.load(f)
    except Exception as e:
        return "Shark", f"deals.json unreadable: {e}"
    fresh = [d for d in data.get("deals", [])
             if d.get("stage") in ("identified", "reached-out", "negotiating")]
    live_buy = [d for d in fresh if str(d.get("verdict", "")).lower()
                .startswith(("buy", "deal", "flip"))]
    if not live_buy:
        return "Scan done — no new winners", "Nothing cleared the bar this pass."
    top = ", ".join(f'{d["title"][:28]} ${d.get("ask","?")}' for d in live_buy[:3])
    return f'{len(live_buy)} live deal(s)', f'{top} · open {CRM}'

if __name__ == "__main__":
    if "--deals" in sys.argv:
        title, msg = deals_summary()
    else:
        args = [a for a in sys.argv[1:] if not a.startswith("--")]
        title = args[0] if args else "Shark alert"
        msg = args[1] if len(args) > 1 else ""
    mac_notify(title, msg)
    print(f'notified: {title} — {msg}')
