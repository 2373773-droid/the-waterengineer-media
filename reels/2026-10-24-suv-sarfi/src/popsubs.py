"""2026 'MrBeast/Hormozi' style captions: 1-3 words on screen, words pop in one by one (scale bounce),
key words/numbers in yellow, heavy font with thick outline, centred in the safe middle zone.
Input: list of (start, end, text). Output: ASS. usage as module: write_ass(lines, path, y=1150)"""
import re
YEL, WHITE = "&H0000E1FF", "&H00FFFFFF"   # ASS BGR: yellow #FFE100
KEY = re.compile(r"\d|%|litr|o'rin|vanna|dalalar|yo'qoladi|milliard|kub|Turkmaniston|O'zbekiston|suvyektiv", re.I)

def ts(t):
    return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"

def chunks(words, n=3, maxc=14):
    out, cur = [], []
    for w in words:
        if cur and (len(cur) >= n or len(" ".join(cur + [w])) > maxc or cur[-1][-1] in ",.?!"):
            out.append(cur); cur = []
        cur.append(w)
    if cur: out.append(cur)
    return out

def write_ass(lines, path, y=1150):
    ev = []
    for a, b, txt in lines:
        txt = re.sub(r'(\d) (\d)', '\\1\u00a0\\2', txt).replace('.', ''); words = txt.split(' '); tot = sum(len(w) + 1 for w in words)
        t = a
        wt = [(b - a) * (len(w) + 1) / tot for w in words]
        k = 0
        for ch in chunks(words):
            t0 = t; durs = wt[k:k + len(ch)]; t1 = t0 + sum(durs)
            # each word appears at its own time with a pop; the chunk stays until its end
            for j in range(len(ch)):
                s = t0 + sum(durs[:j]); e = t1 if j == len(ch) - 1 else t0 + sum(durs[:j + 1])
                parts = []
                for m, w in enumerate(ch[:j + 1]):
                    col = YEL if KEY.search(w) else WHITE
                    pop = r"\fscx72\fscy72\t(0,90,\fscx112\fscy112)\t(90,160,\fscx100\fscy100)" if m == j else ""
                    parts.append(f"{{\\c{col}{pop}}}{w.upper()}")
                ev.append(f"Dialogue: 0,{ts(s)},{ts(e)},P,,0,0,0,,{{\\an5\\pos(540,{y})}}" + " ".join(parts))
            t = t1; k += len(ch)
    hdr = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: P,Inter Black,122,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,1,0,1,8,5,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    open(path, "w").write(hdr + "\n".join(ev) + "\n")

if __name__ == "__main__":
    demo = [(0.3, 4.6, "Statistikaga ko'ra, O'zbekistonda kishi boshiga kuniga 4 778 litr!"),
            (5.0, 8.3, "Bu har kuni taxminan 24 ta to'la vanna degani."),
            (8.6, 14.6, "Shu ko'rsatkich bo'yicha O'zbekiston dunyoda 4-o'rinda.")]
    write_ass(demo, "/home/claude/r2/demo.ass")
