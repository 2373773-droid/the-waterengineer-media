"""'Salardagi hid' reel — 'case file / tergov' style on a light paper board: real Salar photos (credited) as evidence
prints with tape and stamps, navy kinetic text, H2S molecule + process diagrams. Captions: same renderer as 24.10/27.10.
usage: case.py frames | caps | build out.mp4 [--nocaps]"""
import sys, math, subprocess, random, re
sys.path.insert(0, "/home/claude/r2")
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R = "/home/claude/r4/"
W, H, FPS = 1080, 1920, 30
F = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
_fc = {}
def fn(w, s):
    if (w, s) not in _fc: _fc[(w, s)] = ImageFont.truetype(F.format(w), s)
    return _fc[(w, s)]
WHITE, SKY, SKYD, NAVY, WARN = (255, 255, 255), (132, 210, 253), (31, 111, 178), (11, 31, 51), (226, 88, 62)
INK2 = (70, 88, 108); PAPER = (241, 245, 248); SULF = (242, 196, 64)
def ease(u): u = max(0, min(1, u)); return 1 - (1 - u) ** 3
def ph(t, t0, d=0.5): return ease((t - t0) / d)
def back(u): u = max(0, min(1, u)); c = 1.7; return 1 + (c + 1) * (u - 1) ** 3 + c * (u - 1) ** 2

# (scene fn, dur, chapter, caption text)
S = [("hook", 7.5, "", "Sergelida yashaganlar bu hidni yaxshi bilishadi: chirigan tuxum hidi. Qayerdan keladi? Men suv va oqova suv bo'yicha tadqiqot qilaman."),
     ("plant", 7.0, "INSHOOT", "Salar tozalash inshooti 1961 yilda qurilgan. Bugun u kuniga 900 ming kub metr oqova suv qabul qiladi."),
     ("h2s", 8.0, "AYBDOR", "Hidning aybdori — vodorod sulfid. Kislorod yetmagan joyda bakteriyalar sulfat bilan nafas oladi va shu gazni chiqaradi."),
     ("nose", 5.5, "SEZISH", "Burnimiz uni milliard qismdan yarim qism bo'lsa ham sezadi."),
     ("turn", 3.0, "", "Lekin muammo faqat inshootda emas edi."),
     ("case", 12.0, "TEKSHIRUV · 2021", "2021 yilda Salarga 18 ta korxona, jumladan teri zavodlari, oqova tashlagani aniqlandi. Kimyoviy moddalar suvni tozalaydigan mikroorganizmlarni nobud qilgan. 22 mas'ulga ish ochildi."),
     ("fix", 10.0, "YECHIM · 2026", "2026 yil yozida hovuzlar yopildi, havo esa sorbent, ultrabinafsha nur va faollashtirilgan ko'mirdan o'tkazilmoqda. Narxi 9,5 milliard so'm."),
     ("verdict", 10.0, "XULOSA", "Rasmiylar H₂S nolga tushdi deyishmoqda. Lekin hidni yo'qotish suvni tozalash degani emas. Asosiy yechim — korxonalar oqovasini o'zi tozalashi."),
     ("cta", 6.5, "", "Suvni tejang! Suv haqida bilmoqchi bo'lganlaringizni izohlarda yozib qoldiring. Bizni kuzatishda davom eting, suv haqida suvyektiv fikrlaymiz!")]
TOTAL = sum(s[1] for s in S)
STARTS = [sum(s[1] for s in S[:i]) for i in range(len(S))]

# ---------- paper board ----------
def make_paper():
    im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im)
    for x in range(0, W, 54): d.line([(x, 0), (x, H)], fill=(228, 235, 241), width=2)
    for y in range(0, H, 54): d.line([(0, y), (W, y)], fill=(228, 235, 241), width=2)
    rnd = random.Random(3)
    for _ in range(9000):
        x, y = rnd.randrange(W), rnd.randrange(H); c = rnd.randint(225, 248); d.point((x, y), fill=(c, c + 3, c + 6))
    return im
PAPER_IM = None

_ph = {}
def photo(name):
    if name not in _ph: _ph[name] = Image.open(R + f"ph/{name}.jpg").convert("RGB")
    return _ph[name]

def card(im, name, cx, cy, w, rot, a, t, credit="", zoom=0.06, tape=True):
    """evidence print: Ken-Burns inside a white border, drop shadow, slight rotation, tape strip"""
    if a <= 0: return
    p = photo(name); pw, phh = p.size; h = int(w * phh / pw)
    z = 1 + zoom * min(1, t / 8)
    cw, ch = pw / z, phh / z
    sub = p.crop((int((pw - cw) / 2), int((phh - ch) / 2), int((pw + cw) / 2), int((phh + ch) / 2))).resize((w, h), Image.BILINEAR)
    b = 14; fr = Image.new("RGBA", (w + 2 * b, h + 2 * b + (34 if credit else 0)), WHITE + (255,))
    fr.paste(sub, (b, b))
    if credit:
        ImageDraw.Draw(fr).text((b, h + b + 8), "Foto: " + credit, font=fn("SemiBold", 22), fill=INK2 + (255,))
    if tape:
        td = ImageDraw.Draw(fr); tw = 150
        td.rectangle([(fr.width - tw) // 2, 0, (fr.width + tw) // 2, 22], fill=(200, 228, 246, 220))
    fr = fr.rotate(rot, resample=Image.BICUBIC, expand=True)
    s = 0.92 + 0.08 * a
    if s != 1: fr = fr.resize((int(fr.width * s), int(fr.height * s)), Image.BILINEAR)
    sh = Image.new("RGBA", fr.size, (0, 0, 0, 0)); sh.putalpha(fr.getchannel("A").point(lambda v: int(v * 0.28 * a)))
    sh = sh.filter(ImageFilter.GaussianBlur(12))
    if a < 1: fr.putalpha(fr.getchannel("A").point(lambda v: int(v * a)))
    x, y = int(cx - fr.width / 2), int(cy - fr.height / 2 + (1 - a) * 40)
    im.alpha_composite(sh, (x + 6, y + 14)); im.alpha_composite(fr, (x, y))

def stamp(im, s, cx, cy, rot, a, col=WARN, size=54):
    if a <= 0: return
    f = fn("Black", size); tw = int(ImageDraw.Draw(im).textlength(s, font=f)) + 60
    st = Image.new("RGBA", (tw, size + 50)); d = ImageDraw.Draw(st)
    d.rounded_rectangle([4, 4, tw - 4, size + 46], 12, outline=col + (255,), width=7)
    d.text((tw / 2, (size + 50) / 2), s, font=f, fill=col + (255,), anchor="mm")
    sc = 1 + 1.2 * (1 - ease(min(1, a * 1.0)))             # slams in from bigger
    st = st.rotate(rot, resample=Image.BICUBIC, expand=True)
    st = st.resize((int(st.width * sc), int(st.height * sc)), Image.BILINEAR)
    st.putalpha(st.getchannel("A").point(lambda v: int(v * min(1, a * 1.4) * 0.92)))
    im.alpha_composite(st, (int(cx - st.width / 2), int(cy - st.height / 2)))

def text(d, x, y, s, f, col, a=1.0, anchor="la"):
    if a <= 0: return
    d.text((x, y + (1 - a) * 24), s, font=f, fill=col + (int(255 * a),), anchor=anchor)

def marker(d, x, y, s, f, a, col=SKY):
    """highlighter swipe behind text"""
    if a <= 0: return
    w = d.textlength(s, font=f); bb = d.textbbox((x, y), s, font=f)
    d.rectangle([x - 10, bb[1] + (bb[3] - bb[1]) * 0.25, x - 10 + (w + 20) * a, bb[3] + 8], fill=col + (200,))

def hud(d, i, t):
    g = (STARTS[i] + t) / TOTAL
    d.text((80, 120), "TERGOV · SALARDAGI HID", font=fn("Bold", 30), fill=NAVY + (235,))
    if 1 <= i <= 7: d.text((1000, 120), f"{i:02d}/07", font=fn("Bold", 30), fill=SKYD + (255,), anchor="ra")
    d.line([(80, 172), (1000, 172)], fill=(190, 205, 218, 255), width=4)
    d.line([(80, 172), (80 + 920 * g, 172)], fill=SKYD + (255,), width=4)
    d.ellipse([80 + 920 * g - 8, 164, 80 + 920 * g + 8, 180], fill=SKYD + (255,))

def chapter(d, title, t):
    if not title: return
    a = ph(t, 0.1, 0.4)
    d.rectangle([80, 226, 88, 272], fill=WARN + (int(255 * a),))
    text(d, 106, 228, title, fn("ExtraBold", 38), NAVY, a)

# ---------- scenes ----------
def hook(im, d, t):
    card(im, "aerial", 540, 900, 900, -2.5, ph(t, 0.0, 0.6), t, "Toshkent sh. hokimligi")
    text(d, 80, 250, "Sergeli, Toshkent", fn("Bold", 40), SKYD, ph(t, 0.2))
    f = fn("Black", 92)
    marker(d, 80, 320, "Chirigan tuxum", f, ph(t, 0.9, 0.5))
    text(d, 80, 320, "Chirigan tuxum", f, NAVY, ph(t, 0.5))
    text(d, 80, 425, "hidi qayerdan?", f, NAVY, ph(t, 0.7))
    stamp(im, "HID MANBASI?", 760, 640, 8, ph(t, 2.2, 0.35))
    a = ph(t, 4.6)                                                 # who is speaking
    if a > 0:
        d.rounded_rectangle([80, 1300, 80 + 860 * a, 1400], 18, fill=NAVY + (int(240 * a),))
        text(d, 110, 1312, "Javohir · suv va oqova suv tadqiqotchisi", fn("Bold", 38), WHITE, a)
        text(d, 110, 1358, "Dong-A universiteti, suv laboratoriyasi", fn("Medium", 26), SKY, a)

def plant(im, d, t):
    card(im, "aer2", 560, 860, 860, 2, ph(t, 0.0, 0.6), t, "Kun.uz")
    yr = int(1900 + 61 * ph(t, 0.3, 1.2))
    text(d, 80, 300, f"{yr}", fn("Black", 130), NAVY, ph(t, 0.2))
    text(d, 400, 330, "yildan beri", fn("Bold", 44), INK2, ph(t, 1.2))
    text(d, 400, 385, "ishlaydi", fn("Bold", 44), INK2, ph(t, 1.3))
    card(im, "insp", 760, 1180, 480, -4, ph(t, 2.4, 0.5), t, "UzReport")
    v = 900 * ph(t, 3.0, 1.4)
    f = fn("Black", 84)
    a = ph(t, 2.8)
    if a > 0:
        d.rounded_rectangle([60, 1290, 700, 1500], 22, fill=WHITE + (int(245 * a),), outline=SKYD + (int(255 * a),), width=4)
        text(d, 90, 1305, f"{int(v)} ming m³", f, SKYD, a)
        text(d, 92, 1412, "oqova suv · har kuni", fn("Bold", 36), NAVY, a)
        text(d, 92, 1455, "Toshkentning 7 ta tumanidan", fn("Medium", 28), INK2, ph(t, 4.0))

def molecule(im, cx, cy, sc, a, t):
    if a <= 0: return
    lay = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(lay)
    wob = 4 * math.sin(t * 2.2)
    rS, rH, L = 120 * sc, 66 * sc, 190 * sc
    hs = [(cx + L * math.sin(math.radians(46 + wob)), cy + L * math.cos(math.radians(46 + wob))),
          (cx - L * math.sin(math.radians(46 - wob)), cy + L * math.cos(math.radians(46 - wob)))]
    for hx, hy in hs: d.line([(cx, cy), (hx, hy)], fill=NAVY + (255,), width=int(16 * sc))
    for hx, hy in hs:
        d.ellipse([hx - rH, hy - rH, hx + rH, hy + rH], fill=WHITE + (255,), outline=NAVY + (255,), width=int(7 * sc))
        d.text((hx, hy), "H", font=fn("Black", int(66 * sc)), fill=NAVY + (255,), anchor="mm")
    d.ellipse([cx - rS, cy - rS, cx + rS, cy + rS], fill=SULF + (255,), outline=NAVY + (255,), width=int(8 * sc))
    d.text((cx, cy), "S", font=fn("Black", int(120 * sc)), fill=NAVY + (255,), anchor="mm")
    lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    im.alpha_composite(lay)

def h2s(im, d, t):
    text(d, 80, 300, "Vodorod sulfid", fn("Black", 96), NAVY, ph(t, 0.1))
    f = fn("Black", 80); marker(d, 80, 410, "H₂S", f, ph(t, 0.8, 0.4), SULF)
    text(d, 80, 410, "H₂S", f, NAVY, ph(t, 0.5))
    molecule(im, 840, 500, 0.62 * (0.8 + 0.2 * back(min(1, t / 0.8))), ph(t, 0.3), t)
    # process chain
    steps = [("Kislorod yo'q", "O₂ = 0", 2.0), ("Bakteriyalar", "sulfat bilan «nafas»", 3.3), ("Gaz chiqadi", "SO₄²⁻ → H₂S", 4.6)]
    y = 660
    for k, (a1, b1, t0) in enumerate(steps):
        a = ph(t, t0)
        if a <= 0: continue
        yy = y + k * 160
        d.rounded_rectangle([80, yy + (1 - a) * 20, 1000, yy + 140 + (1 - a) * 20], 24, fill=WHITE + (int(250 * a),), outline=(NAVY if k < 2 else WARN) + (int(255 * a),), width=4)
        d.ellipse([110, yy + 30 + (1 - a) * 20, 190, yy + 110 + (1 - a) * 20], fill=(SKYD if k < 2 else WARN) + (int(255 * a),))
        text(d, 150, yy + 70, str(k + 1), fn("Black", 44), WHITE, a, "mm")
        text(d, 220, yy + 26, a1, fn("ExtraBold", 50), NAVY, a)
        text(d, 220, yy + 86, b1, fn("SemiBold", 34), INK2, a)
        if k < 2 and ph(t, steps[k + 1][2] - 0.3) > 0:
            d.polygon([(540, yy + 148), (520, yy + 148), (530, yy + 168)], fill=NAVY + (255,))
    text(d, 80, 1290, "Manba: ATSDR / Hawaii DOH H₂S ma'lumotnomasi", fn("Medium", 24), INK2, ph(t, 5.5))

def nose(im, d, t):
    v = 0.5 * ph(t, 0.3, 1.0)
    text(d, 80, 290, f"{v:.1f}".replace(".", ","), fn("Black", 250), NAVY, ph(t, 0.1))
    text(d, 560, 380, "ppb", fn("Black", 110), SKYD, ph(t, 0.4))
    text(d, 80, 580, "milliard qismdan yarim qism", fn("ExtraBold", 54), NAVY, ph(t, 0.9))
    # pool vs quarter-teaspoon
    a = ph(t, 1.6)
    if a > 0:
        x0, y0, x1, y1 = 80, 690, 1000, 1010
        d.rounded_rectangle([x0, y0, x1, y1], 26, fill=(196, 230, 250, int(255 * a)), outline=SKYD + (int(255 * a),), width=6)
        for k in range(1, 8): d.line([(x0 + k * 115, y0 + 10), (x0 + k * 115, y1 - 10)], fill=(255, 255, 255, int(160 * a)), width=4)
        text(d, 110, 710, "Olimpiya basseyni ≈ 2,5 mln litr", fn("Bold", 36), NAVY, a)
        b = ph(t, 2.6)
        if b > 0:
            cx, cy = 760, 900; r = 9
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WARN + (int(255 * b),))
            for k in range(3):
                rr = r + 14 + k * 22 + 10 * math.sin(t * 4 - k)
                d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=WARN + (int(140 * b / (k + 1)),), width=3)
            text(d, 80, 1050, "ichida chorak choy qoshiq — shuncha nisbat", fn("Bold", 36), WARN, b)
    text(d, 80, 1290, "Sezish chegarasi ≈ 0,5 ppb dan boshlanadi (odamga qarab farq qiladi)", fn("Medium", 24), INK2, ph(t, 3.2))

def turn(im, d, t):
    card(im, "trash", 540, 830, 880, -1.5, ph(t, 0.0, 0.5), t, "Sputnik O'zbekiston")
    text(d, 80, 300, "Lekin muammo", fn("Black", 92), NAVY, ph(t, 0.1))
    text(d, 80, 400, "faqat shu yerdami?", fn("Black", 92), NAVY, ph(t, 0.3))
    stamp(im, "ASOSIY SABAB?", 700, 1180, -7, ph(t, 1.2, 0.35))

def case(im, d, t):
    # part A (0–6s): 18 enterprises + tanneries; part B (6–12s): microbes killed, 22 cases
    if t < 6.2:
        card(im, "pipe", 560, 820, 880, 2, ph(t, 0.0, 0.5), t, "Ekologiya vazirligi")
        v = int(18 * ph(t, 0.6, 1.2))
        text(d, 80, 290, f"{v}", fn("Black", 170), WARN, ph(t, 0.3))
        text(d, 330, 320, "ta korxona", fn("ExtraBold", 56), NAVY, ph(t, 0.8))
        text(d, 330, 390, "oqovasini Salarga tashlagan", fn("Bold", 36), INK2, ph(t, 1.0))
        card(im, "drums", 810, 1360, 400, -4, ph(t, 2.6, 0.5), t, "Daryo")
        a = ph(t, 3.2)
        if a > 0:
            d.rounded_rectangle([60, 1290, 540, 1540], 22, fill=WHITE + (int(245 * a),), outline=NAVY + (int(255 * a),), width=4)
            text(d, 90, 1310, "ular orasida:", fn("SemiBold", 30), INK2, a)
            text(d, 90, 1355, "5 ta teri", fn("Black", 52), NAVY, a)
            text(d, 90, 1420, "6 ta to'qimachilik", fn("Black", 44), NAVY, ph(t, 3.6))
            text(d, 90, 1480, "korxonasi (xavfli ro'yxat)", fn("Medium", 26), INK2, ph(t, 3.8))
    else:
        u = t - 6.2
        card(im, "outfall", 600, 760, 760, -2, ph(u, 0.0, 0.5), u, "Gazeta.uz")
        text(d, 80, 290, "Kimyoviy moddalar", fn("Black", 76), NAVY, ph(u, 0.1))
        f = fn("Black", 76); marker(d, 80, 380, "mikroblarni o'ldirgan", f, ph(u, 0.9, 0.5), (255, 190, 175))
        text(d, 80, 380, "mikroblarni o'ldirgan", f, NAVY, ph(u, 0.4))
        text(d, 80, 1060, "suvni tozalaydigan foydali mikroorganizmlar", fn("Bold", 34), INK2, ph(u, 1.0))
        stamp(im, "22 MAS'ULGA ISH", 560, 1340, -6, ph(u, 3.2, 0.35), size=62)
    text(d, 80, 1580, "Manba: Gazeta.uz (14.06.2021), Kun.uz (24.06.2021)", fn("Medium", 24), INK2, ph(t, 1.5))

def fix(im, d, t):
    card(im, "filter", 540, 520, 900, 1.5, ph(t, 0.0, 0.5), t, "Toshkent sh. hokimligi")
    steps = [("Hovuz yopildi", "germetik qopqoq", NAVY, 1.2), ("11,5 t", "katalitik sorbent", SKYD, 2.4),
             ("UB nur", "ozon va oksidlash", SKYD, 3.6), ("2,5 t", "faollashtirilgan ko'mir", SKYD, 4.8)]
    for k, (a1, b1, col, t0) in enumerate(steps):
        a = ph(t, t0); yy = 760 + k * 100
        if a <= 0: continue
        d.rounded_rectangle([80, yy, 80 + 860 * a, yy + 88], 20, fill=WHITE + (int(250 * a),), outline=col + (255,), width=4)
        text(d, 110, yy + 14, a1, fn("Black", 52), col, a)
        text(d, 530, yy + 26, b1, fn("SemiBold", 36), INK2, a)
        if k < 3: d.polygon([(500, yy + 90), (480, yy + 90), (490, yy + 100)], fill=NAVY + (int(255 * ph(t, t0 + 1.0)),))
    a = ph(t, 6.6)
    if a > 0:
        d.rounded_rectangle([80, 1300, 760, 1420], 24, fill=NAVY + (int(245 * a),))
        text(d, 110, 1318, "9,5 mlrd so'm", fn("Black", 72), SKY, a)
    text(d, 80, 1450, "Manba: Gazeta.uz, Kun.uz (sentyabr 2026)", fn("Medium", 24), INK2, ph(t, 1.5))

def verdict(im, d, t):
    o = 1 - ph(t, 4.9, 0.4)                                    # first half fades out for the solution
    card(im, "lab", 760, 760, 520, 3, min(ph(t, 0.0, 0.5), o), t, "Yuz.uz")
    text(d, 80, 300, "H₂S = 0", fn("Black", 120), NAVY, min(ph(t, 0.2), 1))
    text(d, 80, 440, "rasmiylar ma'lumoti", fn("Bold", 36), INK2, ph(t, 0.6))
    f = fn("Black", 66)
    text(d, 80, 560, "Hid yo'q", f, NAVY, min(ph(t, 2.6), o))
    text(d, 80, 640, "≠", fn("Black", 90), WARN, min(ph(t, 3.0), o))
    text(d, 80, 750, "suv toza", f, NAVY, min(ph(t, 3.3), o))
    b = ph(t, 5.3)
    if b > 0:
        y0 = 580
        d.rounded_rectangle([80, y0, 1000, y0 + 420], 26, fill=WHITE + (int(250 * b),), outline=SKYD + (255,), width=5)
        text(d, 110, y0 + 24, "ASOSIY YECHIM", fn("ExtraBold", 36), SKYD, b)
        flow = [("Korxona", NAVY), ("o'z tozalash inshooti", SKYD), ("kanalizatsiya", NAVY)]
        for k, (s_, col) in enumerate(flow):
            c = ph(t, 5.6 + k * 0.6); yy = y0 + 90 + k * 95
            text(d, 110, yy, s_, fn("Black", 54), col, c)
            if k < 2: text(d, 900, yy + 4, "↓", fn("Black", 54), WARN, c, "ra")
def cta(im, d, t):
    text(d, 80, 380, "Suvni tejang!", fn("Black", 120), SKYD, ph(t, 0))
    text(d, 80, 540, "Suv haqida bilmoqchi bo'lganlaringizni", fn("Bold", 42), NAVY, ph(t, 0.6))
    a = ph(t, 0.9)
    w = d.textlength("izohlarda yozib qoldiring ↓", font=fn("Bold", 46)) + 60
    d.rounded_rectangle([80, 605, 80 + w, 687], 41, fill=SKY + (int(255 * a),))
    text(d, 110, 620, "izohlarda yozib qoldiring ↓", fn("Bold", 46), NAVY, a)
    text(d, 80, 780, "Bizni kuzatishda davom eting —", fn("SemiBold", 42), NAVY, ph(t, 1.6))
    text(d, 80, 836, "suv haqida suvyektiv fikrlaymiz!", fn("ExtraBold", 52), SKYD, ph(t, 2.1))
    text(d, 80, 940, "Doktor H₂O  ·  @suvyektiv", fn("Bold", 40), NAVY, ph(t, 2.6))

SC = {k: globals()[k] for k in [s[0] for s in S]}

def frame(i, t):
    im = PAPER_IM.copy().convert("RGBA"); d = ImageDraw.Draw(im)
    hud(d, i, t); chapter(d, S[i][2], t); SC[S[i][0]](im, d, t)
    return im

def frames(out=R + "board.mp4", only=None):
    global PAPER_IM; PAPER_IM = make_paper()
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i, s in enumerate(S):
        if only is not None and i not in only: continue
        n = int(round(s[1] * FPS))
        for f in range(n):
            t = f / FPS; im = frame(i, t)
            if f < 5 and i > 0:                                   # quick paper-flash cut
                im = Image.blend(im, PAPER_IM.convert("RGBA"), 1 - f / 5)
            p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()

def caps():
    import news
    lines = [(STARTS[i] + 0.15, STARTS[i] + s[1] - 0.15, s[3]) for i, s in enumerate(S)]
    news.KEY = re.compile(r"\d|%|H₂S|hid|sulfid|korxona|teri|mikroorganizm|milliard|kub|kislorod|suvyektiv|tejang", re.I)
    news.caps_render(lines, TOTAL, R + "caps.mov")

def build(out, use_caps=True):
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", R + "board.mp4"]
    if use_caps: cmd += ["-i", R + "caps.mov"]
    cmd += ["-i", R + "music.wav"]
    mi = 2 if use_caps else 1
    fc = "[0:v][1:v]overlay=0:0:format=auto[v]" if use_caps else "[0:v]null[v]"
    cmd += ["-filter_complex", fc + f";[{mi}:a]loudnorm=I=-16:TP=-1.5[a]", "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", out]
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    a = sys.argv[1]
    if a == "frames": frames()
    elif a == "still":
        PAPER_IM = make_paper(); i = int(sys.argv[2]); t = float(sys.argv[3])
        frame(i, t).convert("RGB").save(sys.argv[4])
    elif a == "caps": caps()
    elif a == "build": build(sys.argv[2], "--nocaps" not in sys.argv)
