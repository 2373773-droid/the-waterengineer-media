"""'Butilka suvida 240 000 plastik' paper reel — ZOOM-LENS style: real footage per hack, a persistent litre counter + a
vertical tank gauge on the right that fills as each hack's saving 'drops in'; big hack number + title per scene.
Captions: same renderer as previous reels.  usage: hack.py gfx | caps | build out.mp4 [--nocaps]"""
import sys, re, math, subprocess
sys.path.insert(0, "/home/claude/r2")
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R = "/home/claude/r8/"
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

# source, start, dur, crop-x, scene, -, -, caption
S = [("px/35574", 3.0, 6.0, .50, "hook", 0, 0, "Bir litr butilka suvida o'rtacha 240 ming plastik zarrasi bor. Bu raqam 2024 yilgi ilmiy maqoladan."),
     ("px/197489", 2.0, 7.0, .45, "paper", 0, 0, "Kolumbiya universiteti olimlari uchta mashhur brend suvini maxsus lazer mikroskop bilan zarrama-zarra tekshirdi."),
     ("px/8281", 0.0, 9.5, .45, "zoom", 0, 0, "Zarralarning 90 foizi nanoplastik bo'lib chiqdi: ular mikrometrdan kichik, soch tolasidan 70 baravar ingichka."),
     ("px/262188", 1.0, 7.0, .50, "compare", 0, 0, "Bu avvalgi hisoblardan 10 dan 100 martagacha ko'p. Eski usullar faqat yirik mikroplastikni ko'ra olardi."),
     ("px/35574", 5.5, 7.5, .55, "types", 0, 0, "Eng ko'p topilganlari: poliamid — u suv tozalash filtrlarida ishlatiladi, va PET — butilkaning o'z plastigi."),
     ("px/197489", 14.0, 7.0, .45, "caveat", 0, 0, "Muhim: bu zarralarning sog'liqqa ta'siri hali isbotlanmagan, olimlar o'rganishda davom etmoqda."),
     ("px/133507", 4.0, 6.5, .50, "cta", 0, 0, "Suvni qadrlang! Suv haqida bilmoqchi bo'lganlaringizni izohlarda yozib qoldiring. Bizni kuzatishda davom eting, suv haqida suvyektiv fikrlaymiz!")]
XF = 0.3
TOTAL = sum(s[2] for s in S)
STARTS = [sum(s[2] for s in S[:i]) for i in range(len(S))]

def text(d, x, y, s, f, col, a=1.0, anchor="la"):
    if a <= 0: return
    y = y + (1 - a) * 24
    d.text((x + 3, y + 5), s, font=f, fill=(0, 0, 0, int(150 * a)), anchor=anchor)
    d.text((x, y), s, font=f, fill=col + (int(255 * a),), anchor=anchor)

def hud(d, T, show=True):
    if not show: return
    d.text((80, 112), "MAQOLA MUHOKAMASI · PNAS 2024", font=fn("Bold", 30), fill=WHITE + (235,))
    g = T / TOTAL
    d.line([(80, 164), (1000, 164)], fill=(255, 255, 255, 90), width=4)
    d.line([(80, 164), (80 + 920 * g, 164)], fill=SKY + (255,), width=4)

def card(d, box, a, fill=WHITE, out=None):
    x0, y0, x1, y1 = box; dy = (1 - a) * 30
    d.rounded_rectangle([x0, y0 + dy, x1, y1 + dy], 26, fill=fill + (int(240 * a),), outline=(out + (int(255 * a),)) if out else None, width=4)
    return dy

# ---------- scenes ----------
def hook(d, t, T):
    v = 240000 * eout((t - 0.3) / 2.2)
    text(d, 80, 300, "1 litr butilka suvida", fn("ExtraBold", 60), WHITE, ph(t, 0.0))
    text(d, 66, 380, fmt(v), fn("Black", 210), SKY, ph(t, 0.2))
    text(d, 80, 620, "plastik zarrasi", fn("Black", 92), WHITE, ph(t, 1.0))
    a = ph(t, 3.0)
    if a > 0:
        f = fn("Bold", 40); s = "PNAS · 2024 · Kolumbiya universiteti"; w = d.textlength(s, font=f) + 60
        d.rounded_rectangle([80, 760, 80 + w, 836], 38, fill=(8, 22, 38, int(210 * a)))
        d.text((110, 775), s, font=f, fill=SKY + (int(255 * a),))

def paper(d, t, T):
    a = ph(t, 0.0)
    dy = card(d, (70, 260, 1010, 1060), a)
    d.rectangle([70, 260 + dy, 1010, 330 + dy], fill=(170, 30, 40, int(255 * a)))
    d.text((100, 278 + dy), "PNAS · 2024 · 121(3)", font=fn("Bold", 30), fill=WHITE + (int(255 * a),))
    t1 = "Rapid single-particle chemical"; t2 = "imaging of nanoplastics by SRS"; t3 = "microscopy"
    for k, s in enumerate((t1, t2, t3)):
        d.text((100, 360 + k * 56 + dy), s, font=fn("Bold", 44), fill=NAVY + (int(255 * ph(t, 0.3 + k * 0.1)),))
    d.text((100, 540 + dy), "Qian, … Yan, Min · Columbia University", font=fn("Medium", 30), fill=(70, 88, 108, int(255 * ph(t, 0.8))))
    rows = [("3", "mashhur brend suvi"), ("lazer", "SRS mikroskop"), ("7", "xil plastik turi qidirildi")]
    for k, (v, lab) in enumerate(rows):
        b = ph(t, 1.8 + k * 0.7); y = 640 + k * 120 + dy
        d.text((100, y + (1 - b) * 20), v, font=fn("Black", 76), fill=SKYD + (int(255 * b),))
        d.text((100 + d.textlength(v, font=fn("Black", 76)) + 28, y + 26 + (1 - b) * 20), lab, font=fn("Bold", 40), fill=NAVY + (int(255 * b),))
    d.text((100, 1005 + dy), "doi:10.1073/pnas.2300582121", font=fn("Medium", 26), fill=(70, 88, 108, int(255 * a)))

# zoom: objects with real size (µm), the lens 'field' shrinks 10× steps
OBJ = [(5000, "mikroplastik ≤ 5 mm", "kunjut urug'idek"), (70, "soch tolasi", "≈ 70 µm"), (8, "qon hujayrasi", "≈ 8 µm"),
       (1, "nanoplastik", "< 1 µm"), (0.1, "eng kichigi topilgan", "≈ 100 nm")]
def zoom(d, t, T):
    cx, cy, R0 = 540, 790, 350
    a = ph(t, 0.0)
    d.ellipse([cx - R0 - 14, cy - R0 - 14, cx + R0 + 14, cy + R0 + 14], fill=(8, 22, 38, int(230 * a)))
    lay = Image.new("RGBA", (W, H)); ld = ImageDraw.Draw(lay)
    ld.ellipse([cx - R0, cy - R0, cx + R0, cy + R0], fill=(238, 244, 248, 255))
    # field width in µm (log-interpolated): 20 mm → 0.4 µm over 1.0..7.5 s
    u = max(0, min(1, (t - 1.0) / 6.5)); fw = 20000 * (0.4 / 20000) ** (u * u * (3 - 2 * u))
    px_per_um = 2 * R0 / fw
    cur = None
    for size, name, sub in OBJ:
        r = size * px_per_um / 2
        if 3 < r < 6000:
            col = {5000: (90, 90, 90), 70: (60, 40, 20), 8: (200, 60, 60), 1: SKYD, 0.1: WARN}[size]
            rr = min(r, 3000)
            if size == 70: ld.rectangle([cx - rr, 0, cx + rr, H], fill=col + (170,))
            else: ld.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col + (210,))
            if 40 < r < 360: cur = (name, sub, r)
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).ellipse([cx - R0, cy - R0, cx + R0, cy + R0], fill=int(255 * a))
    base = d._image; base.paste(lay, (0, 0), Image.composite(lay.getchannel("A"), Image.new("L", (W, H), 0), m) if False else m)
    # lens mask: repaint outside ring (keep shapes inside the circle)
    d.ellipse([cx - R0 - 14, cy - R0 - 14, cx + R0 + 14, cy + R0 + 14], outline=(8, 22, 38, int(255 * a)), width=24)
    # scale bar
    bar_um = 10 ** math.floor(math.log10(fw / 3)); bw = bar_um * px_per_um
    lab = f"{bar_um / 1000:g} mm" if bar_um >= 1000 else (f"{bar_um:g} µm" if bar_um >= 1 else f"{bar_um * 1000:g} nm")
    d.rectangle([cx - bw / 2, cy + R0 - 70, cx + bw / 2, cy + R0 - 58], fill=NAVY + (255,))
    d.text((cx, cy + R0 - 104), lab, font=fn("Bold", 30), fill=NAVY + (255,), anchor="ma")
    if cur:
        text(d, 80, 250, cur[0], fn("Black", 76), WHITE, 1.0)
        text(d, 80, 340, cur[1], fn("Bold", 46), SKY, 1.0)
    b = ph(t, 7.4)
    if b > 0:
        f = fn("Black", 64); s = "90% — nanoplastik"; w = d.textlength(s, font=f) + 70
        d.rounded_rectangle([(W - w) / 2, 1300 + (1 - b) * 20, (W + w) / 2, 1396 + (1 - b) * 20], 48, fill=SKY + (int(250 * b),))
        d.text((W / 2, 1348 + (1 - b) * 20), s, font=f, fill=NAVY + (int(255 * b),), anchor="mm")

def compare(d, t, T):
    text(d, 80, 280, "Avvalgi hisoblar", fn("ExtraBold", 60), WHITE, ph(t, 0.0))
    text(d, 80, 360, "faqat mikroplastik", fn("Bold", 42), SKY, ph(t, 0.3))
    base = 1050; x0, x1 = 180, 900
    a = ph(t, 0.8, 0.6); b = ph(t, 1.8, 1.4)
    d.rectangle([x0, base - 40 * a, x0 + 260, base], fill=WHITE + (235,))
    d.rectangle([x1 - 260, base - 520 * b, x1, base], fill=SKY + (245,))
    text(d, x0 + 130, base + 14, "eski", fn("Bold", 38), WHITE, a, "ma")
    text(d, x1 - 130, base + 14, "yangi (SRS)", fn("Bold", 38), WHITE, b, "ma")
    text(d, x1 - 130, base - 520 * b - 110, "10–100×", fn("Black", 92), SKY, ph(t, 3.2), "ma")

def types(d, t, T):
    text(d, 80, 280, "Eng ko'p topilganlari", fn("ExtraBold", 60), WHITE, ph(t, 0.0))
    for k, (nm, sub, t0) in enumerate((("Poliamid", "neylon · suv filtrlarida ishlatiladi", 1.0), ("PET", "butilkaning o'z plastigi", 2.6))):
        a = ph(t, t0); y = 420 + k * 260
        if a <= 0: continue
        d.rounded_rectangle([80, y + (1 - a) * 20, 1000, y + 210 + (1 - a) * 20], 30, fill=(8, 22, 38, int(205 * a)))
        d.text((120, y + 24 + (1 - a) * 20), nm, font=fn("Black", 88), fill=SKY + (int(255 * a),))
        d.text((120, y + 136 + (1 - a) * 20), sub, font=fn("Bold", 40), fill=WHITE + (int(255 * a),))
    text(d, 80, 960, "+ PVX, PMMA, polistirol ham bor", fn("Bold", 36), WHITE, ph(t, 4.4))

def caveat(d, t, T):
    a = ph(t, 0.0)
    d.rounded_rectangle([80, 300 + (1 - a) * 20, 1000, 640 + (1 - a) * 20], 30, fill=(8, 22, 38, int(210 * a)))
    d.text((120, 330), "Sog'liqqa ta'siri", font=fn("ExtraBold", 66), fill=WHITE + (int(255 * a),))
    d.text((120, 420), "hali isbotlanmagan", font=fn("Black", 80), fill=WARN + (int(255 * ph(t, 0.6)),))
    d.text((120, 540), "tadqiqotlar davom etmoqda", font=fn("Bold", 40), fill=SKY + (int(255 * ph(t, 1.2)),))
    b = ph(t, 3.0)
    if b > 0:
        d.rounded_rectangle([80, 700, 1000, 880], 30, fill=WHITE + (int(240 * b),))
        d.text((120, 726), "Xulosa:", font=fn("Bold", 38), fill=SKYD + (int(255 * b),))
        d.text((120, 780), "\"butilka\" ≠ \"plastiksiz\"", font=fn("Black", 62), fill=NAVY + (int(255 * b),))
    text(d, 80, 1100, "Manba: Qian et al., PNAS, 2024 · NIH Research Matters", fn("Medium", 26), WHITE, ph(t, 1.0))

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
        hud(d, T, name not in ("cta",)); SC[name](d, t, T)
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
    news.KEY = re.compile(r"\d|%|plastik|nanoplastik|mikroplastik|poliamid|pet|lazer|suvyektiv|qadrlang", re.I)
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
        fc.append(f"[{cur}][s{i}]xfade=transition={'fade' if i in (3, 6) else 'slideup'}:duration={XF}:offset={off:.3f}[x{i}]"); cur = f"x{i}"; off += S[i][2]
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
