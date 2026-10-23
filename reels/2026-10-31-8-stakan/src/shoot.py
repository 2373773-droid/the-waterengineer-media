"""Full-page mobile screenshots of the real article pages + page-space rects of the phrases to highlight."""
import asyncio, json
from playwright.async_api import async_playwright
PAGES = {
 "pmc": ("https://pmc.ncbi.nlm.nih.gov/articles/PMC9764345/", [
    "Variation in human water turnover associated with environmental and lifestyle factors",
    "5,604 people from the ages of 8 days to 96 years from 26 countries",
    "the low end for men and women is ~1–1.5 L/day while the upper end is around ~6 L/day",
    "has a predicted WT of 3.2 L/d",
    "will have a WT of 2.7 L/d",
    "is not equal to daily water intake from liquids and foods",
    "Athletes have ~1000 ml more WT than do non-athletes",
    "a 50% increase in relative humidity induces a ~300 ml increase in WT",
    "one size does not fit all for drinking water guidelines",
    "the common suggestion that we should drink 8 × 8oz glasses of water per day (approx. 2 L) is not backed by objective evidence"]),
 "dart": ("https://geiselmed.dartmouth.edu/news/2002_h2/08aug2002_water.shtml", [
    "Dartmouth Professor Finds No Scientific Evidence for '8 x 8'",
    "He found no scientific studies in support of 8 x 8.",
    "caffeinated drinks, such as most coffee, tea and soft drinks, may indeed be counted toward the daily total",
    "thirst begins when the concentration of blood (an accurate indicator of our state of hydration) has risen by less than two percent"]),
}
JS = """(phr) => {
  const out = {};
  const walker = () => document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  // build one flat string of all text nodes to allow phrases that span nodes
  const nodes = []; let s = ''; const w = walker(); let n;
  while ((n = w.nextNode())) { nodes.push([n, s.length]); s += n.nodeValue; }
  const norm = x => x.replace(/\\s+/g, ' ');
  for (const p of phr) {
    // find in raw string allowing whitespace differences
    const re = new RegExp(p.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&').replace(/ /g, '\\\\s+'));
    const m = re.exec(s); if (!m) { out[p] = null; continue; }
    const a = m.index, b = a + m[0].length;
    const loc = (pos) => { for (let i = nodes.length - 1; i >= 0; i--) if (nodes[i][1] <= pos) return [nodes[i][0], pos - nodes[i][1]]; };
    const [sn, so] = loc(a), [en, eo] = loc(b);
    const r = document.createRange(); r.setStart(sn, so); r.setEnd(en, Math.min(eo, en.nodeValue.length));
    out[p] = Array.from(r.getClientRects()).filter(q => q.width > 2).map(q => [q.left, q.top + window.scrollY, q.right, q.bottom + window.scrollY]);
  }
  return out;
}"""
HIDE = """for (const sel of ['#cookie', '.cookie', '[class*=cookie]', '[id*=cookie]', '.usa-banner', '[class*=banner]', '[class*=consent]', '[id*=consent]'])
  document.querySelectorAll(sel).forEach(e => { if (e.offsetHeight < 400) e.style.display = 'none'; });"""
async def one(b, k, u, phr):
    ctx = await b.new_context(viewport={"width": 432, "height": 768}, device_scale_factor=2.5, is_mobile=True, has_touch=True,
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
    p = await ctx.new_page()
    for attempt in range(6):
        await p.goto(u, wait_until="networkidle", timeout=60000); await p.wait_for_timeout(3000 + 2000 * attempt)
        if await p.evaluate("document.documentElement.scrollHeight") > 3000: break
        print(k, "retry", attempt, await p.title())
    await p.evaluate(HIDE)
    hgt = await p.evaluate("document.documentElement.scrollHeight")
    for yy in range(0, hgt, 600): await p.evaluate(f"window.scrollTo(0,{yy})"); await p.wait_for_timeout(60)
    await p.evaluate("window.scrollTo(0,0)"); await p.wait_for_timeout(1500)
    for _ in range(4):
        hgt = await p.evaluate("document.documentElement.scrollHeight")
        await p.set_viewport_size({"width": 432, "height": hgt}); await p.wait_for_timeout(1500)
    rects = await p.evaluate(JS, phr)
    await p.screenshot(path=f"scr/{k}_full.png", full_page=True)
    print(k, "scrollH", await p.evaluate("[document.documentElement.scrollHeight, window.scrollY]"))
    json.dump(rects, open(f"scr/{k}_rects.json", "w"), indent=1)
    print(k, {q[:40]: (len(v) if v else None) for q, v in rects.items()})
    await ctx.close()
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        for k, (u, phr) in PAGES.items(): await one(b, k, u, phr)
        await b.close()
asyncio.run(main())
