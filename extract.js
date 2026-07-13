// extract.js — FB Marketplace search-result extractor for the Shark scout.
//
// Run via the Chrome javascript_tool during a scan (paste this into the page
// context on a marketplace search results page). Returns structured listings
// WITH listing_url + thumbnail so the scout can populate deals.json cards
// (clickable links + images) instead of text-only.
//
// Filters out notification-panel links and non-listing junk: a real search card
// has both a thumbnail <img> and a "$price" line.
(() => {
  const seen = new Set(), out = [];
  document.querySelectorAll('a[href*="/marketplace/item/"]').forEach(a => {
    const m = a.href.match(/\/marketplace\/item\/(\d+)/);
    if (!m || seen.has(m[1])) return;
    const img = a.querySelector('img');
    const lines = a.innerText.split('\n').map(s => s.trim()).filter(Boolean);
    const priceLine = lines.find(l => /^\$[\d,]+/.test(l));
    if (!img || !priceLine) return;            // skip notifications / non-cards
    seen.add(m[1]);
    const title = lines[lines.indexOf(priceLine) + 1]
      || lines.find(l => l !== priceLine && l !== 'Just listed') || '';
    const loc = lines[lines.length - 1] !== title ? lines[lines.length - 1] : '';
    out.push({
      id: m[1],
      url: 'https://www.facebook.com/marketplace/item/' + m[1] + '/',
      thumbnail: img.src,
      price: priceLine,
      title,
      location: loc
    });
  });
  return out;   // -> map into deals.json: listing_url=url, thumbnail=thumbnail
})()
