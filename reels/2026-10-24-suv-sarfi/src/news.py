"""Serious news/documentary version of the 4 778 L reel.
Real footage everywhere; data scenes = clean white cards over softly blurred real footage; lower-thirds on B-roll;
calm captions (white bold, key words in brand sky-blue, no bounce); simple dissolves.
usage: news.py gfx | build out.mp4 [--nocaps]"""
import sys, math, subprocess, re, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R = "/home/claude/r2/"
W, H, FPS = 1080, 1920, 30
F = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
fn = lambda w, s: ImageFont.truetype(F.format(w), s)
NAVY, SKY, SKYD, GREY, LIGHT, REDC = (11, 31, 51), (132, 210, 253), (31, 111, 178), (110, 122, 135), (233, 244, 252), (210, 64, 60)
def ease(u): u = max(0, min(1, u)); return 1 - (1 - u) ** 3
def ph(t, t0, d=0.45): return ease((t - t0) / d)
def fmt(n): return f"{int(round(n)):,}".replace(",", " ")

def card(d, x0, y0, x1, y1, a=1.0):
    d.rounded_rectangle([x0, y0 + 10, x1, y1 + 10], 28, fill=(0, 0, 0, int(60 * a)))
    d.rounded_rectangle([x0, y0, x1, y1], 28, fill=(255, 255, 255, int(244 * a)))
def txt(d, x, y, s, f, col, a=1.0, anchor="la"):
    if a > 0: d.text((x, y + (1 - a) * 18), s, font=f, fill=col + (int(255 * a),), anchor=anchor)
def head(d, t, tag, title, sub=None):
    a = ph(t, 0, 0.4)
    card(d, 60, 250, 1020, 1050, a)
    tw = d.textlength(tag, font=fn("Bold", 30))
    d.rounded_rectangle([110, 300, 110 + tw + 36, 348], 10, fill=SKY + (int(255 * a),))
    txt(d, 128, 306, tag, fn("Bold", 30), NAVY, a)
    txt(d, 110, 372, title, fn("ExtraBold", 54), NAVY, a)
    if sub: txt(d, 110, 442, sub, fn("Medium", 34), GREY, a)
def src(d, t, s, t0=0.8): txt(d, 110, 1000, s, fn("Medium", 26), GREY, ph(t, t0))

def scene_calc(t):
    im = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(im)
    head(d, t, "HISOB", "4 778 litr qayerdan chiqadi?")
    rows = [(0.6, "Yillik suv olinishi", "54,56 mlrd m³"), (1.5, "Bir kunga", "÷ 365"), (2.2, "Aholi soniga*", "÷ 31,3 mln")]
    y = 470
    for t0, lab, val in rows:
        a = ph(t, t0); txt(d, 110, y, lab, fn("Medium", 34), GREY, a); txt(d, 970, y - 12, val, fn("ExtraBold", 58), NAVY, a, "ra"); y += 80
    a = ph(t, 3.0, 0.4); d.line([(110, y + 4), (110 + 860 * a, y + 4)], fill=SKY + (255,), width=6)
    a = ph(t, 3.3)
    txt(d, 110, y + 30, "Kishi boshiga, kuniga", fn("SemiBold", 36), NAVY, a)
    txt(d, 970, y + 8, f"{fmt(4778 * ph(t, 3.3, 1.0))} L", fn("Black", 96), SKYD, a, "ra")
    a = ph(t, 5.0)
    if a > 0:
        d.rounded_rectangle([110, 845, 970, 965], 18, fill=LIGHT + (int(255 * a),))
        txt(d, 140, 860, "Bugungi 39 mln aholi bilan: ≈ 3 830 L", fn("Bold", 38), NAVY, a)
        txt(d, 140, 914, "O'rtacha raqam: har kim va har hudud uchun har xil", fn("Medium", 30), GREY, ph(t, 5.8))
    src(d, t, "*2016 yil aholisi · Manba: Worldometer (BMT, FAO); stat.uz", 1.0)
    return im

def cube(d, x, y, sz, fill, a):
    """isometric 1 m³ cube outline with water level `fill` (0..1)"""
    dx, dy = sz * 0.5, sz * 0.28
    A = (x, y + dy); B = (x + sz, y + dy); C = (x + sz + dx, y); D = (x + dx, y)
    A2 = (A[0], A[1] + sz); B2 = (B[0], B[1] + sz); C2 = (C[0], C[1] + sz)
    if fill > 0:
        h = sz * fill
        d.polygon([(A2[0], A2[1] - h), (B2[0], B2[1] - h), (C2[0], C2[1] - h), (C2[0] - 0, C2[1]), B2, A2], fill=SKY + (int(235 * a),))
        d.polygon([(A2[0], A2[1] - h), (B2[0], B2[1] - h), (C2[0], C2[1] - h), (D[0], D[1] + sz - h)], fill=(170, 225, 254, int(255 * a)))
    col = NAVY + (int(255 * a),)
    for p, q in [(A, B), (B, C), (C, D), (D, A), (A, A2), (B, B2), (C, C2), (A2, B2), (B2, C2)]:
        d.line([p, q], fill=col, width=5)
def scene_tubs(t):
    im = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(im)
    head(d, t, "TAQQOSLASH", "4 778 litr — bu qancha?", "1 m³ = 1 000 litr ≈ 1 tonna")
    vals = [1, 1, 1, 1, 0.78]
    for i, v in enumerate(vals):
        a = ph(t, 0.4 + i * 0.15, 0.3); f = v * ph(t, 0.8 + i * 0.35, 0.45)
        cube(d, 104 + i * 174, 545, 106, f, a)
    k = sum(v * ph(t, 0.8 + i * 0.35, 0.45) for i, v in enumerate(vals))
    txt(d, 540, 735, f"≈ {k:.1f} m³".replace(".", ","), fn("Black", 92), SKYD, ph(t, 0.8), "ma")
    txt(d, 540, 845, "har bir kishiga, har kuni — deyarli 5 tonna suv", fn("SemiBold", 36), NAVY, ph(t, 2.8), "ma")
    txt(d, 540, 905, "bir yilda: ≈ 1 744 m³", fn("Bold", 38), GREY, ph(t, 3.4), "ma")
    src(d, t, "4 778 L × 365 kun ≈ 1 744 m³ · o'rtacha ko'rsatkich", 3.6)
    return im

DATA = [("Turkmaniston", 15445), ("Chili", 5880), ("Gayana", 5284), ("O'zbekiston", 4778), ("Tojikiston", 4460),
        ("Qirg'iziston", 4153), ("Eron", 3638), ("Estoniya", 3585), ("Ozarbayjon", 3512), ("Sharqiy Timor", 3456)]
def scene_rank(t):
    im = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(im)
    head(d, t, "REYTING", "Kishi boshiga suv olinishi", "TOP-10 · litr / kun")
    y0, row = 496, 43
    for i, (name, v) in enumerate(DATA):
        a = ph(t, 0.5 + i * 0.12, 0.35); y = y0 + i * row; uz = name == "O'zbekiston"
        if uz and a > 0: d.rounded_rectangle([90, y - 6, 990, y + 40], 10, fill=LIGHT + (int(255 * a),))
        col = NAVY if uz else (60, 72, 86)
        txt(d, 110, y, f"{i + 1}", fn("Bold", 32), GREY if not uz else SKYD, a)
        txt(d, 160, y, name, fn("Bold" if uz else "SemiBold", 32), col, a)
        L = 420 * v / 15445 * ph(t, 0.6 + i * 0.12, 0.8)
        bc = SKYD if uz else (SKY if i == 0 else (196, 208, 220))
        if L > 1: d.rounded_rectangle([420, y + 6, 420 + L, y + 32], 6, fill=bc + (int(255 * a),))
        txt(d, 970, y, fmt(v * ph(t, 0.6 + i * 0.12, 0.8)), fn("Bold", 32), col, a, "ra")
    a = ph(t, 2.4)
    txt(d, 110, 930, "Top-10 ning 4 tasi — Markaziy Osiyodan", fn("SemiBold", 32), SKYD, a)
    src(d, t, "Manba: Worldometer (BMT, FAO) · ma'lumot yillari turlicha", 2.6)
    return im

def scene_split(t):
    im = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(im)
    head(d, t, "TAQSIMOT", "4 778 litr qayerga ketadi?", "kishi boshiga, kuniga")
    x0, x1 = 110, 970; Wd = x1 - x0
    a = ph(t, 0.5); p = ph(t, 0.7, 1.0)
    txt(d, x0, 520, "Qishloq xo'jaligi — 90%+", fn("Bold", 36), NAVY, a)
    d.rounded_rectangle([x0, 575, x1, 640], 12, fill=(214, 223, 232, int(255 * a)))
    if p > 0: d.rounded_rectangle([x0, 575, x0 + Wd * 0.9 * p, 640], 12, fill=SKY + (255,))
    txt(d, x0 + 20, 588, "≈ 4 300 L", fn("ExtraBold", 38), NAVY, ph(t, 1.4))
    txt(d, x1 - 10, 652, "uy va sanoat ≈ 10%", fn("Medium", 28), GREY, ph(t, 1.6), "ra")
    a = ph(t, 2.6); q = ph(t, 2.9, 1.0)
    txt(d, x0, 730, "Shundan tuproq kanallarda yo'qoladi — 36%", fn("Bold", 36), NAVY, a)
    d.rounded_rectangle([x0, 785, x0 + Wd * 0.9, 850], 12, fill=SKY + (int(255 * a),))
    if q > 0: d.rounded_rectangle([x0, 785, x0 + Wd * 0.9 * 0.36 * q, 850], 12, fill=REDC + (255,))
    txt(d, x0 + 20, 798, "≈ 1 550 L", fn("ExtraBold", 38), (255, 255, 255), ph(t, 3.6))
    txt(d, x0, 880, "Yiliga 14 mlrd m³ dan ortiq suv dalaga yetib bormaydi.", fn("SemiBold", 32), REDC, ph(t, 4.3))
    src(d, t, "Manba: Prezident matbuot xizmati (2023) · Worldometer", 1.0)
    return im

def scene_cta(t):
    im = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(im)
    a = ph(t, 0, 0.4)
    card(d, 60, 330, 1020, 1030, a)
    txt(d, 540, 400, "Suv haqida yana nimalarni", fn("ExtraBold", 58), NAVY, a, "ma")
    txt(d, 540, 472, "bilmoqchisiz?", fn("ExtraBold", 58), NAVY, a, "ma")
    a2 = ph(t, 0.6)
    if a2 > 0:
        w = d.textlength("Izohlarda yozib qoldiring", font=fn("Bold", 44)) + 120
        d.rounded_rectangle([540 - w / 2, 575, 540 + w / 2, 655], 40, fill=SKY + (int(255 * a2),))
        txt(d, 540, 590, "Izohlarda yozib qoldiring", fn("Bold", 44), NAVY, a2, "ma")
        ay = 690 + 10 * math.sin(t * 5)                       # small bouncing arrow
        d.line([(540, ay), (540, ay + 46)], fill=NAVY + (int(255 * a2),), width=7)
        d.polygon([(518, ay + 34), (562, ay + 34), (540, ay + 62)], fill=NAVY + (int(255 * a2),))
    a3 = ph(t, 1.4)
    d.line([(160, 790), (920, 790)], fill=(214, 223, 232, int(255 * a3)), width=3)
    txt(d, 540, 815, "Bizni kuzatishda davom eting —", fn("SemiBold", 40), GREY, a3, "ma")
    txt(d, 540, 868, "suv haqida suvyektiv fikrlaymiz!", fn("ExtraBold", 46), SKYD, ph(t, 1.9), "ma")
    txt(d, 540, 950, "Doktor H₂O  ·  @suvyektiv", fn("Bold", 36), NAVY, ph(t, 2.4), "ma")
    return im

def lower_third(title, sub):
    im = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(im)
    f1, f2 = fn("ExtraBold", 58), fn("SemiBold", 34)
    w = max(d.textlength(title, font=f1), d.textlength(sub, font=f2) if sub else 0) + 70
    y = 820; h = 150 if sub else 100
    d.rounded_rectangle([60, y + 8, 60 + w, y + h + 8], 14, fill=(0, 0, 0, 60))
    d.rounded_rectangle([60, y, 60 + w, y + h], 14, fill=(255, 255, 255, 246))
    d.rounded_rectangle([60, y, 74, y + h], 6, fill=SKY + (255,))
    d.text((100, y + 16), title, font=f1, fill=NAVY)
    if sub: d.text((100, y + 92), sub, font=f2, fill=GREY)
    return im

def ovl_video(name, dur, fnc):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "qtrle", R + f"nw/{name}.mov"], stdin=subprocess.PIPE)
    for f in range(int(dur * FPS)): p.stdin.write(fnc(f / FPS).tobytes())
    p.stdin.close(); p.wait()

# file, start, dur, crop-x, kind, payload
S = [("Z1", 4.5, 5.0, .33, "lt", ("4 778 litr", "kishi boshiga, har kuni")),
     ("Z1", 0.5, 8.5, .33, "data", "calc"),
     ("A6", 1.0, 5.0, .45, "data", "tubs"),
     ("G6", 0.0, 3.0, .50, "lt", ("Dunyoda 4-o'rin", "kishi boshiga suv olinishi")),
     ("TK0", 2.0, 3.5, .20, "lt", ("1-o'rin: Turkmaniston", "kuniga 15 445 litr")),
     ("G2", 2.0, 7.5, .38, "data", "rank"),
     ("Q0", 0.0, 2.5, .50, "lt", ("90%+ suv dalalarga", "paxta · bug'doy · sholi")),
     ("U2", 2.0, 3.5, .50, "lt", ("Qishloq xo'jaligi", "suvning asosiy iste'molchisi")),
     ("C2", 5.0, 7.0, .50, "data", "split"),
     ("D0", 1.0, 4.5, .50, "lt", ("36% yo'qoladi", "tuproq kanallar va ariqlarda")),
     ("V5", 2.0, 4.0, .50, "lt", ("14 mlrd m³", "har yili yerga singib, bug'lanib")),
     ("T4", 5.0, 2.5, .50, "lt", ("Beton kanallar", "yo'qotishni kamaytiradi")),
     ("W5", 3.0, 2.0, .62, "lt", ("Zamonaviy sug'orish", "tomchilatib, yomg'irlatib")),
     ("T0", 12.0, 6.0, .50, "data", "cta")]
SC = {"cta": scene_cta, "calc": scene_calc, "tubs": scene_tubs, "rank": scene_rank, "split": scene_split}

def gfx():
    import os; os.makedirs(R + "nw", exist_ok=True)
    for i, (k, ss, dur, cx, kind, pay) in enumerate(S):
        if kind == "data": ovl_video(pay, dur + 0.5, SC[pay])
        else: lower_third(*pay).save(R + f"nw/lt_{i}.png")

def build(out, caps=True):
    XF = 0.35; inputs, fc = [], []
    for i, (k, ss, dur, cx, kind, pay) in enumerate(S):
        L = dur + XF
        inputs += ["-ss", str(ss), "-i", R + f"px/{k}.mp4"]
        vi = len([x for x in inputs if x == "-i"]) - 1
        base = (f"[{vi}:v]fps=30,trim=0:{L:.3f},setpts=PTS-STARTPTS,scale=w=-2:h='1920*(1.0+0.035*t/{L:.3f})':eval=frame:flags=bicubic,"
                f"crop=1080:1920:(iw-1080)*{cx}:(ih-1920)/2,setsar=1,eq=saturation=0.95:contrast=1.04")
        if kind == "data":
            inputs += ["-i", R + f"nw/{pay}.mov"]; oi = vi + 1
            fc.append(base + f",gblur=sigma=14,eq=brightness=-0.04,format=yuv420p[b{i}];[{oi}:v]trim=0:{L:.3f},setpts=PTS-STARTPTS,format=rgba[o{i}];"
                      f"[b{i}][o{i}]overlay=format=auto,format=yuv420p,settb=1/30[s{i}]")
        else:
            inputs += ["-loop", "1", "-i", R + f"nw/lt_{i}.png"]; oi = vi + 1
            fc.append(base + f",format=yuv420p[b{i}];[{oi}:v]trim=0:{L:.3f},setpts=PTS-STARTPTS,format=rgba,"
                      f"fade=in:st=0.3:d=0.3:alpha=1,fade=out:st={L - 0.65:.3f}:d=0.3:alpha=1[o{i}];[b{i}][o{i}]overlay=format=auto,format=yuv420p,settb=1/30[s{i}]")
    cur, off = "s0", S[0][2]
    for i in range(1, len(S)):
        fc.append(f"[{cur}][s{i}]xfade=transition=fade:duration={XF}:offset={off:.3f}[x{i}]"); cur = f"x{i}"; off += S[i][2]
    total = off
    last = cur
    if caps:
        inputs += ["-i", R + "nw/caps.mov"]; ci = len([x for x in inputs if x == "-i"]) - 1
        fc.append(f"[{cur}][{ci}:v]overlay=format=auto[cv]"); last = "cv"
    fc.append(f"[{last}]fade=in:d=0.3,fade=out:st={total - 0.6:.3f}:d=0.6,format=yuv420p[V]")
    inputs += ["-i", R + "nw/music.wav"]; mi = len([x for x in inputs if x == "-i"]) - 1
    fc.append(f"[{mi}:a]atrim=0:{total:.3f},afade=t=out:st={total - 1.5:.3f}:d=1.5,loudnorm=I=-16:TP=-1.5[A]")
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + inputs + ["-filter_complex", ";".join(fc), "-map", "[V]", "-map", "[A]", "-t", f"{total:.3f}",
                    "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
    t = 0
    for k, ss, dur, cx, kind, pay in S: print(f"{t:5.1f}s {k:4s} {kind} {pay}"); t += dur
    print("total", round(total, 1))

# calm captions: white bold, key words sky-blue, quick fade, max ~24 chars per line
KEY = re.compile(r"\d|%|litr|o'rin|vanna|dala|yo'qol|milliard|kub|turkmaniston|o'zbekiston|kanal|o'rtacha", re.I)
def caps_render(lines, dur, out, y=1180):
    f = fn("Bold", 64); ev = []
    for a, b, s in lines:
        s = re.sub(r"(\d) (\d)", "\\1\u00a0\\2", s); words = s.split(" "); chunks = []; cur = []
        for w in words:
            if cur and len(" ".join(cur + [w])) > 24: chunks.append(cur); cur = []
            cur.append(w)
        chunks.append(cur); tot = sum(len(" ".join(c)) for c in chunks); t = a
        for c in chunks:
            d_ = (b - a) * len(" ".join(c)) / tot; ev.append((t, t + d_, c)); t += d_
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "qtrle", out], stdin=subprocess.PIPE)
    for fr in range(int(dur * FPS)):
        t = fr / FPS; im = Image.new("RGBA", (W, H))
        cur = [e for e in ev if e[0] <= t < e[1]]
        if cur:
            t0, t1, ws = cur[0]; al = min(1, (t - t0) / 0.08, (t1 - t) / 0.06)
            lay = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(lay)
            widths = [d.textlength(w, font=f) for w in ws]; sp = d.textlength(" ", font=f)
            x = (W - sum(widths) - sp * (len(ws) - 1)) / 2
            for w, wd in zip(ws, widths):
                d.text((x, y), w, font=f, fill=(SKY if KEY.search(w) else (255, 255, 255)) + (255,), stroke_width=3, stroke_fill=(0, 0, 0, 160))
                x += wd + sp
            sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sh.putalpha(lay.getchannel("A").point(lambda v: int(v * 0.6)))
            sh = sh.filter(ImageFilter.GaussianBlur(10)); im.alpha_composite(sh, (0, 5)); im.alpha_composite(lay)
            if al < 1: im.putalpha(im.getchannel("A").point(lambda v: int(v * max(0, al))))
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()

if __name__ == "__main__":
    if sys.argv[1] == "gfx": gfx()
    elif sys.argv[1] == "build": build(sys.argv[2], caps="--nocaps" not in sys.argv)
