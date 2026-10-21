import json, sys, html, pathlib, os
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).parent
slides = json.loads((ROOT / sys.argv[1]).read_text(encoding="utf-8"))
out = pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
F = ROOT / "node_modules/@fontsource"

def ff(family, path, weight):
    return f"@font-face{{font-family:'{family}';src:url('file://{path}') format('woff2');font-weight:{weight};}}"

fonts = "".join([
    ff("Manrope", F/"manrope/files/manrope-latin-800-normal.woff2", 800),
    ff("ManropeX", F/"manrope/files/manrope-latin-ext-800-normal.woff2", 800),
    ff("Inter", F/"inter/files/inter-latin-400-normal.woff2", 400),
    ff("Inter", F/"inter/files/inter-latin-600-normal.woff2", 600),
    ff("InterX", F/"inter/files/inter-latin-ext-400-normal.woff2", 400),
    ff("InterX", F/"inter/files/inter-latin-ext-600-normal.woff2", 600),
])

DROP = '<svg width="34" height="42" viewBox="0 0 34 42"><path d="M17 2C17 2 3 18 3 27a14 14 0 0 0 28 0C31 18 17 2 17 2Z" fill="none" stroke="currentColor" stroke-width="3"/></svg>'
RIPPLE = '<svg class="ripple" width="760" height="760" viewBox="0 0 760 760">' + "".join(
    f'<circle cx="380" cy="380" r="{r}" fill="none" stroke="currentColor" stroke-width="2" opacity="{o}"/>'
    for r, o in [(90, .55), (170, .4), (250, .28), (330, .18), (378, .1)]) + '</svg>'

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1350px}
body{font-family:Inter,InterX,sans-serif;-webkit-font-smoothing:antialiased}
.s{position:relative;width:1080px;height:1350px;padding:96px 104px;display:flex;flex-direction:column;overflow:hidden}
.light{background:#F7F8FA;color:#0B1F33}
.dark{background:#0B1F33;color:#FFFFFF}
.top{display:flex;justify-content:space-between;align-items:center;font-size:28px;font-weight:600;letter-spacing:.02em}
.brand{display:flex;align-items:center;gap:16px;color:#2F80ED}
.dark .brand{color:#6FA8F5}
.brand span{color:inherit}
.brand sub{font-size:.7em;vertical-align:-.15em;line-height:0}
.count{opacity:.55;font-variant-numeric:tabular-nums}
.main{flex:1;display:flex;flex-direction:column;justify-content:center}
.kicker{font-size:30px;font-weight:600;text-transform:uppercase;letter-spacing:.12em;color:#2F80ED;margin-bottom:36px}
.dark .kicker{color:#6FA8F5}
h1{font-family:Manrope,ManropeX,sans-serif;font-weight:800;font-size:76px;line-height:1.08;letter-spacing:-.02em}
.hook h1{font-size:92px}
.accent{font-family:Manrope,ManropeX,sans-serif;font-weight:800;font-size:76px;line-height:1.1;letter-spacing:-.02em;color:#6FA8F5;margin-top:28px}
.rule{width:96px;height:6px;background:#2F80ED;border-radius:3px;margin:48px 0 44px}
.body p{font-size:42px;line-height:1.38;margin-bottom:30px;max-width:860px}
.body p:last-child{margin-bottom:0}
.steps{list-style:none;margin-top:4px}
.steps li{display:flex;align-items:center;gap:32px;font-size:42px;line-height:1.3;margin-bottom:34px}
.steps .n{flex:none;width:72px;height:72px;border-radius:50%;border:4px solid #2F80ED;color:#2F80ED;display:flex;align-items:center;justify-content:center;font-family:Manrope,ManropeX;font-weight:800;font-size:34px}
.note{margin-top:20px;padding:26px 32px;border-left:6px solid #2F80ED;background:#EAF2FD;font-size:34px;line-height:1.35}
.foot{display:flex;justify-content:space-between;align-items:center;font-size:26px;padding-top:32px;border-top:2px solid currentColor;opacity:.6}
.dark .foot{opacity:.55}
.ripple{position:absolute;right:-330px;bottom:-330px;color:#2F80ED;opacity:.7;pointer-events:none}.top,.main,.foot{position:relative;z-index:1}
.handle{font-family:Manrope,ManropeX;font-weight:800;font-size:46px;color:#6FA8F5;margin-top:56px}
.swipe{margin-top:64px;font-size:30px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;opacity:.7}
"""

e = html.escape
# Branding (2026-10-21: Instagram and YouTube share one look — Doktor H2O / @suvyektiv, sky theme).
# Old Instagram look: THEME=navy BRAND=the.waterengineer HANDLE=@the.waterengineer
BRAND = os.environ.get("BRAND", "Doktor H<sub>2</sub>O")  # raw HTML allowed
HANDLE = os.environ.get("HANDLE", "@suvyektiv")
TAGLINE = os.environ.get("TAGLINE", "Suv haqida, oddiy tilda.")
# THEME=sky: Doktor H2O palette, taken from the YouTube avatar (sky-blue #84D2FD bg, navy "Dr. H2O" text)
THEME_CSS = {"sky": """
.dark{background:#84D2FD;color:#0B1F33}
.dark .brand,.dark .kicker,.dark .handle,.accent{color:#1F3A80}
.ripple{color:#FFFFFF;opacity:.55}
.light{background:#EDF8FF;color:#0B1F33}
.light .brand,.light .kicker{color:#1F6FB2}
.rule{background:#1F6FB2}
.steps .n{border-color:#1F6FB2;color:#1F6FB2}
.note{border-left-color:#1F6FB2;background:#D6EFFE}
.dark .foot{opacity:.7}
"""}.get(os.environ.get("THEME", "sky"), "")
n = len(slides)
for i, s in enumerate(slides, 1):
    k = s["kind"]
    parts = []
    if s.get("kicker"): parts.append(f'<div class="kicker">{e(s["kicker"])}</div>')
    parts.append(f'<h1>{e(s["title"])}</h1>')
    if s.get("accent"): parts.append(f'<div class="accent">{e(s["accent"])}</div>')
    if k in ("body", "steps"): parts.append('<div class="rule"></div>')
    if k == "body":
        parts.append('<div class="body">' + "".join(f"<p>{e(p)}</p>" for p in s["body"]) + "</div>")
    if k == "steps":
        parts.append('<ol class="steps">' + "".join(f'<li><span class="n">{j}</span><span>{e(t)}</span></li>' for j, t in enumerate(s["steps"], 1)) + "</ol>")
        if s.get("note"): parts.append(f'<div class="note">{e(s["note"])}</div>')
    if k == "hook": parts.append('<div class="swipe">Varaqlang →</div>')
    if k == "cta": parts.append(f'<div class="handle">{e(HANDLE if "HANDLE" in os.environ else s["handle"])}</div>')
    ripple = RIPPLE if s["theme"] == "dark" else ""
    doc = f"""<!doctype html><html><head><meta charset="utf-8"><style>{fonts}{CSS}{THEME_CSS}</style></head>
<body><div class="s {s['theme']} {k}">{ripple}
<div class="top"><div class="brand">{DROP}<span>{BRAND}</span></div><div class="count">{i}/{n}</div></div>
<div class="main">{''.join(parts)}</div>
<div class="foot"><span>{e(HANDLE)}</span><span>{e(TAGLINE)}</span></div>
</div></body></html>"""
    p = ROOT / f"_slide{i}.html"; p.write_text(doc, encoding="utf-8")

with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page(viewport={"width": 1080, "height": 1350})
    for i in range(1, n + 1):
        pg.goto(f"file://{ROOT}/_slide{i}.html"); pg.wait_for_load_state("networkidle")
        pg.evaluate("document.fonts.ready")
        over = pg.evaluate("(() => {const m=document.querySelector('.main');return m.scrollHeight>m.clientHeight+2})()")
        pg.screenshot(path=str(out / f"{i:02d}.png"))
        print(i, "OVERFLOW" if over else "ok")
    b.close()
