"""Animated data charts for the 4 778 L reel (1080x1920, 30 fps). usage: charts.py outdir"""
import sys, math, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
OUT = sys.argv[1]
W, H, FPS = 1080, 1920, 30
F = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
fnt = lambda w, s: ImageFont.truetype(F.format(w), s)
BG1, BG2 = (11, 31, 51), (6, 16, 28)
WHITE, SKY, YEL, GREY, RED = (255, 255, 255), (132, 210, 253), (255, 225, 0), (150, 170, 190), (255, 110, 80)

def bg():
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        k = y / H; d.line([(0, y), (W, y)], fill=tuple(int(BG1[i] * (1 - k) + BG2[i] * k) for i in range(3)))
    return im
BG = bg()
def ease(u): u = max(0, min(1, u)); return 1 - (1 - u) ** 3
def fade(t, t0, d=0.35): return ease((t - t0) / d)
def fmt(n): return f"{int(round(n)):,}".replace(",", " ")
def ctext(d, y, s, f, col, a=1.0, x=None):
    w = d.textlength(s, font=f); x = (W - w) / 2 if x is None else x
    d.text((x, y + (1 - a) * 25), s, font=f, fill=col + (int(255 * a),))
    return w

def render(name, dur, draw):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", f"{OUT}/{name}.mp4"], stdin=subprocess.PIPE)
    for f in range(int(dur * FPS)):
        im = BG.copy(); d = ImageDraw.Draw(im, "RGBA"); draw(d, f / FPS, im)
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()

def src(d, s): ctext(d, 262, s, fnt("Medium", 30), GREY)

# A — the calculation
def calc(d, t, im):
    ctext(d, 170, "4 778 litr qayerdan chiqadi?", fnt("ExtraBold", 62), SKY, fade(t, 0))
    rows = [(0.5, "Yiliga olinadigan suv", 54.56, "{:.2f} mlrd m³", WHITE),
            (1.6, "÷  365 kun", None, "", WHITE),
            (2.5, "÷  31,3 mln kishi*", None, "", WHITE)]
    y = 330
    for t0, lab, val, fm, col in rows:
        a = fade(t, t0)
        if val is None:
            ctext(d, y, lab, fnt("Bold", 70), col, a)
            y += 105
        else:
            ctext(d, y, lab, fnt("SemiBold", 44), GREY, a)
            v = val * ease((t - t0) / 0.9)
            ctext(d, y + 60, fm.format(v).replace(".", ","), fnt("Black", 110), col, a)
            y += 200
    a = fade(t, 3.4)
    if a > 0:
        d.line([(160, y - 10), (920, y - 10)], fill=WHITE + (int(200 * a),), width=4)
        v = 4778 * ease((t - 3.4) / 1.0)
        ctext(d, y + 20, f"= {fmt(v)} litr", fnt("Black", 130), YEL, a)
        ctext(d, y + 170, "har bir kishiga, har kuni", fnt("SemiBold", 46), WHITE, a)
        ctext(d, y + 240, "*ma'lumot yilidagi aholi soni", fnt("Medium", 30), GREY, a)
    src(d, "Manba: Worldometer (BMT, FAO), 2026")
render("chart_calc", 6.5, calc)

# B — 24 bathtubs
def tub(d, x, y, w, h, fill):
    d.rounded_rectangle([x, y, x + w, y + h], 18, outline=WHITE + (230,), width=5)
    if fill > 0:
        fh = (h - 14) * fill
        d.rounded_rectangle([x + 7, y + h - 7 - fh, x + w - 7, y + h - 7], 12, fill=SKY + (235,))
    d.line([(x + 15, y + h), (x + 15, y + h + 18)], fill=WHITE + (230,), width=5)
    d.line([(x + w - 15, y + h), (x + w - 15, y + h + 18)], fill=WHITE + (230,), width=5)
def tubs(d, t, im):
    ctext(d, 170, "1 vanna ≈ 200 litr", fnt("ExtraBold", 62), SKY, fade(t, 0))
    cols, rows, w, h, gx, gy = 4, 6, 180, 66, 50, 40
    x0 = (W - (cols * w + (cols - 1) * gx)) / 2; y0 = 290
    n = 0
    for r in range(rows):
        for c in range(cols):
            fill = ease((t - 0.4 - n * 0.11) / 0.35)
            tub(d, x0 + c * (w + gx), y0 + r * (h + gy), w, h, fill); n += 1
    k = min(24, max(0, int((t - 0.4) / 0.11) + 1)) if t > 0.4 else 0
    ctext(d, 930, f"{k} ta vanna", fnt("Black", 110), YEL)
    ctext(d, 1060, "= 4 778 litr · har kuni", fnt("SemiBold", 42), WHITE, fade(t, 3.0))
render("chart_tubs", 4.6, tubs)

# C — Central Asia ranking
DATA = [("Turkmaniston", 15445, "1-o'rin dunyoda"), ("O'zbekiston", 4778, "4-o'rin dunyoda"),
        ("Tojikiston", 4460, ""), ("Qirg'iziston", 4153, ""), ("Qozog'iston", 3397, "")]
def bars(d, t, im):
    ctext(d, 150, "Kishi boshiga suv sarfi", fnt("ExtraBold", 64), SKY, fade(t, 0))
    ctext(d, 228, "litr / kun · Manba: Worldometer (BMT, FAO), 2026", fnt("Medium", 32), GREY, fade(t, 0))
    x0, maxw, bh, gap, y = 70, 760, 110, 40, 420
    for i, (name, v, note) in enumerate(DATA):
        t0 = 0.4 + i * 0.35; a = fade(t, t0)
        col = YEL if name == "O'zbekiston" else (SKY if i == 0 else (200, 215, 230))
        d.text((x0, y - 58), name, font=fnt("Bold", 44), fill=WHITE + (int(255 * a),))
        L = maxw * v / 15445 * ease((t - t0) / 1.0)
        d.rounded_rectangle([x0, y, x0 + max(L, 2), y + bh * 0.62], 14, fill=col + (int(255 * a),))
        d.text((x0 + L + 18, y + 4), fmt(v * ease((t - t0) / 1.0)), font=fnt("Black", 56), fill=col + (int(255 * a),))
        if note:
            d.text((x0 + 340 if i == 0 else x0 + 360, y - 52), note, font=fnt("SemiBold", 36), fill=col + (int(255 * fade(t, t0 + 0.9)),))
        y += bh + gap
render("chart_rank", 5.5, bars)

# D — where the 4 778 L go
def split(d, t, im):
    ctext(d, 170, "4 778 litr qayerga ketadi?", fnt("ExtraBold", 62), SKY, fade(t, 0))
    x0, x1, y0, y1 = 140, 940, 330, 1050          # one tall bar = 4 778 L
    H_ = y1 - y0
    a = fade(t, 0.3)
    agri = 0.90 * ease((t - 0.8) / 0.9)
    lost = 0.36 * 0.90 * ease((t - 3.0) / 0.9)
    # other uses (top 10%)
    d.rounded_rectangle([x0, y0, x1, y1], 26, fill=(60, 80, 100, int(255 * a)))
    ya = y1 - H_ * agri
    if agri > 0:
        d.rounded_rectangle([x0, ya, x1, y1], 26, fill=SKY + (255,))
    if lost > 0:
        yl = y1 - H_ * lost
        d.rounded_rectangle([x0, yl, x1, y1], 26, fill=RED + (255,))
    fb, fs = fnt("Black", 64), fnt("SemiBold", 38)
    if t > 1.0:
        d.text((x0 + 30, y0 + 22), "Uy, sanoat ≈ 10%", font=fs, fill=WHITE + (int(255 * fade(t, 1.6)),))
        d.text((x0 + 30, ya + 30), "Qishloq xo'jaligi", font=fs, fill=BG1 + (int(255 * fade(t, 1.4)),))
        d.text((x0 + 30, ya + 80), "≈ 4 300 L (90%+)", font=fb, fill=BG1 + (int(255 * fade(t, 1.4)),))
    if t > 3.2:
        yl = y1 - H_ * 0.324
        d.text((x0 + 30, yl + 30), "shundan 36% i tuproq kanallarda", font=fs, fill=WHITE + (int(255 * fade(t, 3.5)),))
        d.text((x0 + 30, yl + 80), "≈ 1 550 L yo'qoladi", font=fb, fill=WHITE + (int(255 * fade(t, 3.5)),))
    src(d, "kishi boshiga, har kuni · Manba: Prezident matbuot xizmati, 2023")
render("chart_split", 6.5, split)
print("ok")
