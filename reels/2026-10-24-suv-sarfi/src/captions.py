"""2026 'Submagic/Hormozi' captions rendered with Pillow into a transparent overlay video.
- 1-3 words per screen, UPPERCASE, heavy font with thick black stroke
- the word being spoken sits in a tilted yellow box (black text) and pops (0.8 -> 1.1 -> 1.0)
- numbers / key words stay yellow when not active; each new chunk slides up 24 px
usage (module): render(lines, dur, out_mov, y=1150)   lines = [(start, end, text)]"""
import re, math, subprocess
from PIL import Image, ImageDraw, ImageFont
W, H, FPS = 1080, 1920, 30
FONT = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Black.otf", 104)
YEL, WHITE, BLACK = (255, 225, 0), (255, 255, 255), (0, 0, 0)
KEY = re.compile(r"\d|%|litr|o'rin|vanna|dala|yo'qol|milliard|kub|turkmaniston|o'zbekiston|suvyektiv|kanal", re.I)

def chunks(words, n=3, maxc=15):
    out, cur = [], []
    for w in words:
        if cur and (len(cur) >= n or len(" ".join(cur + [w])) > maxc or cur[-1][-1] in ",.?!:"):
            out.append(cur); cur = []
        cur.append(w)
    if cur: out.append(cur)
    return out

def timeline(lines):
    """-> list of (t0, t1, words, word_starts)"""
    ev = []
    for a, b, txt in lines:
        txt = re.sub(r"(\d) (\d)", "\\1\u00a0\\2", txt)
        words = [w.strip(".") for w in txt.split(" ") if w.strip(".")]
        tot = sum(len(w) + 2 for w in words); t = a; k = 0
        dur = [(b - a) * (len(w) + 2) / tot for w in words]
        for ch in chunks(words):
            ds = dur[k:k + len(ch)]; starts = [t + sum(ds[:j]) for j in range(len(ch))]
            ev.append((t, t + sum(ds), ch, starts)); t += sum(ds); k += len(ch)
    return ev

def pop(u):  # 0..1 over 0.18 s
    if u >= 1: return 1.0
    return 0.8 + 0.3 * math.sin(min(1, u) * math.pi * 0.75) if u < 0.66 else 1.1 - 0.1 * (u - 0.66) / 0.34

def frame(ev, t, y):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cur = [e for e in ev if e[0] <= t < e[1]]
    if not cur: return im
    t0, t1, ws, st = cur[0]
    shown = [j for j in range(len(ws)) if st[j] <= t]
    act = shown[-1]
    lift = max(0, 24 * (1 - (t - t0) / 0.12))
    d = ImageDraw.Draw(im)
    sizes = [d.textlength(w.upper(), font=FONT) for w in ws]
    gap = 26; total = sum(sizes) + gap * (len(ws) - 1)
    x = (W - total) / 2
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for j, w in enumerate(ws):
        if j not in shown: x += sizes[j] + gap; continue
        s = pop((t - st[j]) / 0.18)
        word = Image.new("RGBA", (int(sizes[j]) + 80, 190), (0, 0, 0, 0)); dw = ImageDraw.Draw(word)
        if j == act:
            dw.rounded_rectangle([12, 22, sizes[j] + 68, 168], 22, fill=YEL + (255,))
            dw.text((40, 30), w.upper(), font=FONT, fill=BLACK)
        else:
            col = YEL if KEY.search(w) else WHITE
            dw.text((40, 30), w.upper(), font=FONT, fill=col, stroke_width=10, stroke_fill=BLACK)
        if j == act: word = word.rotate(-3 if (len(ev) + j) % 2 else 3, resample=Image.BICUBIC, expand=False)
        if s != 1: word = word.resize((int(word.width * s), int(word.height * s)), Image.BICUBIC)
        cx = x + sizes[j] / 2; cy = y + lift
        layer.alpha_composite(word, (int(cx - word.width / 2), int(cy - word.height / 2)))
        x += sizes[j] + gap
    # soft shadow under the whole chunk
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sh.putalpha(layer.getchannel("A").point(lambda v: v * 0.45))
    from PIL import ImageFilter
    sh = sh.filter(ImageFilter.GaussianBlur(8))
    im.alpha_composite(sh, (0, 8)); im.alpha_composite(layer)
    return im

def render(lines, dur, out, y=1150):
    ev = timeline(lines)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "qtrle", out], stdin=subprocess.PIPE)
    for f in range(int(dur * FPS)):
        p.stdin.write(frame(ev, f / FPS, y).tobytes())
    p.stdin.close(); p.wait()

if __name__ == "__main__":
    demo = [(0.25, 4.8, "Statistikaga ko'ra, O'zbekistonda kishi boshiga kuniga 4 778 litr!"),
            (5.2, 8.9, "Hisob oddiy: yiliga 54,5 milliard kub metr suv"),
            (9.0, 13.2, "365 kunga va aholiga bo'lsak, 4 778 litr chiqadi!"),
            (13.6, 17.0, "Bu har kuni 24 ta to'la vanna degani!")]
    render(demo, 18.0, "/home/claude/r2/caps_demo.mov")
