#!/usr/bin/env python3
"""comp.py — eBay SOLD-comp helper for the Marketplace Shark.

Computes the median resale value R from a set of eBay SOLD prices (median resists
outlier drag, per research). Two ways to feed it prices:

  1. BROWSER (works today, low-ban): during a shark session Claude navigates
     eBay sold-search in real Chrome, grabs the page text, and calls
     parse_prices() + median_comp() here. Server-side urllib is BLOCKED by eBay
     (HTTP 403), so the automated fetch below is best-effort only.

  2. eBay API (upgrade): apply for eBay Marketplace Insights API access
     (sold-item data) → set EBAY_APP_ID, wire an authed call into fetch_sold().

Usage:
    python3 comp.py "PXG 0811 driver"          # tries fetch, may 403
    echo "$PAGE_TEXT" | python3 comp.py --stdin # parse prices from piped text
"""
import sys, re, json, statistics, urllib.request, urllib.parse

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

def parse_prices(text):
    """Pull $ prices from eBay sold-search text/HTML. Returns sorted floats >= $2."""
    prices = []
    for m in re.finditer(r'\$([\d,]+\.\d{2})', text):
        try:
            p = float(m.group(1).replace(",", ""))
            if p >= 2:
                prices.append(p)
        except ValueError:
            pass
    return sorted(prices)

def median_comp(prices):
    """Median R with top/bottom 10% trimmed for stability. Returns dict."""
    if not prices:
        return {"count": 0, "median": None}
    k = max(0, len(prices) // 10)
    core = prices[k: len(prices) - k] or prices
    return {"count": len(prices), "median": round(statistics.median(core)),
            "low": round(min(prices)), "high": round(max(prices)),
            "sample": [round(p) for p in prices[:8]]}

def fetch_sold(query):
    """Best-effort server-side fetch. eBay usually returns 403 — use the browser path."""
    q = urllib.parse.quote(query)
    url = (f"https://www.ebay.com/sch/i.html?_nkw={q}&LH_Sold=1&LH_Complete=1&_ipg=120")
    req = urllib.request.Request(url, headers={"User-Agent": UA,
          "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", "ignore")

def report(res, query=""):
    if res.get("median") is None:
        return f'{query}: no comps parsed.'
    return (f'{query}: median R ${res["median"]} '
            f'(range ${res["low"]}-${res["high"]}, n={res["count"]})')

if __name__ == "__main__":
    if "--stdin" in sys.argv:
        res = median_comp(parse_prices(sys.stdin.read()))
        print(json.dumps(res) if "--json" in sys.argv else report(res, "stdin"))
        sys.exit(0)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print('usage: python3 comp.py "item query"  |  ... --stdin'); sys.exit(1)
    query = " ".join(args)
    try:
        res = median_comp(parse_prices(fetch_sold(query)))
        print(json.dumps(res, indent=2) if "--json" in sys.argv else report(res, query))
    except Exception as e:
        print(f'[comp] server-side fetch blocked ({type(e).__name__}: {e}).')
        print('[comp] Use the BROWSER path: in a shark session, navigate eBay '
              'sold-search in Chrome, pipe the page text to `comp.py --stdin`.')
        sys.exit(2)
