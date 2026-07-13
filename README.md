# 🦈 Marketplace Shark

An autonomous deal desk for Facebook Marketplace. It hunts, scores, drafts, and plans negotiations for the things Ben wants — and only pulls Ben in to green-light first contact + final purchase.

## How to use
- **Open the app:** double-click `dashboard.html` (or run `./start.command`).
- **Run a scan:** in a Claude session, say **"run the shark"** (optionally a category), then **"go autonomous"** to grant send-within-mandate for that session.
- Deals flow left→right: **Found → Negotiating → Ready to buy.**

## The deal (session-autonomous — locked 2026-07-13)
Autonomy model = **session-autonomous**. Not 24/7 (that's the FB-ban wall — the agent runs on Ben's real account). Full spec: vault `AUTONOMY-SPEC.md`.
- **Automated, no Ben:** discover (local + ship) → score vs comps → **auto-send opener** → **negotiate silently within the mandate** (lowball / counter / hold) → log every move.
- **Ben pulled in ONLY on 4 triggers:** (1) buy-ready, (2) seller counter close-but-over-walk, (3) condition red flag, (4) logistics need him.
- **Never automated:** clicking Buy/Pay, wiring money/deposits, agreeing above the **walk** price, sharing Ben's home address/identity. The money moment always stops for Ben.
- **Session-bound:** runs only inside a session Ben started + granted. No background daemon. Consent re-granted each run.

## Files
- `deals.json` — source-of-truth pipeline record.
- `index.html` — hosted Deal CRM (Kanban + P&L). `dashboard.html` = old, deprecated.
- `comp.py` — eBay sold-comp median. Browser path: navigate eBay sold-search in Chrome, pipe page text → `python3 comp.py --stdin`. (Server fetch 403s; API upgrade needs eBay App ID.)
- `notify.py` — native macOS deal alert. `python3 notify.py --deals` summarizes live winners.
- `extract.js` — Chrome-console snippet: pulls listing_url + thumbnail + price/title per search card (filters notifications). Run via javascript_tool in the Record step.
- `shark.command` — double-click launcher: opens the hosted CRM + prints scan triggers.
- `start.command` — legacy (opens old dashboard.html).

## Automation & cadence (4×/day)
Optimal = **4 runs/day, ~every 3–4h in waking hours** (8:32 / 12:32 / 16:32 / 20:02). More = looks botty + diminishing returns; fewer = lose negotiation momentum. Instant/always-on is NOT possible (no FB push, real-FB automation = ban) and not even desirable (instant = bot signal). Each run = scan + inbox-check + advance + notify.

Three ways it fires:
1. **In-session crons** — fire the 4×/day scan while a Claude session is alive (die when Claude closes).
2. **Persistent launchd runner** (`shark-scout.sh` + `~/Library/LaunchAgents/com.ben.shark-scout.plist`) — fires the 4×/day scan **without a session open**. SCOUT-ONLY (no sends). **Disabled by default** — enable at NYC:
   `launchctl load ~/Library/LaunchAgents/com.ben.shark-scout.plist`
   ⚠️ Each run spends API tokens (`claude -p`). Headless browser-drive is unverified — check the first real run at NYC.
3. **Session trigger** — say **"run the shark"** anytime.

### Full autonomous negotiation (the goal) — post-van-sale + NYC, BURNER account
Ben's target: agent negotiates fully on its own, Ben absent, steps in only for red-flags + final buy. Path: run it on a **burner FB account** (isolates ban risk from the real/van account), enable send-within-mandate on the launchd runner. Async pull-in model = agent negotiates → HOLDS at buy-ready or red-flag → notifies Ben → he confirms whenever (never buys without him). Turns on only AFTER van sells (removes the account-loss stake).

## Tools in the scan loop
- **Score step** → get eBay-SOLD R: in-session Chrome opens `ebay.com/sch/i.html?_nkw=<item>&LH_Sold=1&LH_Complete=1`, grab page text, `comp.py --stdin` → median R for the walk math.
- **Surface step** → `notify.py --deals` fires a Mac notification for live winners (no spamming Ben on dry scans).

## SCAN PROTOCOL (the brain — Claude follows this every run)
1. **Discover.** For each category profile in the vault `CONTEXT.md`, run both passes: LOCAL pickup + `deliveryMethod=shipping`. Sort newest, last 1–7 days.
2. **Filter.** Kill anything below the quality bar (off-brand, beat-up, dated game-improvement). Premium brands + recent models only.
3. **Score.** Personal-priority items first (irons set, putter, 3-wood, wedges, high-spec MacBook). Everything else = flip. Compare ask vs benchmark + pull a live eBay-sold comp for flips. Flag ≤ GOOD.
4. **Draft.** For each hit: write the opener (ask availability + missing specs + condition photos + local/cash) and set the mandate {open ≈ 15–20% under, target, walk = max Ben pays}.
5. **Record.** Update `deals.json`. Capture `listing_url` + `thumbnail` by running **`extract.js`** via the Chrome javascript_tool on the search page (returns {url, thumbnail, price, title, location} per card — clickable + visual CRM). Log `conversation` once negotiating. Set `stage`.
6. **Publish.** From `~/fb-marketplace-shark/`: `git add deals.json && git commit -m "scan <date>" && git push` — this refreshes the hosted CRM (https://benjchapman3-cmd.github.io/fb-marketplace-shark/) so Ben sees it on any device.
7. **Surface.** Move real hits forward and tell Ben ONLY these. Stay silent on noise.

## Deal CRM (hosted)
`index.html` = Kanban deal board reading `deals.json`, hosted on GitHub Pages: **https://benjchapman3-cmd.github.io/fb-marketplace-shark/** (phone-viewable). Columns = pipeline stages; cards show ask/comp/walk/net + verdict; click a card → listing link + mandate + seller conversation. Public repo — data is world-readable to anyone with the URL.

## Safety rails (locked)
- Runs on Ben's real FB (the van-sale account) → human pace, no rapid-fire, no background headless driving.
- Session caps: ≤ 8 active negotiations, ≤ 25 messages/session (anti spam-flag). Claude never exceeds the walk price.
- Claude auto-sends openers + negotiates within mandate; **Buy/Pay + money always route to Ben** (pull-in). Cash on pickup only; shippable via FB buyer-protection checkout only.
- Verify authenticity in person before cash (Scotty Cameron, PXG, watches, Apple gear = check Activation Lock).
