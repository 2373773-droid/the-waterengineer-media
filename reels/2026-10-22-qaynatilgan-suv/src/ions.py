"""Animated 'ions stay in water' panel, 1080x900. usage: ions.py out.mp4 duration"""
import sys, math, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
out, DUR = sys.argv[1], float(sys.argv[2])
W, H, FPS = 1080, 900, 30
F = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
fb = lambda s: ImageFont.truetype(F.format("ExtraBold"), s)
fs = lambda s: ImageFont.truetype(F.format("SemiBold"), s)
NAVY, SKY = (11, 31, 51), (132, 210, 253)
METAL, SALT = (255, 170, 60), (132, 210, 253)
rng = np.random.default_rng(11)
# background: water gradient
bg = Image.new("RGB", (W, H))
g = np.linspace(0, 1, H)[:, None]
top, bot = np.array([28, 92, 150]), np.array([8, 30, 62])
arr = (top * (1 - g) + bot * g)[:, None, :].repeat(W, 1).reshape(H, W, 3)
bg = Image.fromarray(arr.astype(np.uint8))
# caustic light streaks
cl = Image.new("L", (W, H), 0); d = ImageDraw.Draw(cl)
for i in range(7):
    x = rng.uniform(0, W); d.polygon([(x, 0), (x + 90, 0), (x - 160, H), (x - 300, H)], fill=26)
bg = Image.composite(Image.new("RGB", (W, H), (180, 230, 255)), bg, cl.filter(ImageFilter.GaussianBlur(30)))
ions = [("Pb²⁺", METAL), ("Hg²⁺", METAL), ("Cd²⁺", METAL), ("As", METAL),
        ("Na⁺", SALT), ("Cl⁻", SALT), ("NO₃⁻", SALT), ("SO₄²⁻", SALT)]
slots = [(200, 300), (520, 250), (850, 330), (330, 520), (720, 480), (160, 700), (520, 690), (880, 640)]
order = [0, 4, 1, 5, 2, 6, 3, 7]
P = []
for k, i in enumerate(order):
    name, col = ions[i]; x, y = slots[k]
    P.append(dict(name=name, col=col, x=x + rng.uniform(-30, 30), y=y + rng.uniform(-20, 20), r=rng.uniform(78, 92),
                  t0=0.25 + k * 0.32, ph=rng.uniform(0, 6.28), sp=rng.uniform(0.6, 1.0)))
bubbles = [dict(x=rng.uniform(0, W), y=rng.uniform(0, H), r=rng.uniform(3, 9), v=rng.uniform(40, 110)) for _ in range(40)]
proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                         "-i", "-", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
def ease(u): u = min(1, max(0, u)); return 1 - (1 - u) ** 3 * (1 - 2.2 * u * (1 - u))  # slight overshoot
for f in range(int(DUR * FPS)):
    t = f / FPS
    im = bg.copy(); d = ImageDraw.Draw(im, "RGBA")
    for b in bubbles:
        y = (b["y"] - b["v"] * t) % (H + 40) - 20
        d.ellipse([b["x"] - b["r"], y - b["r"], b["x"] + b["r"], y + b["r"]], outline=(255, 255, 255, 90), width=2)
    for p in P:
        s = ease((t - p["t0"]) / 0.45)
        if s <= 0: continue
        x = p["x"] + 14 * math.sin(p["sp"] * t + p["ph"]); y = p["y"] + 12 * math.cos(0.8 * p["sp"] * t + p["ph"])
        r = p["r"] * s
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse([x - r * 1.25, y - r * 1.25, x + r * 1.25, y + r * 1.25], fill=p["col"] + (70,))
        im.paste(glow.filter(ImageFilter.GaussianBlur(18)), (0, 0), glow.filter(ImageFilter.GaussianBlur(18)))
        d = ImageDraw.Draw(im, "RGBA")
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 235), outline=p["col"] + (255,), width=max(1, int(9 * s)))
        if s > 0.5:
            fnt = fb(int(54 * s if len(p["name"]) < 5 else 46 * s))
            w = d.textlength(p["name"], font=fnt)
            d.text((x - w / 2, y - 32 * s), p["name"], font=fnt, fill=NAVY)
    # legend
    d.rounded_rectangle([40, 40, 470, 112], 36, fill=(255, 255, 255, 235))
    d.ellipse([62, 58, 98, 94], fill=METAL); d.text((114, 52), "Og'ir metallar", font=fs(40), fill=NAVY)
    d.rounded_rectangle([500, 40, 770, 112], 36, fill=(255, 255, 255, 235))
    d.ellipse([522, 58, 558, 94], fill=SALT); d.text((574, 52), "Tuzlar", font=fs(40), fill=NAVY)
    proc.stdin.write(im.tobytes())
proc.stdin.close(); proc.wait()
