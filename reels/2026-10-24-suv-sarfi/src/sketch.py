"""Hand-drawn 'notebook' data scenes for the 4 778 L reel. Paper background, marker ink, wobbly 'boiling'
lines (re-drawn at ~8 fps like hand animation), write-on text, highlighter swipes. usage: sketch.py outdir"""
import sys, math, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
OUT = sys.argv[1]
W, H, FPS = 1080, 1920, 30
FD = "/home/claude/r2/fonts/"
def cav(s, bold=True):
    f = ImageFont.truetype(FD + "Caveat[wght].ttf", s)
    try: f.set_variation_by_name("Bold" if bold else "Medium")
    except Exception: pass
    return f
def pat(s): return ImageFont.truetype(FD + "PatrickHand-Regular.ttf", s)
INK, RED, BLUE, WATER, HL, GREY = (28, 44, 92), (214, 58, 47), (40, 110, 200), (70, 160, 225), (255, 222, 60), (120, 120, 120)

# ---------- paper ----------
rng0 = np.random.default_rng(1)
def make_paper():
    base = np.ones((H, W, 3), np.float32) * np.array([246, 241, 230], np.float32)
    n = rng0.normal(0, 1, (H // 2, W // 2)).astype(np.float32)
    from scipy.ndimage import gaussian_filter, zoom
    grain = zoom(gaussian_filter(n, 1.2), 2, order=1)[:H, :W] * 5 + rng0.normal(0, 2.2, (H, W))
    base += grain[..., None]
    yy, xx = np.mgrid[0:H, 0:W]
    vig = 1 - 0.10 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    base *= vig[..., None]
    im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im, "RGBA")
    for x in range(0, W, 54): d.line([(x, 0), (x, H)], fill=(120, 170, 220, 38), width=2)       # squared paper
    for y in range(0, H, 54): d.line([(0, y), (W, y)], fill=(120, 170, 220, 38), width=2)
    d.line([(96, 0), (96, H)], fill=(230, 110, 110, 90), width=3)                               # margin line
    # masking tape at the top corners
    for cx, ang in [(150, -28), (930, 24)]:
        tape = Image.new("RGBA", (260, 70), (232, 214, 170, 175)); tape = tape.rotate(ang, expand=True)
        im.paste(tape, (cx - tape.width // 2, 20 - tape.height // 3), tape)
    return im
PAPER = make_paper()

# ---------- hand-drawn primitives ----------
def jitter_seed(t, k=0): return int(t * 8) * 1000 + k          # boil: new wobble 8x per second
def wob(pts, seed, amp=2.2, step=18):
    r = np.random.default_rng(seed); out = []
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0); n = max(1, int(L / step))
        for i in range(n):
            u = i / n; out.append((x0 + (x1 - x0) * u + r.normal(0, amp), y0 + (y1 - y0) * u + r.normal(0, amp)))
    out.append((pts[-1][0] + r.normal(0, amp), pts[-1][1] + r.normal(0, amp)))
    return out
def partial(pts, p):
    if p >= 1: return pts
    if p <= 0: return pts[:1]
    seg = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts[:-1], pts[1:])]
    tot, acc, out = sum(seg), 0, [pts[0]]
    for (a, b), s in zip(zip(pts[:-1], pts[1:]), seg):
        if acc + s >= p * tot:
            u = (p * tot - acc) / s if s else 0; out.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)); break
        out.append(b); acc += s
    return out
def stroke(d, pts, col, w, t, k, p=1.0, amp=2.2, alpha=235):
    q = partial(wob(pts, jitter_seed(t, k), amp), p)
    if len(q) > 1: d.line(q, fill=col + (alpha,), width=w, joint="curve")
    for x, y in (q[0], q[-1]): d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=col + (alpha,))
def ellipse_pts(cx, cy, rx, ry, turns=1.12, start=-2.4):
    n = 60; return [(cx + rx * math.cos(start + 2 * math.pi * turns * i / n), cy + ry * math.sin(start + 2 * math.pi * turns * i / n)) for i in range(n + 1)]
def write(im, x, y, s, font, col, p=1.0, t=0, k=0, center=False, rot=None):
    """write-on text: revealed left to right, tiny boil rotation"""
    if p <= 0: return 0
    d0 = ImageDraw.Draw(im); w = d0.textlength(s, font=font); hgt = font.size * 1.35
    lay = Image.new("RGBA", (int(w) + 40, int(hgt) + 40), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((20, 10), s, font=font, fill=col + (240,))
    if p < 1:
        m = Image.new("L", lay.size, 0); ImageDraw.Draw(m).rectangle([0, 0, 20 + w * p, lay.height], fill=255)
        lay.putalpha(Image.composite(lay.getchannel("A"), Image.new("L", lay.size, 0), m))
    r = np.random.default_rng(jitter_seed(t, k)); ang = (rot if rot is not None else 0) + r.normal(0, 0.35)
    lay = lay.rotate(ang, resample=Image.BICUBIC, expand=True)
    X = (W - lay.width) / 2 if center else x - 20
    im.alpha_composite(lay, (int(X + r.normal(0, 0.8)), int(y + r.normal(0, 0.8))))
    return w
def highlight(im, x0, y0, x1, y1, p, t, k):
    if p <= 0: return
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    xe = x0 + (x1 - x0) * min(1, p); r = np.random.default_rng(k)
    d.polygon([(x0, y0 + r.normal(0, 4)), (xe, y0 + r.normal(0, 4)), (xe, y1 + r.normal(0, 4)), (x0, y1 + r.normal(0, 4))], fill=HL + (120,))
    im.alpha_composite(lay)
def hatch(d, x0, y0, x1, y1, col, p, t, k, gap=16, w=6, alpha=200):
    """marker scribble fill, drawn left to right"""
    r = np.random.default_rng(k); xs = np.arange(x0, x1, gap)
    n = int(len(xs) * max(0, min(1, p)))
    pts = []
    for i, x in enumerate(xs[:n]):
        pts += [(x + r.normal(0, 2), y1 - 4 + r.normal(0, 2)), (x + gap * 0.5 + r.normal(0, 2), y0 + 4 + r.normal(0, 2))]
    if len(pts) > 1: d.line(pts, fill=col + (alpha,), width=w, joint="curve")
def ease(u): u = max(0, min(1, u)); return 1 - (1 - u) ** 3
def ph(t, t0, d): return ease((t - t0) / d)
def fmt(n): return f"{int(round(n)):,}".replace(",", " ")

def render(name, dur, scene):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", f"{OUT}/{name}.mp4"], stdin=subprocess.PIPE)
    for f in range(int(dur * FPS)):
        t = f / FPS; im = PAPER.copy().convert("RGBA"); scene(im, t)
        p.stdin.write(im.convert("RGB").tobytes())
    p.stdin.close(); p.wait()

# ---------- A: the sum, worked out on paper ----------
def calc(im, t):
    d = ImageDraw.Draw(im, "RGBA")
    write(im, 0, 150, "4 778 litr qayerdan chiqadi?", cav(78), INK, ph(t, 0, 0.9), t, 1, center=True, rot=-1)
    stroke(d, [(180, 255), (900, 250)], RED, 6, t, 2, ph(t, 0.7, 0.4))
    write(im, 150, 320, "yiliga olinadigan suv:", pat(48), GREY, ph(t, 1.0, 0.5), t, 3)
    write(im, 150, 380, "54,56 mlrd m³", cav(118), INK, ph(t, 1.3, 0.8), t, 4)
    write(im, 150, 540, "÷ 365 kun", cav(100), INK, ph(t, 2.2, 0.6), t, 5)
    write(im, 150, 670, "÷ 31,3 mln kishi*", cav(100), INK, ph(t, 2.9, 0.7), t, 6)
    stroke(d, [(140, 820), (940, 812)], INK, 7, t, 7, ph(t, 3.7, 0.35))
    highlight(im, 160, 860, 880, 975, ph(t, 4.6, 0.5), t, 8)
    write(im, 0, 830, "= 4 778 litr", cav(150), RED, ph(t, 4.0, 0.7), t, 9, center=True, rot=-2)
    d = ImageDraw.Draw(im, "RGBA")
    stroke(d, ellipse_pts(540, 915, 420, 110), RED, 7, t, 10, ph(t, 5.1, 0.7), amp=3)
    write(im, 0, 1030, "*ma'lumot yilidagi aholi · Worldometer (BMT, FAO)", pat(32), GREY, ph(t, 5.3, 0.4), t, 11, center=True)
render("sk_calc", 7.0, calc)

# ---------- B: 24 bathtubs + tally marks ----------
def tub_pts(x, y, w, h):
    return [(x, y), (x + 8, y + h - 18), (x + 30, y + h), (x + w - 30, y + h), (x + w - 8, y + h - 18), (x + w, y)]
def tubs(im, t):
    d = ImageDraw.Draw(im, "RGBA")
    write(im, 0, 140, "1 vanna ≈ 200 litr", cav(84), INK, ph(t, 0, 0.7), t, 1, center=True, rot=-1)
    cols, w, h, gx, gy, x0, y0 = 4, 170, 58, 52, 38, 150, 260
    for n in range(24):
        r_, c = divmod(n, cols); x = x0 + c * (w + gx); y = y0 + r_ * (h + gy)
        t0 = 0.5 + n * 0.11
        stroke(d, tub_pts(x, y, w, h), INK, 5, t, 100 + n, ph(t, t0, 0.25))
        if t > t0 + 0.15:
            hatch(d, x + 10, y + 14, x + w - 10, y + h - 4, WATER, ph(t, t0 + 0.15, 0.3), t, 200 + n, gap=14, w=5)
        stroke(d, [(x + 22, y + h), (x + 18, y + h + 16)], INK, 5, t, 300 + n, 1 if t > t0 + 0.2 else 0)
        stroke(d, [(x + w - 22, y + h), (x + w - 18, y + h + 16)], INK, 5, t, 400 + n, 1 if t > t0 + 0.2 else 0)
    # tally marks under the grid
    k = min(24, max(0, int((t - 0.5) / 0.11) + 1)) if t > 0.5 else 0
    tx, ty = 200, 870
    for i in range(k):
        g, j = divmod(i, 5)
        bx = tx + g * 150
        if j < 4: stroke(d, [(bx + j * 26, ty), (bx + j * 26 + 4, ty + 70)], INK, 6, t, 500 + i)
        else: stroke(d, [(bx - 12, ty + 58), (bx + 96, ty + 12)], RED, 6, t, 500 + i)
    write(im, 0, 950, "24 ta vanna!", cav(96), RED, ph(t, 3.4, 0.6), t, 2, center=True, rot=-3) if t > 3.4 else None
render("sk_tubs", 5.0, tubs)

# ---------- C: neighbours bar chart, drawn with marker ----------
DATA = [("Turkmaniston", 15445), ("O'zbekiston", 4778), ("Tojikiston", 4460), ("Qirg'iziston", 4153), ("Qozog'iston", 3397)]
def rank(im, t):
    d = ImageDraw.Draw(im, "RGBA")
    write(im, 0, 130, "Kishi boshiga, litr / kun", cav(80), INK, ph(t, 0, 0.7), t, 1, center=True, rot=-1)
    x0, y, maxw, bh, gap = 150, 300, 640, 74, 72
    stroke(d, [(x0 - 10, y - 30), (x0 - 14, y + 5 * (bh + gap) - 40)], INK, 6, t, 2, ph(t, 0.4, 0.4))
    for i, (name, v) in enumerate(DATA):
        t0 = 0.6 + i * 0.4; L = maxw * v / 15445 * ph(t, t0, 0.8)
        yb = y + i * (bh + gap)
        write(im, x0, yb - 64, name, pat(40), INK, ph(t, t0, 0.3), t, 10 + i)
        col = RED if name == "O'zbekiston" else BLUE
        if L > 4:
            hatch(d, x0, yb, x0 + L, yb + bh * 0.62, col, 1, t, 20 + i, gap=13, w=6, alpha=170)
            stroke(d, [(x0, yb), (x0 + L, yb), (x0 + L, yb + bh * 0.62), (x0, yb + bh * 0.62)], col, 4, t, 30 + i, amp=1.6)
            write(im, x0 + L + 18, yb - 14, fmt(v * ph(t, t0, 0.8)), cav(64), col, 1, t, 40 + i)
    if t > 3.4:
        highlight(im, x0 - 6, y + (bh + gap) - 60, x0 + 230, y + (bh + gap) - 14, ph(t, 3.4, 0.4), t, 50)
        d = ImageDraw.Draw(im, "RGBA")
        ax, ay = 520, y + (bh + gap) + 10
        stroke(d, [(ax + 200, ay + 110), (ax + 90, ay + 70), (ax + 10, ay + 14)], RED, 6, t, 51, ph(t, 3.6, 0.4))
        stroke(d, [(ax + 10, ay + 14), (ax + 40, ay + 2)], RED, 6, t, 52, ph(t, 3.95, 0.15))
        stroke(d, [(ax + 10, ay + 14), (ax + 34, ay + 36)], RED, 6, t, 53, ph(t, 3.95, 0.15))
        write(im, ax + 150, ay + 110, "dunyoda 4-o'rin!", cav(60), RED, ph(t, 4.1, 0.5), t, 54, rot=-4)
        write(im, 830, y - 70, "1-o'rin", cav(52), BLUE, ph(t, 4.4, 0.4), t, 55, rot=-3)
    write(im, 0, 1030, "Worldometer (BMT, FAO) · Times of Central Asia, 2026", pat(32), GREY, ph(t, 4.6, 0.4), t, 60, center=True)
render("sk_rank", 6.0, rank)

# ---------- D: measuring cylinder 4 778 L → farms → leaks ----------
def split(im, t):
    d = ImageDraw.Draw(im, "RGBA")
    write(im, 0, 130, "4 778 litr qayerga ketadi?", cav(80), INK, ph(t, 0, 0.7), t, 1, center=True, rot=-1)
    cx0, cx1, top, bot = 200, 520, 300, 1000                     # cylinder
    lvl = ph(t, 0.6, 1.0)
    wl = bot - (bot - top - 20) * lvl
    if lvl > 0:
        hatch(d, cx0 + 8, wl, cx1 - 8, bot - 8, WATER, 1, t, 2, gap=12, w=7, alpha=170)
    stroke(d, [(cx0 - 20, top), (cx0, top + 10), (cx0, bot), (cx1, bot), (cx1, top + 10), (cx1 + 20, top)], INK, 7, t, 3, ph(t, 0.2, 0.5))
    for i in range(1, 10):                                       # graduation ticks
        yy = bot - (bot - top - 20) * i / 10
        stroke(d, [(cx0, yy), (cx0 + (40 if i % 5 else 70), yy)], INK, 4, t, 10 + i, ph(t, 0.5, 0.3))
    y90 = bot - (bot - top - 20) * 0.9
    if t > 1.8:
        stroke(d, [(cx0 - 30, y90), (cx1 + 60, y90 + 4)], RED, 6, t, 30, ph(t, 1.8, 0.4))
        write(im, cx1 + 70, y90 - 70, "10% uy, sanoat", pat(46), INK, ph(t, 2.0, 0.5), t, 31)
        write(im, cx1 + 70, y90 + 60, "90% dalalarga", cav(70), BLUE, ph(t, 2.3, 0.6), t, 32)
        write(im, cx1 + 70, y90 + 140, "≈ 4 300 L", cav(92), BLUE, ph(t, 2.6, 0.6), t, 33)
    if t > 3.6:                                                  # crack + leaking drops
        crack = [(cx1, 760), (cx1 + 18, 780), (cx1 + 6, 800), (cx1 + 24, 828)]
        stroke(d, crack, RED, 5, t, 40, ph(t, 3.6, 0.3), amp=1)
        for j in range(6):
            ph_ = (t - 3.9 - j * 0.28)
            if ph_ > 0:
                yy = 830 + (ph_ % 1.2) * 200; xx = cx1 + 34 + j % 3 * 8
                d.ellipse([xx - 9, yy - 14, xx + 9, yy + 10], fill=WATER + (220,), outline=INK + (200,), width=3)
        highlight(im, cx1 + 60, 845, cx1 + 520, 990, ph(t, 4.3, 0.5), t, 41)
        write(im, cx1 + 70, 760, "36% i kanallarda", pat(48), RED, ph(t, 4.0, 0.5), t, 42)
        write(im, cx1 + 70, 830, "≈ 1 550 L", cav(110), RED, ph(t, 4.3, 0.6), t, 43, rot=-3)
        write(im, cx1 + 70, 940, "yo'qoladi!", cav(64), RED, ph(t, 4.8, 0.4), t, 44, rot=-3)
    write(im, 0, 1040, "kishi boshiga, har kuni · Prezident matbuot xizmati, 2023", pat(32), GREY, ph(t, 5.2, 0.4), t, 50, center=True)
render("sk_split", 7.0, split)
print("ok")
