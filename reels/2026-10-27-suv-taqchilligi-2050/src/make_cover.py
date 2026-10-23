"""Cover for the 2050 reel: real dry-riverbed frame, Javohir cut-out (bust) with a soft brand-blue rim glow,
big hook text in the same 'timeline documentary' look as the reel."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np
D = "/home/claude/r3/cover/"
F = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
fn = lambda w, s: ImageFont.truetype(F.format(w), s)
W, H = 1080, 1920
WHITE, SKY, WARN = (255, 255, 255), (132, 210, 253), (255, 140, 110)

bg = Image.open(D + "bg.png").convert("RGB")
s = max(W / bg.width, H / bg.height); bg = bg.resize((int(bg.width * s), int(bg.height * s)), Image.LANCZOS)
bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
bg = ImageEnhance.Color(bg).enhance(0.85); bg = ImageEnhance.Contrast(bg).enhance(1.08)
im = bg.convert("RGBA")
# top gradient for the text, bottom vignette under the person
g = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(g)
for y in range(H):
    a = 190 * max(0, 1 - y / 1100) ** 1.1 + 120 * max(0, (y - 1300) / 620) ** 1.5
    d.line([(0, y), (W, y)], fill=(5, 15, 25, int(a)))
im.alpha_composite(g)

# person bust
cut = Image.open(D + "cut.png").convert("RGBA").crop((400, 790, 1000, 1330))
sc = 1.8; cut = cut.resize((int(cut.width * sc), int(cut.height * sc)), Image.LANCZOS)
m = np.array(cut.getchannel("A")).astype(np.float32)
fade = np.clip((cut.height - np.arange(cut.height)) / 160, 0, 1)[:, None]      # soft bottom edge
cut.putalpha(Image.fromarray((m * fade).astype(np.uint8)))
px, py = (W - cut.width) // 2, H - cut.height + 10
glow = Image.new("RGBA", (W, H)); gl = Image.new("RGBA", cut.size, SKY + (0,)); gl.putalpha(cut.getchannel("A"))
glow.alpha_composite(gl, (px, py)); glow = glow.filter(ImageFilter.GaussianBlur(26))
glow.putalpha(glow.getchannel("A").point(lambda v: int(v * 0.85)))
im.alpha_composite(glow); im.alpha_composite(cut, (px, py))

d = ImageDraw.Draw(im)
def text(x, y, s, f, col, anchor="la"):
    d.text((x + 4, y + 5), s, font=f, fill=(0, 0, 0, 150), anchor=anchor)
    d.text((x, y), s, font=f, fill=col + (255,), anchor=anchor)
# HUD like in the reel
d.text((80, 150), "SUV TAQCHILLIGI · 2050", font=fn("Bold", 34), fill=WHITE + (235,))
d.line([(80, 206), (1000, 206)], fill=(255, 255, 255, 100), width=5)
d.line([(80, 206), (1000, 206)], fill=SKY + (255,), width=5)
d.ellipse([990, 197, 1008, 215], fill=SKY + (255,))
text(68, 250, "2050", fn("Black", 300), WHITE)
text(80, 585, "suv taqchilligi", fn("ExtraBold", 92), WHITE)
# ×5 badge
f = fn("Black", 120); w = d.textlength("5 barobar?!", font=f)
d.rounded_rectangle([70, 700, 70 + w + 60, 860], 24, fill=SKY + (255,))
d.text((100, 712), "5 barobar?!", font=f, fill=(11, 31, 51))
d.text((80, 885), "Jahon banki prognozi", font=fn("SemiBold", 40), fill=(230, 238, 245, 240))
im.convert("RGB").save(D + "cover_2050.jpg", quality=93)
im.convert("RGB").resize((360, 640)).save(D + "cover_small.jpg")
# 3:4 grid-crop preview (what the profile grid shows)
im.convert("RGB").crop((0, 240, 1080, 1680)).resize((300, 400)).save(D + "cover_grid.jpg")
print("ok")
