"""'Toshkent kran suvi qanday tozalanadi' reel — BLUEPRINT JOURNEY style: one long engineering drawing (light
blueprint grid) with a vertical water main; the camera travels DOWN the pipe station by station (intake →
screens → coagulation → settling → filtration → chlorine → lab → city). Real Kodiriya photos (Fergana.agency)
in rounded windows. Hook and CTA are full-bleed real footage with big type. Captions: same renderer as before.
usage: journey.py seg [0 1 2] | caps | still t out.png | build out.mp4 [--nocaps]"""
import sys, re, math, subprocess
sys.path.insert(0, "/home/claude/r2")
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R = "/home/claude/r6/"
W, H, FPS = 1080, 1920, 30
F = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
_fc = {}
def fn(w, s):
    if (w, s) not in _fc: _fc[(w, s)] = ImageFont.truetype(F.format(w), s)
    return _fc[(w, s)]
WHITE, SKY, SKYD, NAVY, WARN, OK = (255, 255, 255), (132, 210, 253), (31, 111, 178), (11, 31, 51), (226, 88, 62), (46, 160, 105)
BP, GRID, INK2 = (236, 245, 252), (214, 230, 243), (70, 88, 108)
def ease(u): u = max(0, min(1, u)); return u * u * (3 - 2 * u)
def eout(u): u = max(0, min(1, u)); return 1 - (1 - u) ** 3
def ph(t, t0, d=0.5): return eout((t - t0) / d)
def back(u): u = max(0, min(1, u)); c = 1.7; return 1 + (c + 1) * (u - 1) ** 3 + c * (u - 1) ** 2

CAP = {
 "hook": "Kranni ochasiz — suv keladi. Lekin u qayerdan keladi va qanday tozalanadi? Keling, uning yo'lini kuzatamiz.",
 0: "Toshkent suvining katta qismi Chirchiq daryosidan ajralgan Bo'zsuv kanali orqali Qodiriya suv inshootiga keladi.",
 1: "Birinchi bosqich — panjara va to'rlar: baliq, suv o'tlari va axlat shu yerda ushlanadi.",
 2: "Keyin suvga achchiqtosh, ya'ni alyuminiyli koagulyant qo'shiladi. U mayda loyqa zarralarni bir-biriga yopishtiradi.",
 3: "Og'irlashgan bo'laklar hovuz tubiga cho'kadi. Suzuvchi nasoslar bu loyqani tortib oladi.",
 4: "Tiniqlashgan suv shag'al va kvars qum qatlamlaridan sekin o'tadi. Filtrlar muntazam yuviladi.",
 5: "Oxirida xlor qo'shiladi: u bakteriya va viruslarni yo'q qiladi va quvurlarda ham suvni himoya qiladi.",
 6: "Laboratoriyada suv davlat standarti bo'yicha 40 ta ko'rsatkichga tekshiriladi.",
 7: "Shu yo'l bilan poytaxtga har kuni 1,8 dan 2,3 million kub metrgacha ichimlik suvi yetkaziladi.",
 "cta": "Suvni qadrlang! Suv haqida bilmoqchi bo'lganlaringizni izohlarda yozib qoldiring. Bizni kuzatishda davom eting, suv haqida suvyektiv fikrlaymiz!"}
DUR = [7.5, 5.5, 7.5, 6.0, 7.0, 7.0, 5.5, 7.0]          # blueprint stations
HOOK, CTA, XF = 6.0, 6.5, 0.3
BPT = sum(DUR)
ST = [sum(DUR[:k]) for k in range(len(DUR))]
SPAN = 1400; Y0 = 260                                       # canvas distance between stations, screen y of station top
PX = 112                                                    # pipe x

_im = {}
def photo(n):
    if n not in _im: _im[n] = Image.open(R + f"ph/{n}.jpg").convert("RGB")
    return _im[n]

# ---------- static blueprint background (tall) ----------
def make_bg():
    h = Y0 + SPAN * len(DUR) + H
    im = Image.new("RGB", (W, h), BP); d = ImageDraw.Draw(im)
    for x in range(0, W, 40): d.line([(x, 0), (x, h)], fill=GRID, width=1 if x % 200 else 2)
    for y in range(0, h, 40): d.line([(0, y), (W, y)], fill=GRID, width=1 if y % 200 else 2)
    return im
BG = None

def window(fr, name, box, t, credit=None, zoom=0.07, a=1.0):
    x0, y0, x1, y1 = [int(v) for v in box]
    if a <= 0 or y1 < 0 or y0 > H: return
    p = photo(name); w, h = x1 - x0, y1 - y0
    s = max(w / p.width, h / p.height) * (1 + zoom * min(1, t / 7))
    pw, phh = int(p.width * s), int(p.height * s)
    sub = p.resize((pw, phh), Image.BILINEAR).crop(((pw - w) // 2, (phh - h) // 2, (pw - w) // 2 + w, (phh - h) // 2 + h))
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], 26, fill=int(255 * a))
    sh = Image.new("RGBA", (W, H)); ImageDraw.Draw(sh).rounded_rectangle([x0 + 6, y0 + 14, x1 + 6, y1 + 14], 26, fill=(11, 31, 51, int(70 * a)))
    fr.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    fr.paste(sub, (x0, y0), m)
    d = ImageDraw.Draw(fr); d.rounded_rectangle([x0, y0, x1, y1], 26, outline=NAVY + (int(255 * a),), width=4)
    if credit:
        d.text((x1 - 16, y1 - 16), "Foto: " + credit, font=fn("SemiBold", 22), fill=WHITE + (int(230 * a),), anchor="rd", stroke_width=2, stroke_fill=(0, 0, 0, 120))

def chip(d, x, y, s, a, col=NAVY, fg=WHITE, size=40):
    if a <= 0: return 0
    f = fn("ExtraBold", size); w = d.textlength(s, font=f) + 50; yy = y + (1 - a) * 20
    d.rounded_rectangle([x, yy, x + w, yy + size + 34], (size + 34) // 2, fill=col + (int(240 * a),))
    d.text((x + 25, yy + 15), s, font=f, fill=fg + (int(255 * a),))
    return w

def label(d, x, y, s, f, col, a=1.0, anchor="la"):
    if a <= 0: return
    d.text((x, y + (1 - a) * 18), s, font=f, fill=col + (int(255 * a),), anchor=anchor)

# ---------- station drawers (y0 = screen y of station top; t = local time since station became active, may be <0) ----------
TITLES = ["MANBA", "PANJARA", "KOAGULYATSIYA", "CHO'KTIRISH", "FILTRLASH", "XLORLASH", "LABORATORIYA", "SHAHARGA"]
def node(d, k, y0, active):
    cy = y0 + 44
    d.ellipse([PX - 46, cy - 46, PX + 46, cy + 46], fill=(SKYD if active else WHITE) + (255,), outline=NAVY + (255,), width=5)
    d.text((PX, cy), str(k + 1), font=fn("Black", 44), fill=(WHITE if active else NAVY) + (255,), anchor="mm")

def head(d, k, y0, t):
    label(d, 190, y0, f"BOSQICH {k + 1}/8", fn("Bold", 28), SKYD, ph(t, 0.0))
    label(d, 190, y0 + 34, TITLES[k], fn("Black", 64), NAVY, ph(t, 0.1))

def st0(fr, d, y0, t):
    head(d, 0, y0, t)
    window(fr, "river", (190, y0 + 130, 1010, y0 + 600), t, None, a=ph(t, 0.2))
    window(fr, "canal", (590, y0 + 560, 1010, y0 + 860), t, "Fergana.agency", a=ph(t, 2.4))
    label(d, 200, y0 + 640, "Chirchiq daryosi", fn("ExtraBold", 40), NAVY, ph(t, 1.0))
    label(d, 200, y0 + 700, "↓ Bo'zsuv kanali", fn("Bold", 36), SKYD, ph(t, 2.0))
    label(d, 200, y0 + 750, "↓ Qodiriya", fn("Bold", 36), SKYD, ph(t, 3.2))

def st1(fr, d, y0, t):
    head(d, 1, y0, t)
    window(fr, "intake", (190, y0 + 130, 1010, y0 + 680), t, "Fergana.agency", a=ph(t, 0.2))
    # grate graphic: bars that "catch" items
    a = ph(t, 1.2)
    if a > 0:
        gx, gy = 200, y0 + 720
        for i in range(9): d.line([(gx + i * 34, gy), (gx + i * 34, gy + 110)], fill=NAVY + (int(255 * a),), width=6)
        label(d, 520, gy + 4, "× baliq", fn("Bold", 36), WARN, ph(t, 1.6))
        label(d, 520, gy + 44, "× suv o'tlari", fn("Bold", 36), WARN, ph(t, 2.0))
        label(d, 520, gy + 84, "× axlat", fn("Bold", 36), WARN, ph(t, 2.4))

def st2(fr, d, y0, t):
    head(d, 2, y0, t)
    window(fr, "dredge", (190, y0 + 130, 1010, y0 + 620), t, "Fergana.agency", a=ph(t, 0.2))
    # particles clumping: 18 dots drift together into 3 flocs
    a = ph(t, 1.5); box = (200, y0 + 660, 1000, y0 + 870)
    if a > 0:
        d.rounded_rectangle(box, 22, fill=WHITE + (int(235 * a),), outline=SKYD + (int(255 * a),), width=3)
        u = ease((t - 2.3) / 2.2); import random; rnd = random.Random(5)
        cents = [(330, y0 + 775), (600, y0 + 775), (870, y0 + 775)]
        for i in range(24):
            cx, cy = cents[i % 3]; sx, sy = rnd.uniform(220, 980), rnd.uniform(y0 + 710, y0 + 850)
            jx, jy = rnd.uniform(-22, 22), rnd.uniform(-18, 18)
            x, y = sx + (cx + jx - sx) * u, sy + (cy + jy - sy) * u
            r = 7 + 3 * u
            d.ellipse([x - r, y - r, x + r, y + r], fill=(150, 120, 80, int(255 * a)))
        label(d, 220, y0 + 672, "loyqa zarralari", fn("SemiBold", 26), INK2, a * (1 - u))
        label(d, 220, y0 + 672, "yirik bo'laklar (flokulalar)", fn("SemiBold", 26), INK2, u)
    chip(d, 200, y0 + 1060, "+ achchiqtosh (Al³⁺ koagulyant)", ph(t, 1.0), SKYD)

def st3(fr, d, y0, t):
    head(d, 3, y0, t)
    window(fr, "pond", (190, y0 + 130, 1010, y0 + 620), t, "Fergana.agency", a=ph(t, 0.2))
    a = ph(t, 1.2); bx0, by0, bx1, by1 = 200, y0 + 660, 1000, y0 + 870
    if a > 0:
        d.rounded_rectangle([bx0, by0, bx1, by1], 22, fill=(206, 233, 250, int(255 * a)), outline=SKYD + (255,), width=3)
        u = ease((t - 1.6) / 2.6)
        import random; rnd = random.Random(9)
        for i in range(26):
            x = rnd.uniform(bx0 + 20, bx1 - 20); ys = rnd.uniform(by0 + 20, by1 - 70)
            y = ys + (by1 - 22 - ys) * u
            d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=(150, 120, 80, int(255 * a)))
        d.rectangle([bx0 + 6, by1 - 18 * u - 6, bx1 - 6, by1 - 6], fill=(150, 120, 80, int(200 * a)))
        label(d, bx1 - 20, by0 + 14, "tiniq suv ↑", fn("Bold", 30), SKYD, ph(t, 3.6), "ra")
        label(d, bx0 + 20, by0 + 14, "loyqa ↓", fn("Bold", 30), (130, 95, 50), ph(t, 2.2))

def st4(fr, d, y0, t):
    head(d, 4, y0, t)
    window(fr, "filters", (190, y0 + 130, 1010, y0 + 640), t, "Fergana.agency", a=ph(t, 0.2))
    layers = [("suv", (206, 233, 250), 1.2), ("kvars qum", (232, 214, 170), 1.8), ("mayda shag'al", (196, 182, 160), 2.4), ("shag'al", (160, 150, 140), 3.0)]
    y = y0 + 680
    for s, col, t0 in layers:
        a = ph(t, t0)
        if a <= 0: break
        d.rectangle([200, y, 200 + 800 * a, y + 44], fill=col + (255,), outline=NAVY + (255,), width=2)
        label(d, 220, y + 6, s, fn("Bold", 28), NAVY, a)
        y += 46
    # droplets running through
    if t > 3.4:
        for i in range(6):
            yy = y0 + 680 + ((t * 120 + i * 33) % 184)
            d.ellipse([870 - 7, yy - 9, 870 + 7, yy + 9], fill=SKYD + (255,))

def st5(fr, d, y0, t):
    head(d, 5, y0, t)
    a = ph(t, 0.2)
    if a > 0:   # no photo: big Cl2 molecule on a card
        d.rounded_rectangle([190, y0 + 130, 1010, y0 + 560], 26, fill=WHITE + (int(250 * a),), outline=NAVY + (255,), width=4)
        s = back(min(1, max(0, (t - 0.2) / 0.7)))
        for cx in (490, 710):
            r = 92 * s
            d.ellipse([cx - r, y0 + 330 - r, cx + r, y0 + 330 + r], fill=(196, 236, 160, 255), outline=NAVY + (255,), width=6)
            d.text((cx, y0 + 330), "Cl", font=fn("Black", int(70 * max(0.1, s))), fill=NAVY + (255,), anchor="mm")
        label(d, 600, y0 + 470, "xlor · Cl₂", fn("ExtraBold", 40), NAVY, ph(t, 0.8), "ma")
    label(d, 200, y0 + 610, "× bakteriyalar", fn("ExtraBold", 44), WARN, ph(t, 1.8))
    label(d, 200, y0 + 670, "× viruslar", fn("ExtraBold", 44), WARN, ph(t, 2.4))
    chip(d, 200, y0 + 1060, "qoldiq xlor quvurda ham himoya qiladi", ph(t, 3.6), OK, size=36)

def st6(fr, d, y0, t):
    head(d, 6, y0, t)
    window(fr, "lab", (190, y0 + 130, 1010, y0 + 680), t, "Fergana.agency", a=ph(t, 0.2))
    n = int(40 * ph(t, 1.0, 1.6))
    label(d, 200, y0 + 710, f"{n}", fn("Black", 120), SKYD, ph(t, 0.8))
    label(d, 370, y0 + 736, "ta ko'rsatkich", fn("ExtraBold", 48), NAVY, ph(t, 1.2))
    label(d, 370, y0 + 796, "O'zDSt 951-2011", fn("Bold", 32), INK2, ph(t, 1.8))

def st7(fr, d, y0, t):
    head(d, 7, y0, t)
    a = ph(t, 0.2)
    if a > 0:
        d.rounded_rectangle([190, y0 + 130, 1010, y0 + 620], 26, fill=WHITE + (int(250 * a),), outline=NAVY + (255,), width=4)
        v = 1.8 + 0.5 * ph(t, 1.2, 1.6)
        label(d, 600, y0 + 170, "har kuni", fn("Bold", 40), INK2, a, "ma")
        label(d, 600, y0 + 230, f"{v:.1f}".replace(".", ",") + " mln m³", fn("Black", 110), SKYD, a, "ma")
        label(d, 600, y0 + 380, "(mavsumga qarab 1,8–2,3 mln)", fn("SemiBold", 30), INK2, ph(t, 1.6), "ma")
        b = ph(t, 3.0)
        if b > 0:
            for i in range(12):        # pool icons
                x = 260 + (i % 6) * 120; y = y0 + 450 + (i // 6) * 70
                d.rounded_rectangle([x, y, x + 100, y + 52], 10, fill=SKY + (int(255 * ph(t, 3.0 + i * 0.06, 0.3)),), outline=NAVY + (255,), width=2)
            label(d, 600, y0 + 640, "≈ 900 ta olimpiya basseyni", fn("ExtraBold", 44), NAVY, ph(t, 3.8), "ma")
    label(d, 200, y0 + 1060, "Manba: UzA (2023), Fergana.agency (2020)", fn("Medium", 26), INK2, ph(t, 1.0))

STATIONS = [st0, st1, st2, st3, st4, st5, st6, st7]

def cam(T):
    """camera = canvas y at screen top. scroll during first 1.0 s of each station"""
    k = max(i for i in range(len(DUR)) if ST[i] <= T)
    u = ease((T - ST[k]) / 1.0) if k > 0 else 1
    return (k - 1 + u) * SPAN if k > 0 else 0, k

def hud(d, k, T):
    d.rectangle([0, 0, W, 205], fill=BP + (230,))
    d.text((80, 112), "KRANGACHA YO'L · TOSHKENT", font=fn("Bold", 30), fill=NAVY + (255,))
    d.text((1000, 112), f"{k + 1:02d}/08", font=fn("Bold", 30), fill=SKYD + (255,), anchor="ra")
    g = T / BPT
    d.line([(80, 164), (1000, 164)], fill=(190, 210, 228, 255), width=4)
    d.line([(80, 164), (80 + 920 * g, 164)], fill=SKYD + (255,), width=4)

def bp_frame(T):
    c, k = cam(T)
    top = int(c)
    fr = BG.crop((0, top, W, top + H)).convert("RGBA"); d = ImageDraw.Draw(fr)
    # pipe (screen coords)
    d.rectangle([PX - 15, 0, PX + 15, H], fill=WHITE + (255,), outline=NAVY + (255,), width=4)
    filled = Y0 + (T / BPT) * SPAN * len(DUR) - top + 600
    d.rectangle([PX - 11, 0, PX + 11, min(H, filled)], fill=SKY + (255,))
    for i in range(40):                                     # flow dashes moving down
        y = ((T * 260 + i * 70) % (H + 70)) - 70
        if y < filled: d.line([(PX, y), (PX, y + 26)], fill=SKYD + (255,), width=6)
    for j in range(len(DUR)):
        y0 = Y0 + j * SPAN - top
        if -SPAN < y0 < H + 100:
            node(d, j, y0, j <= k)
            STATIONS[j](fr, d, y0, T - ST[j] if j <= k else -1)
    # caption backing band
    hud(d, k, T)
    return fr

def _band():
    b = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(b)
    for y in range(1120, 1320):
        u = 1 - abs(y - 1220) / 100; d.line([(0, y), (W, y)], fill=(8, 20, 34, int(165 * min(1, u * 1.6))))
    return b
BAND = _band()

# ---------- full-bleed footage scenes ----------
def big(d, x, y, s, f, col, a, anchor="ma"):
    if a <= 0: return
    y += (1 - a) * 30
    d.text((x + 4, y + 6), s, font=f, fill=(0, 0, 0, int(130 * a)), anchor=anchor)
    d.text((x, y), s, font=f, fill=col + (int(255 * a),), anchor=anchor)

def o_hook(d, t):
    big(d, 540, 330, "Kran suvi", fn("Black", 130), WHITE, ph(t, 0.0))
    big(d, 540, 480, "qayerdan keladi?", fn("ExtraBold", 84), SKY, ph(t, 0.6))
    big(d, 540, 640, "daryodan — stakangacha", fn("Bold", 52), WHITE, ph(t, 2.2))
    big(d, 540, 720, "8 bosqich", fn("Black", 96), WHITE, ph(t, 3.0))

def o_cta(d, t):
    big(d, 540, 360, "Suvni", fn("Black", 150), WHITE, ph(t, 0.0))
    big(d, 540, 520, "qadrlang!", fn("Black", 150), SKY, ph(t, 0.2))
    big(d, 540, 760, "Suv haqida bilmoqchi bo'lganlaringizni", fn("Bold", 42), WHITE, ph(t, 0.8))
    a = ph(t, 1.1); w = d.textlength("izohlarda yozib qoldiring ↓", font=fn("Bold", 46)) + 70
    d.rounded_rectangle([(W - w) / 2, 820, (W + w) / 2, 910], 45, fill=SKY + (int(255 * a),))
    d.text((W / 2, 865), "izohlarda yozib qoldiring ↓", font=fn("Bold", 46), fill=NAVY + (int(255 * a),), anchor="mm")
    big(d, 540, 960, "suv haqida suvyektiv fikrlaymiz!", fn("ExtraBold", 50), WHITE, ph(t, 1.8))
    big(d, 540, 1040, "Doktor H₂O · @suvyektiv", fn("Bold", 40), SKY, ph(t, 2.4))

def foot_seg(i, clip, ss, dur, fnc):
    L = dur + XF; ov = R + f"seg/ov{i}.mov"; out = R + f"seg/{i:02d}.mp4"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "qtrle", ov], stdin=subprocess.PIPE)
    for f in range(int(round(L * FPS))):
        im = Image.new("RGBA", (W, H)); fnc(ImageDraw.Draw(im), f / FPS); p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-i", R + f"px/{clip}.mp4", "-i", ov, "-filter_complex",
                    f"[0:v]fps=30,trim=0:{L:.3f},setpts=PTS-STARTPTS,scale=-2:1920,crop=1080:1920,eq=brightness=-0.10:saturation=0.95,gblur=sigma=1.2[b];"
                    f"[b][1:v]overlay=format=auto,format=yuv420p", "-t", f"{L:.3f}", "-c:v", "libx264", "-crf", "14", "-preset", "veryfast", out], check=True)

def seg(i):
    global BG
    if i == 0: foot_seg(0, "109879", 0.0, HOOK, o_hook)
    elif i == 2: foot_seg(2, "136086", 0.5, CTA, o_cta)
    else:
        BG = make_bg(); L = BPT + XF
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-crf", "14", "-preset", "veryfast", "-pix_fmt", "yuv420p", R + "seg/01.mp4"], stdin=subprocess.PIPE)
        for f in range(int(round(L * FPS))): p.stdin.write(bp_frame(min(f / FPS, BPT - 0.01)).tobytes())
        p.stdin.close(); p.wait()

def timeline():
    ev = [(0, HOOK, CAP["hook"])] + [(HOOK + ST[k], HOOK + ST[k] + DUR[k], CAP[k]) for k in range(len(DUR))] + [(HOOK + BPT, HOOK + BPT + CTA, CAP["cta"])]
    return ev

def caps():
    import news
    news.KEY = re.compile(r"\d|%|chirchiq|bo'zsuv|qodiriya|panjara|koagulyant|achchiqtosh|qum|xlor|laboratoriya|suvyektiv|qadrlang", re.I)
    news.caps_render([(a + 0.12, b - 0.12, s) for a, b, s in timeline()], HOOK + BPT + CTA, R + "seg/caps.mov")

def build(out, use_caps=True):
    total = HOOK + BPT + CTA
    inputs = ["-i", R + "seg/00.mp4", "-i", R + "seg/01.mp4", "-i", R + "seg/02.mp4"]
    fc = [f"[{i}:v]settb=1/30,fps=30,format=yuv420p[s{i}]" for i in range(3)]
    fc.append(f"[s0][s1]xfade=transition=fade:duration={XF}:offset={HOOK:.3f}[x1]")
    fc.append(f"[x1][s2]xfade=transition=fade:duration={XF}:offset={HOOK + BPT:.3f}[x2]")
    last, n = "x2", 3
    if use_caps:
        inputs += ["-i", R + "seg/caps.mov"]; fc.append(f"[x2][3:v]overlay=format=auto[cv]"); last, n = "cv", 4
    fc.append(f"[{last}]fade=in:d=0.3,fade=out:st={total - 0.6:.3f}:d=0.6,format=yuv420p[V]")
    inputs += ["-i", R + "seg/music.wav"]
    fc.append(f"[{n}:a]atrim=0:{total:.3f},afade=t=out:st={total - 1.5:.3f}:d=1.5,loudnorm=I=-16:TP=-1.5[A]")
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + inputs + ["-filter_complex", ";".join(fc), "-map", "[V]", "-map", "[A]", "-t", f"{total:.3f}",
                    "-c:v", "libx264", "-crf", "20", "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
    print("total", total)

if __name__ == "__main__":
    import os; os.makedirs(R + "seg", exist_ok=True)
    a = sys.argv[1]
    if a == "seg":
        for i in ([int(x) for x in sys.argv[2:]] or [0, 1, 2]): seg(i); print("seg", i)
    elif a == "still":
        BG = make_bg(); bp_frame(float(sys.argv[2])).convert("RGB").save(sys.argv[3])
    elif a == "caps": caps()
    elif a == "build": build(sys.argv[2], "--nocaps" not in sys.argv)
