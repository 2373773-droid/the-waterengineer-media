"""B-roll for '4 778 litr' reel: real Pixabay footage, vertical 1080x1920, slow push-in, crossfades,
optional number titles. usage: build_broll.py out.mp4 [--clean]"""
import sys, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
CLEAN = "--clean" in sys.argv
F = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
XF = 0.4
# file, start, dur, crop-x fraction, title, subtitle
S = [("Z1", 4.5, 5.0, .33, "4 778 litr", "kishi boshiga · har kuni"),
     ("P0", 0.0, 3.5, .50, "≈ 24 ta vanna", "har kuni, har bir odamga"),
     ("G2", 2.0, 3.5, .38, "Dunyoda 4-o'rin", "kishi boshiga suv sarfi"),
     ("G6", 0.0, 3.0, .50, "1-o'rin: Turkmaniston", "kuniga 15 445 litr"),
     ("Q0", 0.0, 2.5, .50, "90% dan ko'p", "suv dalalarga ketadi"),
     ("U2", 2.0, 3.5, .50, "paxta · bug'doy · sholi", ""),
     ("D0", 1.0, 4.5, .50, "36% yo'qoladi", "tuproq kanallarda"),
     ("V5", 2.0, 4.0, .50, "14 mlrd m³", "har yili yerga singib, bug'lanib"),
     ("T4", 5.0, 2.5, .50, "Beton kanallar", ""),
     ("W5", 3.0, 2.0, .62, "zamonaviy sug'orish", "")]

def title_png(i, t, sub):
    im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    if not CLEAN and t:
        d = ImageDraw.Draw(im)
        f1 = ImageFont.truetype(F.format("Black"), 120 if len(t) < 14 else 84)
        f2 = ImageFont.truetype(F.format("SemiBold"), 50)
        band = Image.new("RGBA", im.size, (0, 0, 0, 0)); db = ImageDraw.Draw(band)
        db.ellipse([-200, 470, 1280, 860], fill=(0, 0, 0, 120))
        im = Image.alpha_composite(im, band.filter(ImageFilter.GaussianBlur(70))); d = ImageDraw.Draw(im)
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
        for (txt, f, y) in [(t, f1, 560), (sub, f2, 720)]:
            if not txt: continue
            w = d.textlength(txt, font=f)
            ds.text(((1080 - w) / 2, y + 4), txt, font=f, fill=(0, 0, 0, 200))
        im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(10))); d = ImageDraw.Draw(im)
        for (txt, f, y) in [(t, f1, 560), (sub, f2, 720)]:
            if not txt: continue
            w = d.textlength(txt, font=f)
            d.text(((1080 - w) / 2, y), txt, font=f, fill=(255, 255, 255, 255))
    p = f"/home/claude/r2/title_{i}.png"; im.save(p); return p

inputs, fc = [], []
for i, (k, ss, dur, cx, t, sub) in enumerate(S):
    L = dur + XF
    inputs += ["-ss", str(ss), "-i", f"/home/claude/r2/px/{k}.mp4", "-loop", "1", "-i", title_png(i, t, sub)]
    v, g = 2 * i, 2 * i + 1
    fc.append(f"[{v}:v]fps=30,trim=0:{L:.3f},setpts=PTS-STARTPTS,scale=w=-2:h='1920*(1.0+0.05*t/{L:.3f})':eval=frame:flags=bicubic,"
              f"crop=1080:1920:(iw-1080)*{cx}:(ih-1920)/2,setsar=1,eq=saturation=1.06:contrast=1.03,format=yuv420p[v{i}]")
    fc.append(f"[{g}:v]trim=0:{L:.3f},setpts=PTS-STARTPTS,format=rgba,fade=in:st=0.35:d=0.4:alpha=1,fade=out:st={L-0.6:.3f}:d=0.35:alpha=1[g{i}];"
              f"[v{i}][g{i}]overlay=format=auto,format=yuv420p,fps=30,settb=1/30[s{i}]")
cur, off = "s0", S[0][2]
for i in range(1, len(S)):
    fc.append(f"[{cur}][s{i}]xfade=transition=fade:duration={XF}:offset={off:.3f}[x{i}]")
    cur = f"x{i}"; off += S[i][2]
fc.append(f"[{cur}]fade=in:d=0.4,fade=out:st={off+XF-0.5:.3f}:d=0.5[V]")
subprocess.run(["ffmpeg", "-v", "error", "-y"] + inputs + ["-filter_complex", ";".join(fc), "-map", "[V]", "-an",
                "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p", "-movflags", "+faststart", sys.argv[1]], check=True)
# scene list
t = 0
for k, ss, dur, cx, ti, sub in S:
    print(f"{t:5.1f}s  {k:3s} {ti} {('— ' + sub) if sub else ''}"); t += dur
