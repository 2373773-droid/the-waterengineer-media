"""'2050: suv taqchilligi 5 barobar' reel — 'timeline documentary' style:
graphics drawn straight on real footage (no cards), left-aligned kinetic numbers, a top HUD (topic + chapter n/6 +
progress line), a soft top gradient for legibility. Captions: same calm style as the 24.10 reel (news.caps_render).
usage: doc.py gfx | build out.mp4 [--nocaps]"""
import sys, math, subprocess
sys.path.insert(0, "/home/claude/r2")
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R = "/home/claude/r3/"
W, H, FPS = 1080, 1920, 30
F = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
fn = lambda w, s: ImageFont.truetype(F.format(w), s)
WHITE, SKY, SKYD, NAVY, WARN = (255, 255, 255), (132, 210, 253), (31, 111, 178), (11, 31, 51), (255, 140, 110)
def ease(u): u = max(0, min(1, u)); return 1 - (1 - u) ** 3
def ph(t, t0, d=0.5): return ease((t - t0) / d)
def fmt(n, dec=0):
    s = f"{n:,.{dec}f}".replace(",", " ")
    return s.replace(".", ",")

# scene list: footage, start, dur, crop-x, chapter title, scene fn name
S = [("H6", 3.0, 4.5, .50, "", "hook"),
     ("G6", 4.0, 8.0, .50, "TALAB va ZAXIRA", "lines"),
     ("G0", 3.0, 5.5, .50, "TAQCHILLIK", "gap"),
     ("D5", 0.0, 8.0, .50, "KISHI BOSHIGA", "percap"),
     ("A0", 2.0, 6.5, .50, "MUZLIKLAR", "glacier"),
     ("B3", 0.0, 7.0, .40, "YER OSTI SUVI", "well"),
     ("F7", 4.0, 8.0, .62, "YECHIM", "fix"),
     ("E0", 6.0, 6.0, .50, "", "cta")]
TOTAL = sum(s[2] for s in S)
STARTS = [sum(s[2] for s in S[:i]) for i in range(len(S))]

def text(d, x, y, s, f, col, a=1.0, anchor="la", shadow=True):
    if a <= 0: return
    y = y + (1 - a) * 24
    if shadow: d.text((x + 3, y + 4), s, font=f, fill=(0, 0, 0, int(140 * a)), anchor=anchor)
    d.text((x, y), s, font=f, fill=col + (int(255 * a),), anchor=anchor)

def hud(d, i, t):
    """top HUD: topic, chapter n/6, thin progress line (whole-video progress)"""
    g = (STARTS[i] + t) / TOTAL
    d.text((80, 120), "SUV TAQCHILLIGI · 2050", font=fn("Bold", 30), fill=WHITE + (230,))
    ch = [k for k in range(1, 7)]
    if 1 <= i <= 6:
        d.text((1000, 120), f"{i:02d}/06", font=fn("Bold", 30), fill=SKY + (255,), anchor="ra")
    d.line([(80, 172), (1000, 172)], fill=(255, 255, 255, 90), width=4)
    d.line([(80, 172), (80 + 920 * g, 172)], fill=SKY + (255,), width=4)
    d.ellipse([80 + 920 * g - 8, 164, 80 + 920 * g + 8, 180], fill=SKY + (255,))

def chapter(d, title, t):
    if not title: return
    a = ph(t, 0.1, 0.4)
    d.rectangle([80, 230, 80 + 8, 280], fill=SKY + (int(255 * a),))
    text(d, 108, 232, title, fn("ExtraBold", 40), WHITE, a)

def src(d, s, t, t0=1.0): text(d, 80, 1060, s, fn("Medium", 26), (225, 232, 240), ph(t, t0), shadow=True)

# ---------- scenes ----------
def hook(d, t, im):
    y = 2022 + (2050 - 2022) * ph(t, 0.2, 2.2)
    text(d, 80, 420, "Bugun → kelajak", fn("SemiBold", 44), SKY, ph(t, 0))
    text(d, 72, 480, f"{int(round(y))}", fn("Black", 260), WHITE, ph(t, 0.1))
    text(d, 80, 770, "suv taqchilligi", fn("ExtraBold", 72), WHITE, ph(t, 2.4))
    text(d, 80, 860, "5 barobardan ko'proq", fn("Black", 84), SKY, ph(t, 2.9))

def lines(d, t, im):
    x0, x1, y0, y1 = 120, 960, 380, 900                     # value axis 50..64 km³
    yv = lambda v: y1 - (v - 50) / 14 * (y1 - y0)
    xv = lambda yr: x0 + (yr - 2022) / 28 * (x1 - x0)
    a = ph(t, 0.2)
    for v in (52, 56, 60, 64):
        d.line([(x0, yv(v)), (x1, yv(v))], fill=(255, 255, 255, int(55 * a)), width=2)
        text(d, x0 - 14, yv(v) - 16, str(v), fn("Medium", 26), (230, 236, 242), a, "ra")
    text(d, x0, y1 + 16, "2022", fn("SemiBold", 30), WHITE, a)
    text(d, x1, y1 + 16, "2050", fn("SemiBold", 30), WHITE, a, "ra")
    p = ph(t, 0.8, 2.6)
    dem = lambda yr: 59 + (62.5 - 59) * (yr - 2022) / 28
    sup = lambda yr: 57 + (52.5 - 57) * (yr - 2022) / 28
    yrs = [2022 + 28 * k / 60 * p for k in range(61)]
    if p > 0:
        poly = [(xv(y), yv(dem(y))) for y in yrs] + [(xv(y), yv(sup(y))) for y in reversed(yrs)]
        d.polygon(poly, fill=WARN + (70,))
        d.line([(xv(y), yv(dem(y))) for y in yrs], fill=SKY + (255,), width=9, joint="curve")
        d.line([(xv(y), yv(sup(y))) for y in yrs], fill=WHITE + (255,), width=9, joint="curve")
    text(d, x0 + 10, yv(59) - 70, "Talab  59", fn("Bold", 38), SKY, ph(t, 0.9))
    text(d, x0 + 10, yv(57) + 30, "Mavjud suv  57", fn("Bold", 38), WHITE, ph(t, 1.1))
    text(d, x1, yv(62.5) - 66, "62–63", fn("Black", 52), SKY, ph(t, 3.3), "ra")
    text(d, x1, yv(52.5) + 14, "52–53", fn("Black", 52), WHITE, ph(t, 3.5), "ra")
    text(d, 540, 960, "km³ / yil", fn("SemiBold", 32), WHITE, ph(t, 0.4), "ma")
    src(d, "Manba: Jahon banki tahlili · O'zsuvta'minot (Kun.uz, 2022)", t, 1.5)

def gap(d, t, im):
    base = 980; sc = 38                                   # px per km³
    a1 = ph(t, 0.3, 0.8); a2 = ph(t, 1.2, 1.4)
    h1 = 2 * sc * a1; h2 = 11.5 * sc * a2
    d.rectangle([180, base - h1, 400, base], fill=WHITE + (235,))
    d.rectangle([620, base - h2, 840, base], fill=WARN + (235,))
    text(d, 290, base + 14, "Bugun", fn("Bold", 38), WHITE, ph(t, 0.3), "ma")
    text(d, 730, base + 14, "2050", fn("Bold", 38), WHITE, ph(t, 1.2), "ma")
    text(d, 290, base - h1 - 90, "2 km³", fn("Black", 70), WHITE, ph(t, 0.6), "ma")
    text(d, 730, base - h2 - 90, f"{fmt(11 * ph(t, 1.2, 1.4))}–12 km³", fn("Black", 64), WARN, ph(t, 1.4), "ma")
    text(d, 80, 300, "Yillik suv taqchilligi", fn("ExtraBold", 56), WHITE, ph(t, 0))
    text(d, 80, 370, "× 5,5–6", fn("Black", 96), SKY, ph(t, 3.0))

def percap(d, t, im):
    text(d, 80, 300, "Bir kishiga yillik suv", fn("ExtraBold", 56), WHITE, ph(t, 0))
    text(d, 80, 368, "so'nggi 15 yilda", fn("SemiBold", 40), (230, 236, 242), ph(t, 0.2))
    v = 3048 + (1589 - 3048) * ph(t, 0.9, 2.2)
    col = WARN if v < 1700 else WHITE
    text(d, 80, 440, f"{fmt(v)}", fn("Black", 190), col, ph(t, 0.5))
    text(d, 80, 650, "m³ / kishi / yil", fn("Bold", 44), WHITE, ph(t, 0.5))
    # scale bar with the 1 700 m³ stress line
    x0, x1, yb = 80, 1000, 790; mx = 3200
    xv = lambda q: x0 + (x1 - x0) * q / mx
    a = ph(t, 0.6)
    d.rounded_rectangle([x0, yb, x1, yb + 34], 17, fill=(255, 255, 255, int(70 * a)))
    d.rounded_rectangle([x0, yb, xv(v), yb + 34], 17, fill=col + (int(240 * a),))
    xs = xv(1700); b = ph(t, 2.4)
    d.line([(xs, yb - 30), (xs, yb + 64)], fill=SKY + (int(255 * b),), width=5)
    text(d, xs, yb + 76, "1 700 — suv stressi chegarasi", fn("Bold", 34), SKY, b, "ma")
    text(d, 80, 960, "Deyarli 2 barobar kam", fn("Black", 62), WARN, ph(t, 3.4))
    src(d, "Manba: O'zsuvta'minot (Kun.uz, 2022) · chegara: Falkenmark ko'rsatkichi", t, 1.2)

def glacier(d, t, im):
    text(d, 80, 300, "Amudaryo suvining", fn("ExtraBold", 56), WHITE, ph(t, 0))
    cx, cy, r = 540, 640, 230; p = 0.74 * ph(t, 0.6, 2.0)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255, 90), width=34)
    if p > 0: d.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * p, fill=SKY + (255,), width=34)
    text(d, cx, cy - 70, f"{int(round(p * 100))}%", fn("Black", 150), WHITE, ph(t, 0.4), "ma")
    text(d, 540, 905, "qor va muzliklar erishidan keladi", fn("Bold", 44), WHITE, ph(t, 2.4), "ma")
    text(d, 540, 965, "Muzliklar esa qisqarmoqda", fn("ExtraBold", 48), WARN, ph(t, 3.4), "ma")
    src(d, "Manba: ICIMOD, Markaziy Osiyo muzliklar forumi (2025)", t, 1.0)

def well(d, t, im):
    text(d, 80, 300, "Yer osti suvi sathi", fn("ExtraBold", 56), WHITE, ph(t, 0))
    text(d, 80, 368, "Quyi Chirchiq, kuzatuv qudug'i", fn("SemiBold", 38), (230, 236, 242), ph(t, 0.2))
    x0, y0, yb = 680, 470, 1010; mpx = (yb - y0) / 6        # 0..6 m below ground
    a = ph(t, 0.3)
    d.line([(x0, y0), (x0, yb)], fill=WHITE + (int(255 * a),), width=6)
    for m in range(7):
        yy = y0 + m * mpx
        d.line([(x0 - 22, yy), (x0, yy)], fill=WHITE + (int(255 * a),), width=4)
        text(d, x0 - 34, yy - 18, f"{m} m", fn("SemiBold", 30), WHITE, a, "ra")
    lvl = 2.15 + (5.38 - 2.15) * ph(t, 1.6, 2.2)
    yy = y0 + lvl * mpx
    d.rectangle([x0 + 10, yy, x0 + 150, yb], fill=SKY + (int(200 * a),))
    d.line([(x0 + 10, y0 + 2.15 * mpx), (x0 + 150, y0 + 2.15 * mpx)], fill=WHITE + (int(200 * ph(t, 1.6)),), width=3)
    text(d, x0 + 165, y0 + 2.15 * mpx - 20, "2,15 m (2014)", fn("Bold", 30), WHITE, ph(t, 0.8))
    text(d, x0 + 165, yy - 24, f"{fmt(lvl, 2)} m", fn("Black", 42), WARN, ph(t, 1.6))
    text(d, 80, 560, "−3,2 m", fn("Black", 118), WARN, ph(t, 3.6))
    text(d, 80, 730, "8 yilda", fn("Bold", 48), WHITE, ph(t, 3.9))
    src(d, "Manba: O'zsuvta'minot, ishchi guruh xulosasi (Kun.uz, 2022)", t, 1.0)

def fix(d, t, im):
    text(d, 80, 300, "Suvning ~90% i —", fn("ExtraBold", 56), WHITE, ph(t, 0))
    text(d, 80, 368, "qishloq xo'jaligida", fn("ExtraBold", 56), WHITE, ph(t, 0.2))
    v = 540 * ph(t, 1.0, 1.8)
    text(d, 80, 500, f"{fmt(v)} mln m³", fn("Black", 128), SKY, ph(t, 0.8))
    text(d, 80, 660, "har yili tejash — sug'orishni yangilash orqali", fn("Bold", 40), WHITE, ph(t, 1.6))
    text(d, 80, 780, "$200 mln · 232 ming gektar", fn("ExtraBold", 50), WHITE, ph(t, 2.6))
    src(d, "Manba: Jahon banki, 2025", t, 1.0)

def cta(d, t, im):
    text(d, 80, 400, "Suvni tejang!", fn("Black", 120), SKY, ph(t, 0))
    text(d, 80, 560, "Suv haqida bilmoqchi bo'lganlaringizni", fn("Bold", 42), WHITE, ph(t, 0.6))
    a = ph(t, 0.9)
    w = d.textlength("izohlarda yozib qoldiring ↓", font=fn("Bold", 46)) + 60
    d.rounded_rectangle([80, 625, 80 + w, 707], 41, fill=SKY + (int(255 * a),))
    text(d, 110, 640, "izohlarda yozib qoldiring ↓", fn("Bold", 46), NAVY, a, shadow=False)
    text(d, 80, 800, "Bizni kuzatishda davom eting —", fn("SemiBold", 42), WHITE, ph(t, 1.6))
    text(d, 80, 856, "suv haqida suvyektiv fikrlaymiz!", fn("ExtraBold", 52), SKY, ph(t, 2.1))
    text(d, 80, 960, "Doktor H₂O  ·  @suvyektiv", fn("Bold", 40), WHITE, ph(t, 2.6))

SC = {k: v for k, v in globals().items() if k in {s[5] for s in S}}

def ovl(i):
    k, ss, dur, cx, title, name = S[i]
    out = R + f"ov/{name}.mov"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "qtrle", out], stdin=subprocess.PIPE)
    for f in range(int((dur + 0.5) * FPS)):
        t = f / FPS; im = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(im)
        hud(d, i, t); chapter(d, title, t); SC[name](d, t, im)
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()

def gfx():
    import os; os.makedirs(R + "ov", exist_ok=True)
    # top gradient for legibility (footage stays visible)
    g = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(g)
    for y in range(1150):
        d.line([(0, y), (W, y)], fill=(5, 15, 25, int(175 * (1 - y / 1150) ** 1.1)))
    g.save(R + "ov/grad.png")
    for i in range(len(S)): ovl(i)

def build(out, caps=True):
    XF = 0.3; inputs, fc = [], []
    n = lambda: sum(1 for x in inputs if x == "-i")
    inputs += ["-loop", "1", "-i", R + "ov/grad.png"]; gi = 0
    fc.append(f"[{gi}:v]format=rgba,split={len(S)}" + "".join(f"[g{i}]" for i in range(len(S))))
    for i, (k, ss, dur, cx, title, name) in enumerate(S):
        L = dur + XF
        inputs += ["-ss", str(ss), "-i", R + f"px/{k}.mp4"]; vi = n() - 1
        inputs += ["-i", R + f"ov/{name}.mov"]; oi = n() - 1
        extra = {"A0": ",eq=brightness=-0.16:contrast=1.1,gblur=sigma=3", "B3": ",gblur=sigma=4,eq=brightness=-0.06", "D5": ",gblur=sigma=2"}.get(k, "")
        fc.append(f"[{vi}:v]fps=30,trim=0:{L:.3f},setpts=PTS-STARTPTS,scale=w=-2:h='1920*(1.0+0.04*t/{L:.3f})':eval=frame:flags=bicubic,"
                  f"crop=1080:1920:(iw-1080)*{cx}:(ih-1920)/2,setsar=1,eq=saturation=0.88:contrast=1.06:gamma=0.97{extra},format=rgba[b{i}];"
                  f"[g{i}]trim=0:{L:.3f},setpts=PTS-STARTPTS[gg{i}];[b{i}][gg{i}]overlay=format=auto[bg{i}];"
                  f"[{oi}:v]trim=0:{L:.3f},setpts=PTS-STARTPTS,format=rgba[o{i}];[bg{i}][o{i}]overlay=format=auto,format=yuv420p,settb=1/30[s{i}]")
    cur, off = "s0", S[0][2]
    for i in range(1, len(S)):
        tr = "slideup" if i in (2, 4, 6) else "fade"
        fc.append(f"[{cur}][s{i}]xfade=transition={tr}:duration={XF}:offset={off:.3f}[x{i}]"); cur = f"x{i}"; off += S[i][2]
    last = cur
    if caps:
        inputs += ["-i", R + "ov/caps.mov"]; ci = n() - 1
        fc.append(f"[{cur}][{ci}:v]overlay=format=auto[cv]"); last = "cv"
    fc.append(f"[{last}]fade=in:d=0.3,fade=out:st={off - 0.6:.3f}:d=0.6,format=yuv420p[V]")
    inputs += ["-i", R + "ov/music.wav"]; mi = n() - 1
    fc.append(f"[{mi}:a]atrim=0:{off:.3f},afade=t=out:st={off - 1.5:.3f}:d=1.5,loudnorm=I=-16:TP=-1.5[A]")
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + inputs + ["-filter_complex", ";".join(fc), "-map", "[V]", "-map", "[A]", "-t", f"{off:.3f}",
                    "-c:v", "libx264", "-crf", "20", "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
    for i, s in enumerate(S): print(f"{STARTS[i]:5.1f}s {s[0]:3s} {s[5]}")
    print("total", round(off, 1))

if __name__ == "__main__":
    if sys.argv[1] == "gfx": gfx()
    else: build(sys.argv[2], caps="--nocaps" not in sys.argv)
