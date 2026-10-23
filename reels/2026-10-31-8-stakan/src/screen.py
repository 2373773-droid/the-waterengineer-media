"""'8 stakan suv' reel — SCREEN-RECORD style: the real article pages (Science/PMC full text, Valtin 2002 PDF,
Dartmouth release) shown as a phone screen recording: scroll, zoom, marker highlights drawn under the text,
touch dots, Uzbek gloss chips. Hook/CTA on real footage with big type. Captions: same renderer as before.
usage: screen.py seg [i ...] | caps | build out.mp4 [--nocaps]"""
import sys, re, json, math, subprocess
sys.path.insert(0, "/home/claude/r2")
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
R = "/home/claude/r5/"
W, H, FPS = 1080, 1920, 30
F = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
_fc = {}
def fn(w, s):
    if (w, s) not in _fc: _fc[(w, s)] = ImageFont.truetype(F.format(w), s)
    return _fc[(w, s)]
WHITE, SKY, SKYD, NAVY, WARN = (255, 255, 255), (132, 210, 253), (31, 111, 178), (11, 31, 51), (226, 88, 62)
MARK_SKY, MARK_HOT = (150, 215, 255), (255, 196, 120)
def ease(u): u = max(0, min(1, u)); return u * u * (3 - 2 * u)
def eout(u): u = max(0, min(1, u)); return 1 - (1 - u) ** 3
def ph(t, t0, d=0.5): return eout((t - t0) / d)

# ---------- page sources ----------
PAGES = {}
def page(key):
    if key in PAGES: return PAGES[key]
    if key == "pmc":   img, rects, sc, url = "scr/pmc_full.png", json.load(open(R + "scr/pmc_rects.json")), 2.5, "pmc.ncbi.nlm.nih.gov"
    elif key == "dart": img, rects, sc, url = "scr/dart_full.png", json.load(open(R + "scr/dart_rects.json")), 2.5, "geiselmed.dartmouth.edu"
    elif key in ("v1", "v3"):
        pg = key[1]; img = f"scr/v{pg}-0{pg}.png"; sc = 1.0; url = "journals.physiology.org · PDF"
        rects = {k.split(":", 1)[1]: v for k, v in json.load(open(R + "scr/valtin_rects.json")).items() if k.startswith(pg + ":")}
    im = Image.open(R + img).convert("RGB")
    rr = {k: [[c * sc for c in q] for q in v] for k, v in rects.items() if v}
    PAGES[key] = (im, rr, url); return PAGES[key]

def _band():
    b = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(b)
    for y in range(1120, 1320):
        u = 1 - abs(y - 1220) / 100; d.line([(0, y), (W, y)], fill=(8, 20, 34, int(175 * min(1, u * 1.6))))
    return b
CAPBAND = _band()
TOP = 190                       # status + url bar height; page viewport is TOP..H
VH = H - TOP

def chrome(d, url, pdf=False):
    d.rectangle([0, 0, W, TOP], fill=(246, 247, 249))
    d.text((60, 30), "16:00", font=fn("SemiBold", 34), fill=(20, 20, 20))
    d.rounded_rectangle([930, 36, 990, 66], 8, outline=(20, 20, 20), width=3); d.rectangle([936, 42, 978, 60], fill=(20, 20, 20))
    d.rounded_rectangle([40, 92, W - 40, 170], 22, fill=(229, 231, 235))
    tw = d.textlength(url, font=fn("Medium", 32))
    d.text(((W - tw) / 2 + 18, 112), url, font=fn("Medium", 32), fill=(30, 30, 30))
    lx = (W - tw) / 2 - 22                                          # padlock
    d.rounded_rectangle([lx - 12, 124, lx + 12, 146], 4, fill=(90, 90, 90)); d.arc([lx - 9, 108, lx + 9, 132], 180, 360, fill=(90, 90, 90), width=4)

def cam_at(keys, t):
    """keys: list of (t, y_top, zoom, x_left) in page px; smooth-step between keys"""
    if t <= keys[0][0]: return keys[0][1:]
    for (t0, *a), (t1, *b) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            u = ease((t - t0) / max(1e-6, t1 - t0)); return tuple(x + (y - x) * u for x, y in zip(a, b))
    return keys[-1][1:]

def view(key, keys, t, marks):
    """render the page viewport; marks = list of (phrase, t_start, dur, colour)"""
    im, rects, url = page(key)
    y, z, x = cam_at(keys, t)
    cw, ch = W / z, VH / z
    x = max(0, min(im.width - cw, x)); y = max(0, min(im.height - ch, y))
    box = (int(x), int(y), int(x + cw), int(y + ch))
    crop = im.crop(box)
    # marker highlights: multiply-blend, sweep left→right line by line
    m = Image.new("RGB", crop.size, (255, 255, 255)); md = ImageDraw.Draw(m)
    for phrase, ts, dur, col in marks:
        if t < ts or phrase not in rects: continue
        lines = rects[phrase]; total = sum(q[2] - q[0] for q in lines); done = total * eout((t - ts) / dur)
        for q in lines:
            w = q[2] - q[0]; f = min(w, max(0, done)); done -= w
            if f <= 0: break
            pad = (q[3] - q[1]) * 0.12
            md.rectangle([q[0] - box[0] - 4, q[1] - box[1] - pad, q[0] - box[0] + f + 4, q[3] - box[1] + pad], fill=col)
    crop = ImageChops.multiply(crop, m)
    crop = crop.resize((W, VH), Image.BICUBIC if z < 1.4 else Image.LANCZOS)
    fr = Image.new("RGB", (W, H), WHITE); fr.paste(crop, (0, TOP))
    out = fr.convert("RGBA"); chrome(ImageDraw.Draw(out), url)
    out.alpha_composite(CAPBAND)                                   # dark band so the white captions stay readable
    return out, (box, z)

def to_screen(key, cam, pt):
    (bx0, by0, bx1, by1), z = cam
    return ((pt[0] - bx0) * z, TOP + (pt[1] - by0) * z)

def touch(im, x, y, a):
    if a <= 0: return
    l = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(l); r = 44 + 18 * (1 - a)
    d.ellipse([x - r, y - r, x + r, y + r], fill=(120, 120, 120, int(110 * a)), outline=(255, 255, 255, int(200 * a)), width=4)
    im.alpha_composite(l)

def chip(im, s, a, y=1330, col=NAVY, sub=None):
    """Uzbek gloss chip (kept below the caption band, above IG UI)"""
    if a <= 0: return
    d = ImageDraw.Draw(im); f = fn("ExtraBold", 50)
    w = d.textlength(s, font=f) + 70; x0 = (W - w) / 2; yy = y + (1 - a) * 30
    l = Image.new("RGBA", (W, H)); ld = ImageDraw.Draw(l)
    ld.rounded_rectangle([x0, yy, x0 + w, yy + 96 + (52 if sub else 0)], 28, fill=col + (int(235 * a),))
    ld.text((W / 2, yy + 48), s, font=f, fill=WHITE + (int(255 * a),), anchor="mm")
    if sub: ld.text((W / 2, yy + 112), sub, font=fn("SemiBold", 30), fill=SKY + (int(255 * a),), anchor="mm")
    im.alpha_composite(l)

def tag(im, s, a):
    """small source chip, bottom-left of the page area"""
    if a <= 0: return
    d = ImageDraw.Draw(im); f = fn("Bold", 28); w = d.textlength(s, font=f) + 40
    d.rounded_rectangle([40, 1520, 40 + w, 1576], 28, fill=SKYD + (int(230 * a),))
    d.text((60, 1532), s, font=f, fill=WHITE + (int(255 * a),))

def R_(key, phrase): return page(key)[1][phrase]
def y_of(key, phrase, frac=0.38, z=1.0):
    """y_top so that the phrase sits at `frac` of the viewport"""
    q = R_(key, phrase); return q[0][1] - VH / z * frac

# ---------- screen scenes ----------
P_T = "Variation in human water turnover associated with environmental and lifestyle factors"
P_N = "5,604 people from the ages of 8 days to 96 years from 26 countries"
P_R = "the low end for men and women is ~1–1.5 L/day while the upper end is around ~6 L/day"
P_M, P_F = "has a predicted WT of 3.2 L/d", "will have a WT of 2.7 L/d"
P_EQ = "is not equal to daily water intake from liquids and foods"
P_A, P_H = "Athletes have ~1000 ml more WT than do non-athletes", "a 50% increase in relative humidity induces a ~300 ml increase in WT"
P_1 = "one size does not fit all for drinking water guidelines"
P_8 = "the common suggestion that we should drink 8 × 8oz glasses of water per day (approx. 2 L) is not backed by objective evidence"
D_T, D_C, D_Q = "Dartmouth Professor Finds No Scientific Evidence for '8 x 8'", "caffeinated drinks, such as most coffee, tea and soft drinks, may indeed be counted toward the daily total", "thirst begins when the concentration of blood (an accurate indicator of our state of hydration) has risen by less than two percent"
V_45, V_25, V_PF = "1945 the Food and Nutrition Board", "A suitable allowance of water for adults is 2.5 liters daily", "Most of this quantity is contained in prepared foods."
V_T, V_L = "Drink at least eight glasses of water a day.", "rigorous proof for this counsel appears to be lacking."

def s_origin(t):
    k = "v3"; im = page(k)[0]
    yp = R_(k, V_45)[0][1]
    keys = [(0, 0, 0.5, 0), (1.6, yp - 900, 0.5, 0), (2.6, yp - 380, 1.0, 0)]
    fr, cam = view(k, keys, t, [(V_45, 2.9, 0.6, MARK_SKY), (V_25, 3.8, 1.0, MARK_SKY), (V_PF, 5.6, 0.9, MARK_HOT)])
    touch(fr, 760, 1400 - 500 * ease((t - 0.3) / 1.2), 1 - abs(ph(t, 0.2, 0.3) - ph(t, 1.5, 0.3)))
    tag(fr, "Valtin, Am J Physiol, 2002", ph(t, 0.4))
    chip(fr, "1945: kattalarga kuniga 2,5 L", ph(t, 4.2) * (1 - ph(t, 5.5, 0.25)))
    chip(fr, "«Ko'p qismi — tayyor ovqatda»", ph(t, 6.0), col=WARN, sub="← shu jumla unutilgan")
    return fr

def s_valtin(t):
    k = "v1"; yt = R_(k, V_T)[0][1]
    keys = [(0, 0, 0.5, 0), (1.0, 0, 0.5, 0), (2.0, yt - 300, 0.9, 0)]
    fr, cam = view(k, keys, t, [(V_T, 1.3, 0.8, MARK_SKY), (V_L, 2.8, 1.0, MARK_HOT)])
    tag(fr, "Valtin, Am J Physiol, 2002", ph(t, 0.3))
    chip(fr, "«Qat'iy dalil topilmadi»", ph(t, 3.4), col=WARN)
    return fr

def s_caff(t):
    k = "dart"; y0 = y_of(k, D_T, 0.25); y1 = y_of(k, D_C, 0.40)
    keys = [(0, y0, 1.0, 0), (1.2, y0, 1.0, 0), (2.2, y1, 1.0, 0)]
    fr, cam = view(k, keys, t, [(D_T, 0.3, 0.7, MARK_SKY), (D_C, 2.3, 1.2, MARK_SKY)])
    touch(fr, 800, 1450 - 600 * ease((t - 1.1) / 1.1), 1 - abs(ph(t, 1.0, 0.2) - ph(t, 2.1, 0.2)))
    tag(fr, "Dartmouth, 2002", ph(t, 0.2))
    chip(fr, "Choy va qahva ham hisobga kiradi", ph(t, 2.8))
    return fr

def s_science(t):
    k = "pmc"; yt = y_of(k, P_T, 0.30); yn = y_of(k, P_N, 0.40)
    keys = [(0, 0, 1.0, 0), (1.0, 0, 1.0, 0), (2.2, yt, 1.0, 0), (4.0, yt, 1.0, 0), (5.0, yn, 1.0, 0)]
    fr, cam = view(k, keys, t, [(P_T, 2.4, 1.0, MARK_SKY), (P_N, 5.2, 1.2, MARK_HOT)])
    touch(fr, 820, 1500 - 700 * ease((t - 1.0) / 1.2), 1 - abs(ph(t, 0.9, 0.2) - ph(t, 2.2, 0.2)))
    tag(fr, "Yamada et al., Science, 2022", ph(t, 0.3))
    chip(fr, "26 davlat · 5 604 kishi", ph(t, 5.8), sub="8 kunlikdan 96 yoshgacha")
    return fr

def s_results(t):
    k = "pmc"; yr = y_of(k, P_R, 0.40); ym = y_of(k, P_M, 0.35)
    keys = [(0, yr - 900, 1.0, 0), (1.0, yr, 1.0, 0), (4.0, yr, 1.0, 0), (5.0, ym, 1.0, 0)]
    fr, cam = view(k, keys, t, [(P_R, 1.2, 1.4, MARK_SKY), (P_M, 5.3, 0.6, MARK_HOT), (P_F, 6.6, 0.6, MARK_HOT)])
    chip(fr, "1 L dan 6 L gacha", ph(t, 2.2) * (1 - ph(t, 4.4, 0.25)), sub="odamdan odamga farq qiladi")
    chip(fr, "Yigit 70 kg ≈ 3,2 L · Qiz 60 kg ≈ 2,7 L", ph(t, 6.0))
    return fr

def s_food(t):
    k = "pmc"; y = y_of(k, P_EQ, 0.40)
    keys = [(0, y - 700, 1.0, 0), (1.0, y, 1.0, 0)]
    fr, cam = view(k, keys, t, [(P_EQ, 1.2, 1.0, MARK_HOT)])
    chip(fr, "≠ faqat ichilgan suv", ph(t, 1.8), col=WARN, sub="ovqatdagi suv ham kiradi")
    return fr

def s_factors(t):
    k = "pmc"; y = y_of(k, P_H, 0.22)
    keys = [(0, y - 800, 1.0, 0), (1.0, y, 1.0, 0)]
    fr, cam = view(k, keys, t, [(P_A, 1.2, 0.9, MARK_SKY), (P_H, 3.8, 1.0, MARK_SKY)])
    chip(fr, "Sportchilar: + ~1 L", ph(t, 1.9) * (1 - ph(t, 3.6, 0.25)))
    chip(fr, "Namlik +50%: + 0,3 L", ph(t, 4.4))
    return fr

def s_verdict(t):
    k = "pmc"; y = y_of(k, P_1, 0.32)
    keys = [(0, y - 900, 1.0, 0), (1.2, y, 1.0, 0)]
    fr, cam = view(k, keys, t, [(P_1, 1.4, 0.9, MARK_SKY), (P_8, 3.0, 2.0, MARK_HOT)])
    chip(fr, "Hammaga bir xil me'yor yo'q", ph(t, 2.0) * (1 - ph(t, 4.8, 0.25)))
    chip(fr, "8 stakan — obyektiv dalil yo'q", ph(t, 5.1), col=WARN, sub="Science, 2022")
    return fr

def s_thirst(t):
    k = "dart"; y = y_of(k, D_Q, 0.35)
    keys = [(0, y - 700, 1.0, 0), (0.9, y, 1.0, 0)]
    fr, cam = view(k, keys, t, [(D_Q, 1.0, 1.6, MARK_SKY)])
    tag(fr, "Dartmouth, 2002", ph(t, 0.2))
    chip(fr, "Chanqoq — eng yaxshi signal", ph(t, 2.4), sub="qon < 2% quyuqlashganda boshlanadi")
    return fr

# (kind, footage-or-fn, footage start, dur, caption)
S = [("foot", "8253", 1.0, 6.5, "Kuniga 8 stakan suv ichish kerak — buni hamma eshitgan. Lekin bu ilmiy asoslanganmi? Keling, maqolani o'zim ochib ko'raman."),
     ("scr", s_science, 0, 8.0, "2022 yilda Science jurnalida katta tadqiqot chiqdi: 26 davlatdan 5 604 kishi, 8 kunlikdan 96 yoshgacha."),
     ("scr", s_results, 0, 9.5, "Natija: kunlik suv almashinuvi 1 litrdan 6 litrgacha farq qiladi. 20 yoshli, 70 kilolik yigitda taxminan 3,2 litr, 60 kilolik qizda 2,7 litr."),
     ("scr", s_food, 0, 5.0, "Lekin bu faqat ichilgan suv emas: ovqatdagi suv ham shunga kiradi."),
     ("scr", s_factors, 0, 7.0, "Sportchilarda kuniga taxminan 1 litr ko'proq. Havo namligi 50 foiz oshsa — yana 0,3 litr."),
     ("scr", s_verdict, 0, 8.0, "Maqola xulosasi: hammaga bir xil me'yor yo'q, 8 stakan tavsiyasi esa obyektiv dalil bilan tasdiqlanmagan."),
     ("foot", "95", 3.0, 6.5, "Suvni qadrlang! Suv haqida bilmoqchi bo'lganlaringizni izohlarda yozib qoldiring. Bizni kuzatishda davom eting, suv haqida suvyektiv fikrlaymiz!")]
XF = 0.25
TOTAL = sum(s[3] for s in S)
STARTS = [sum(s[3] for s in S[:i]) for i in range(len(S))]

# ---------- footage scenes (big type) ----------
def big(d, x, y, s, f, col, a, anchor="la"):
    if a <= 0: return
    y += (1 - a) * 30
    d.text((x + 4, y + 6), s, font=f, fill=(0, 0, 0, int(120 * a)), anchor=anchor)
    d.text((x, y), s, font=f, fill=col + (int(255 * a),), anchor=anchor)

def o_hook(im, d, t):
    big(d, 540, 330, "Kuniga", fn("ExtraBold", 80), WHITE, ph(t, 0.0), "ma")
    n = max(1, int(round(8 * ph(t, 0.3, 1.4))))
    big(d, 540, 420, f"{n}", fn("Black", 420), WHITE, ph(t, 0.1), "ma")
    big(d, 540, 860, "STAKAN SUV", fn("Black", 110), WHITE, ph(t, 0.5), "ma")
    big(d, 540, 1000, "ilmiy asosi bormi?", fn("ExtraBold", 72), SKY, ph(t, 2.3), "ma")
    a = ph(t, 4.4)
    if a > 0:
        w = d.textlength("Maqolani ochamiz →", font=fn("Bold", 46)) + 70
        d.rounded_rectangle([(W - w) / 2, 1310, (W + w) / 2, 1400], 45, fill=WHITE + (int(240 * a),))
        d.text((W / 2, 1355), "Maqolani ochamiz →", font=fn("Bold", 46), fill=NAVY + (int(255 * a),), anchor="mm")

def o_cta(im, d, t):
    big(d, 540, 360, "Suvni", fn("Black", 150), WHITE, ph(t, 0.0), "ma")
    big(d, 540, 520, "qadrlang!", fn("Black", 150), SKY, ph(t, 0.2), "ma")
    big(d, 540, 760, "Suv haqida bilmoqchi bo'lganlaringizni", fn("Bold", 42), WHITE, ph(t, 0.8), "ma")
    a = ph(t, 1.1)
    w = d.textlength("izohlarda yozib qoldiring ↓", font=fn("Bold", 46)) + 70
    d.rounded_rectangle([(W - w) / 2, 820, (W + w) / 2, 910], 45, fill=SKY + (int(255 * a),))
    d.text((W / 2, 865), "izohlarda yozib qoldiring ↓", font=fn("Bold", 46), fill=NAVY + (int(255 * a),), anchor="mm")
    big(d, 540, 960, "suv haqida suvyektiv fikrlaymiz!", fn("ExtraBold", 50), WHITE, ph(t, 1.8), "ma")
    big(d, 540, 1040, "Doktor H₂O · @suvyektiv", fn("Bold", 40), SKY, ph(t, 2.4), "ma")

def seg(i):
    kind, src, ss, dur, cap = S[i]; L = dur + XF; out = R + f"seg/{i:02d}.mp4"
    if kind == "scr":
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-crf", "14", "-preset", "veryfast", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for f in range(int(round(L * FPS))): p.stdin.write(src(f / FPS).tobytes())
        p.stdin.close(); p.wait()
    else:
        ov = R + f"seg/ov{i:02d}.mov"; fnc = o_hook if i == 0 else o_cta
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "qtrle", ov], stdin=subprocess.PIPE)
        for f in range(int(round(L * FPS))):
            im = Image.new("RGBA", (W, H)); fnc(im, ImageDraw.Draw(im), f / FPS); p.stdin.write(im.tobytes())
        p.stdin.close(); p.wait()
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-i", R + f"px/{src}.mp4", "-i", ov, "-filter_complex",
                        f"[0:v]fps=30,trim=0:{L:.3f},setpts=PTS-STARTPTS,scale=-2:1920,crop=1080:1920,eq=brightness=-0.10:saturation=0.9,gblur=sigma=1.5[b];"
                        f"[b][1:v]overlay=format=auto,format=yuv420p", "-t", f"{L:.3f}", "-c:v", "libx264", "-crf", "14", "-preset", "veryfast", out], check=True)

def caps():
    import news
    news.KEY = re.compile(r"\d|%|litr|stakan|science|valtin|ovqat|chanqoq|suvyektiv|qadrlang|dalil", re.I)
    news.caps_render([(STARTS[i] + 0.12, STARTS[i] + s[3] - 0.12, s[4]) for i, s in enumerate(S)], TOTAL, R + "seg/caps.mov")

def build(out, use_caps=True):
    inputs, fc = [], []
    for i in range(len(S)):
        inputs += ["-i", R + f"seg/{i:02d}.mp4"]; fc.append(f"[{i}:v]settb=1/30,fps=30,format=yuv420p[s{i}]")
    cur, off = "s0", S[0][3]
    for i in range(1, len(S)):
        tr = "slideleft" if S[i][0] == "scr" and S[i - 1][0] == "scr" else "fade"
        fc.append(f"[{cur}][s{i}]xfade=transition={tr}:duration={XF}:offset={off:.3f}[x{i}]"); cur = f"x{i}"; off += S[i][3]
    n = len(S); last = cur
    if use_caps:
        inputs += ["-i", R + "seg/caps.mov"]; fc.append(f"[{cur}][{n}:v]overlay=format=auto[cv]"); last = "cv"; n += 1
    fc.append(f"[{last}]fade=in:d=0.3,fade=out:st={off - 0.6:.3f}:d=0.6,format=yuv420p[V]")
    inputs += ["-i", R + "seg/music.wav"]
    fc.append(f"[{n}:a]atrim=0:{off:.3f},afade=t=out:st={off - 1.5:.3f}:d=1.5,loudnorm=I=-16:TP=-1.5[A]")
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + inputs + ["-filter_complex", ";".join(fc), "-map", "[V]", "-map", "[A]", "-t", f"{off:.3f}",
                    "-c:v", "libx264", "-crf", "20", "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
    print("total", round(off, 2))

if __name__ == "__main__":
    a = sys.argv[1]
    import os; os.makedirs(R + "seg", exist_ok=True)
    if a == "seg":
        for i in ([int(x) for x in sys.argv[2:]] or range(len(S))): seg(i); print("seg", i)
    elif a == "still":
        i, t = int(sys.argv[2]), float(sys.argv[3]); S[i][1](t).convert("RGB").save(sys.argv[4])
    elif a == "caps": caps()
    elif a == "build": build(sys.argv[2], "--nocaps" not in sys.argv)
