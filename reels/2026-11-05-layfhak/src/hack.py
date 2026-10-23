"""'5 ta suv tejash layfhagi' reel — SAVINGS-METER style: real footage per hack, a persistent litre counter + a
vertical tank gauge on the right that fills as each hack's saving 'drops in'; big hack number + title per scene.
Captions: same renderer as previous reels.  usage: hack.py gfx | caps | build out.mp4 [--nocaps]"""
import sys, re, math, subprocess
sys.path.insert(0, "/home/claude/r2")
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R = "/home/claude/r7/"
W, H, FPS = 1080, 1920, 30
F = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
_fc = {}
def fn(w, s):
    if (w, s) not in _fc: _fc[(w, s)] = ImageFont.truetype(F.format(w), s)
    return _fc[(w, s)]
WHITE, SKY, SKYD, NAVY, WARN, OK = (255, 255, 255), (132, 210, 253), (31, 111, 178), (11, 31, 51), (255, 120, 95), (90, 220, 150)
def eout(u): u = max(0, min(1, u)); return 1 - (1 - u) ** 3
def ph(t, t0, d=0.5): return eout((t - t0) / d)
def back(u): u = max(0, min(1, u)); c = 1.7; return 1 + (c + 1) * (u - 1) ** 3 + c * (u - 1) ** 2
def fmt(n): return f"{int(round(n)):,}".replace(",", " ")

# source (px video id or ph photo id), start, dur, crop-x, scene, add (litres/yr), drop time, caption
S = [("px/4906", 0.5, 5.5, .50, "hook", 0, 0, "5 ta oddiy odat bilan bir yilda o'n minglab litr suvni tejash mumkin. Hammasi uyda, bugunoq."),
     ("px/136086", 0.0, 7.5, .55, "h1", 9000, 3.4, "Birinchisi: tish yuvayotganda kranni yoping. Har safar 15 dan 30 litrgacha suv tejaladi."),
     ("px/51541", 1.0, 7.5, .40, "h2", 11000, 3.8, "Ikkinchisi: tomchilayotgan kranni tuzating. Sekundiga bitta tomchi — yiliga 11 ming litrdan ortiq suv."),
     ("px/2091", 0.0, 8.5, .45, "h3", 0, 0, "Uchinchisi: unitaz testi. Bachokka bir necha tomchi oziq-ovqat bo'yog'ini tomizing va 10 daqiqa kuting. Rang unitazga chiqsa — suv oqyapti."),
     ("ph/2722595", 0.0, 7.0, .50, "h4", 2650, 3.6, "To'rtinchisi: kran uchiga arzon aerator qo'ying. U suv oqimini kamida 30 foizga kamaytiradi."),
     ("px/1958", 0.0, 7.0, .50, "h5", 3470, 3.8, "Beshinchisi: dushni bir daqiqaga qisqartiring. Oddiy dush har daqiqada taxminan 9,5 litr suv sarflaydi."),
     ("px/147075", 2.0, 7.0, .50, "total", 0, 0, "Hammasi birga — yiliga taxminan 26 ming litr suv. Bu 2 600 ta to'la chelak degani."),
     ("px/136086", 6.0, 6.5, .55, "cta", 0, 0, "Suvni qadrlang! Suv haqida bilmoqchi bo'lganlaringizni izohlarda yozib qoldiring. Bizni kuzatishda davom eting, suv haqida suvyektiv fikrlaymiz!")]
XF = 0.3
TOTAL = sum(s[2] for s in S)
STARTS = [sum(s[2] for s in S[:i]) for i in range(len(S))]
GOAL = sum(s[5] for s in S)                                  # 26 120

def saved(T):
    v = 0
    for i, s in enumerate(S):
        if s[5]: v += s[5] * eout((T - STARTS[i] - s[6]) / 1.0)
    return v

def text(d, x, y, s, f, col, a=1.0, anchor="la"):
    if a <= 0: return
    y = y + (1 - a) * 24
    d.text((x + 3, y + 5), s, font=f, fill=(0, 0, 0, int(150 * a)), anchor=anchor)
    d.text((x, y), s, font=f, fill=col + (int(255 * a),), anchor=anchor)

def hud(d, T, show=True):
    if not show: return
    v = saved(T)
    d.rounded_rectangle([60, 100, 700, 230], 28, fill=(8, 22, 38, 190))
    d.text((92, 118), "TEJALDI · yiliga", font=fn("Bold", 28), fill=SKY + (255,))
    d.text((92, 152), f"{fmt(v)} L", font=fn("Black", 64), fill=WHITE + (255,))
    # tank gauge on the right
    x0, y0, x1, y1 = 940, 100, 1010, 640
    d.rounded_rectangle([x0, y0, x1, y1], 18, fill=(8, 22, 38, 150), outline=WHITE + (230,), width=4)
    lv = y1 - 8 - (y1 - y0 - 16) * min(1, v / GOAL)
    if lv < y1 - 9:
        d.rounded_rectangle([x0 + 8, lv, x1 - 8, y1 - 8], 10, fill=SKY + (240,))
        wob = 4 * math.sin(T * 5)
        d.line([(x0 + 10, lv + wob / 2), (x1 - 10, lv - wob / 2)], fill=WHITE + (200,), width=3)
    for k in range(1, 5):
        yy = y1 - (y1 - y0) * k / 5; d.line([(x0 - 14, yy), (x0, yy)], fill=WHITE + (200,), width=3)

def drop_fx(d, t, t0, amount):
    """'+N L' badge pops at the centre, then flies up into the counter"""
    a = ph(t, t0 - 1.4, 0.4)
    if a <= 0 or t > t0 + 0.6: return
    u = eout((t - t0) / 0.6) if t > t0 else 0
    x = 540 + (380 - 540) * u; y = 760 + (170 - 760) * u; sc = back(min(1, (t - t0 + 1.4) / 0.4)) * (1 - 0.5 * u)
    f = fn("Black", int(96 * max(0.2, sc)))
    s = f"+{fmt(amount)} L"
    w = d.textlength(s, font=f) + 60; hh = int(96 * sc) + 40
    al = int(255 * (1 - u * 0.6))
    d.rounded_rectangle([x - w / 2, y - hh / 2, x + w / 2, y + hh / 2], hh // 2, fill=SKY + (al,))
    d.text((x, y), s, font=f, fill=NAVY + (al,), anchor="mm")
    d.text((540, y + hh / 2 + 16), "yiliga", font=fn("Bold", 36), fill=WHITE + (int(al * (1 - u)),), anchor="ma")

def head(d, t, n, title, sub=None):
    text(d, 72, 290, f"#{n}", fn("Black", 190), SKY, ph(t, 0.0))
    text(d, 80, 500, title, fn("ExtraBold", 76), WHITE, ph(t, 0.3))
    if sub: text(d, 80, 595, sub, fn("Bold", 44), SKY, ph(t, 0.7))

def tip(d, t, s, t0=1.4, col=WHITE):
    a = ph(t, t0)
    if a <= 0: return
    f = fn("Bold", 38); w = d.textlength(s, font=f) + 56
    d.rounded_rectangle([80, 1000 + (1 - a) * 20, 80 + w, 1074 + (1 - a) * 20], 37, fill=(8, 22, 38, int(200 * a)))
    d.text((108, 1014 + (1 - a) * 20), s, font=f, fill=col + (int(255 * a),))

# ---------- scenes ----------
def hook(d, t, T):
    text(d, 80, 420, "5 ta layfhak", fn("Black", 128), WHITE, ph(t, 0.0))
    text(d, 80, 580, "suvni tejash uchun", fn("ExtraBold", 72), SKY, ph(t, 0.5))
    text(d, 80, 700, "hammasi uyda · bugunoq", fn("Bold", 46), WHITE, ph(t, 1.6))

def h1(d, t, T):
    head(d, t, 1, "Tish yuvganda", "kranni yoping")
    tip(d, t, "har safar 15–30 L", 1.2)
    drop_fx(d, t, S[1][6], S[1][5])

def h2(d, t, T):
    head(d, t, 2, "Tomchilagan kran", "1 tomchi / sekund")
    # little drip counter
    n = int(max(0, t - 0.8) * 1.0) + 1 if t > 0.8 else 0
    tip(d, t, f"tomchi: {n}", 0.8)
    drop_fx(d, t, S[2][6], S[2][5])

def h3(d, t, T):
    head(d, t, 3, "Unitaz testi", "bachokka bo'yoq tomizing")
    a = ph(t, 2.0)
    if a > 0:   # 10-minute timer ring
        cx, cy, r = 780, 860, 130
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(8, 22, 38, int(190 * a)), outline=WHITE + (int(120 * a),), width=12)
        p = min(1, max(0, (t - 2.2) / 3.0))
        if p > 0: d.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * p, fill=SKY + (255,), width=12)
        d.text((cx, cy - 6), f"{int(10 * p)}", font=fn("Black", 96), fill=WHITE + (int(255 * a),), anchor="mm")
        d.text((cx, cy + 62), "daqiqa", font=fn("Bold", 30), fill=SKY + (int(255 * a),), anchor="mm")
    tip(d, t, "rang chiqsa — oqish bor", 5.4, WARN)
    a = ph(t, 6.4)
    if a > 0:
        f = fn("ExtraBold", 40); s = "oqish: kuniga 750 L gacha!"
        w = d.textlength(s, font=f) + 56
        d.rounded_rectangle([80, 1090, 80 + w, 1164], 37, fill=WARN + (int(235 * a),))
        d.text((108, 1104), s, font=f, fill=WHITE + (int(255 * a),))

def h4(d, t, T):
    head(d, t, 4, "Aerator qo'ying", "kran uchidagi to'rcha")
    tip(d, t, "oqim −30% · narxi arzon", 1.2)
    drop_fx(d, t, S[4][6], S[4][5])

def h5(d, t, T):
    head(d, t, 5, "Dush −1 daqiqa", "≈ 9,5 L har daqiqada")
    tip(d, t, "9,5 L × 365 kun", 1.2)
    drop_fx(d, t, S[5][6], S[5][5])

def total(d, t, T):
    text(d, 80, 330, "Jami", fn("ExtraBold", 72), WHITE, ph(t, 0.0))
    text(d, 72, 420, "≈ 26 000 L", fn("Black", 150), SKY, ph(t, 0.3))
    text(d, 80, 600, "har yili", fn("Bold", 52), WHITE, ph(t, 0.6))
    a = ph(t, 2.0)
    if a > 0:   # 26 buckets, each = 100 buckets
        for k in range(26):
            b = ph(t, 2.0 + k * 0.06, 0.25)
            x = 90 + (k % 9) * 100; y = 720 + (k // 9) * 100
            d.polygon([(x, y), (x + 70, y), (x + 60, y + 72), (x + 10, y + 72)], fill=SKY + (int(235 * b),), outline=WHITE + (int(255 * b),))
            d.arc([x + 6, y - 26, x + 64, y + 22], 200, 340, fill=WHITE + (int(255 * b),), width=4)
        text(d, 80, 1030, "har biri = 100 chelak  →  2 600 ta chelak", fn("Bold", 36), WHITE, ph(t, 4.0))
    text(d, 80, 1095, "Manba: US EPA WaterSense · hisob: Doktor H₂O", fn("Medium", 26), WHITE, ph(t, 1.0))

def cta(d, t, T):
    text(d, 540, 380, "Suvni", fn("Black", 150), WHITE, ph(t, 0.0), "ma")
    text(d, 540, 540, "qadrlang!", fn("Black", 150), SKY, ph(t, 0.2), "ma")
    text(d, 540, 780, "Suv haqida bilmoqchi bo'lganlaringizni", fn("Bold", 42), WHITE, ph(t, 0.8), "ma")
    a = ph(t, 1.1); w = d.textlength("izohlarda yozib qoldiring ↓", font=fn("Bold", 46)) + 70
    d.rounded_rectangle([(W - w) / 2, 840, (W + w) / 2, 930], 45, fill=SKY + (int(255 * a),))
    d.text((W / 2, 885), "izohlarda yozib qoldiring ↓", font=fn("Bold", 46), fill=NAVY + (int(255 * a),), anchor="mm")
    text(d, 540, 980, "suv haqida suvyektiv fikrlaymiz!", fn("ExtraBold", 50), WHITE, ph(t, 1.8), "ma")
    text(d, 540, 1060, "Doktor H₂O · @suvyektiv", fn("Bold", 40), SKY, ph(t, 2.4), "ma")

SC = {s[4]: globals()[s[4]] for s in S}

def ovl(i):
    src, ss, dur, cx, name, add, dt, cap = S[i]
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "qtrle", R + f"ov/{name}.mov"], stdin=subprocess.PIPE)
    for f in range(int((dur + XF) * FPS) + 2):
        t = f / FPS; T = STARTS[i] + t
        im = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(im)
        hud(d, T, name not in ("hook", "cta")); SC[name](d, t, T)
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()

def gfx(only=None):
    import os; os.makedirs(R + "ov", exist_ok=True)
    g = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(g)
    for y in range(H):
        a = 170 * max(0, 1 - y / 1150) ** 1.2 + 90 * max(0, (y - 1450) / 470) ** 1.5
        d.line([(0, y), (W, y)], fill=(5, 15, 25, int(a)))
    g.save(R + "ov/grad.png")
    for i in range(len(S)):
        if only is None or i in only: ovl(i)

def caps():
    import news
    news.KEY = re.compile(r"\d|%|litr|kran|tomchi|bo'yoq|aerator|dush|chelak|suvyektiv|qadrlang", re.I)
    news.caps_render([(STARTS[i] + 0.12, STARTS[i] + s[2] - 0.12, s[7]) for i, s in enumerate(S)], TOTAL, R + "ov/caps.mov")

def build(out, use_caps=True):
    inputs, fc = [], []
    n = lambda: sum(1 for x in inputs if x == "-i")
    inputs += ["-loop", "1", "-i", R + "ov/grad.png"]
    fc.append(f"[0:v]format=rgba,split={len(S)}" + "".join(f"[g{i}]" for i in range(len(S))))
    for i, (src, ss, dur, cx, name, add, dt, cap) in enumerate(S):
        L = dur + XF
        if src.startswith("ph/"):
            inputs += ["-loop", "1", "-framerate", "30", "-i", R + src + ".jpg"]; vi = n() - 1
            base = f"[{vi}:v]trim=0:{L:.3f},setpts=PTS-STARTPTS,scale=-2:2100,crop=1080:1920:(iw-1080)*{cx}:(ih-1920)/2"
            base += f",scale=w=-2:h='1920*(1.0+0.06*t/{L:.3f})':eval=frame,crop=1080:1920"
        else:
            inputs += ["-ss", str(ss), "-i", R + src + ".mp4"]; vi = n() - 1
            base = (f"[{vi}:v]fps=30,trim=0:{L:.3f},setpts=PTS-STARTPTS,scale=w=-2:h='1920*(1.0+0.04*t/{L:.3f})':eval=frame:flags=bicubic,"
                    f"crop=1080:1920:(iw-1080)*{cx}:(ih-1920)/2")
        inputs += ["-i", R + f"ov/{name}.mov"]; oi = n() - 1
        fc.append(base + f",setsar=1,fps=30,eq=saturation=0.95:contrast=1.04,format=rgba[b{i}];"
                  f"[g{i}]trim=0:{L:.3f},setpts=PTS-STARTPTS[gg{i}];[b{i}][gg{i}]overlay=format=auto[bg{i}];"
                  f"[{oi}:v]trim=0:{L:.3f},setpts=PTS-STARTPTS,format=rgba[o{i}];[bg{i}][o{i}]overlay=format=auto,format=yuv420p,settb=1/30[s{i}]")
    cur, off = "s0", S[0][2]
    for i in range(1, len(S)):
        fc.append(f"[{cur}][s{i}]xfade=transition={'slideleft' if 1 <= i <= 6 else 'fade'}:duration={XF}:offset={off:.3f}[x{i}]"); cur = f"x{i}"; off += S[i][2]
    last = cur
    if use_caps:
        inputs += ["-i", R + "ov/caps.mov"]; ci = n() - 1
        fc.append(f"[{cur}][{ci}:v]overlay=format=auto[cv]"); last = "cv"
    fc.append(f"[{last}]fade=in:d=0.3,fade=out:st={off - 0.6:.3f}:d=0.6,format=yuv420p[V]")
    inputs += ["-i", R + "ov/music.wav"]; mi = n() - 1
    fc.append(f"[{mi}:a]atrim=0:{off:.3f},afade=t=out:st={off - 1.5:.3f}:d=1.5,loudnorm=I=-16:TP=-1.5[A]")
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + inputs + ["-filter_complex", ";".join(fc), "-map", "[V]", "-map", "[A]", "-t", f"{off:.3f}",
                    "-c:v", "libx264", "-crf", "20", "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
    print("total", off)

if __name__ == "__main__":
    a = sys.argv[1]
    if a == "gfx": gfx([int(x) for x in sys.argv[2:]] or None)
    elif a == "caps": caps()
    elif a == "build": build(sys.argv[2], "--nocaps" not in sys.argv)
