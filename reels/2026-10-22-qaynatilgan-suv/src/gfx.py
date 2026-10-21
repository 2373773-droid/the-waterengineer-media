"""Static graphics: REC viewfinder overlay, top-panel chips, brand end card, cover."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
F = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
def font(w, s): return ImageFont.truetype(F.format(w), s)
NAVY, SKY, SKYL, ACC = (11, 31, 51), (132, 210, 253), (237, 248, 255), (31, 58, 128)

# --- REC viewfinder (1080x1920, transparent) ---
im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
m, L, w = 70, 110, 7
for (x, y, sx, sy) in [(m, m + 60, 1, 1), (1080 - m, m + 60, -1, 1), (m, 1920 - m - 260, 1, -1), (1080 - m, 1920 - m - 260, -1, -1)]:
    d.line([(x, y), (x + sx * L, y)], fill=(255, 255, 255, 235), width=w)
    d.line([(x, y), (x, y + sy * L)], fill=(255, 255, 255, 235), width=w)
d.text((m + 95, m + 92), "REC", font=font("Bold", 50), fill=(255, 255, 255, 240))
d.text((m + 30, 1920 - m - 330), "HD  30fps", font=font("SemiBold", 34), fill=(255, 255, 255, 220))
# battery
bx, by = 1080 - m - 120, m + 100
d.rounded_rectangle([bx, by, bx + 92, by + 42], 6, outline=(255, 255, 255, 235), width=5)
d.rectangle([bx + 92, by + 12, bx + 100, by + 30], fill=(255, 255, 255, 235))
for i in range(3): d.rectangle([bx + 10 + i * 26, by + 10, bx + 30 + i * 26, by + 32], fill=(255, 255, 255, 235))
# centre cross
cx, cy = 540, 820
d.line([(cx - 34, cy), (cx + 34, cy)], fill=(255, 255, 255, 170), width=4)
d.line([(cx, cy - 34), (cx, cy + 34)], fill=(255, 255, 255, 170), width=4)
im.save("g_rec.png")
dot = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
ImageDraw.Draw(dot).ellipse([m + 30, m + 100, m + 72, m + 142], fill=(235, 30, 40, 255))
dot.save("g_dot.png")

# --- top-panel chips (1080x900, transparent) ---
def chip(txt, fn, sub=None):
    im = Image.new("RGBA", (1080, 900), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f1 = font("ExtraBold", 50); f2 = font("SemiBold", 34)
    w1 = d.textlength(txt, font=f1); w2 = d.textlength(sub, font=f2) if sub else 0
    W = int(max(w1, w2)) + 70; H = 92 + (52 if sub else 0)
    x, y = 48, 900 - 48 - H
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([x + 4, y + 8, x + W + 4, y + H + 8], 26, fill=(0, 0, 0, 110))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(10))); d = ImageDraw.Draw(im)
    d.rounded_rectangle([x, y, x + W, y + H], 26, fill=SKY + (255,))
    d.text((x + 35, y + 18), txt, font=f1, fill=NAVY)
    if sub: d.text((x + 35, y + 84), sub, font=f2, fill=ACC)
    im.save(fn)
chip("Bug' chiqdi ≠ qaynadi", "g_c1.png")
chip("Biqir-biqir qaynash", "g_c2.png", "kamida 1 daqiqa")
chip("Tog'da (2 000 m dan baland)", "g_c3.png", "3 daqiqa qaynatish kerak")
chip("Kimyoviy moddalar", "g_c4.png", "qaynatganda yo'qolmaydi")
chip("Oq qatlam = Ca, Mg", "g_c5.png", "zararsiz minerallar")
chip("Og'ir metallar, tuzlar", "g_c6.png", "suvda qolaveradi")

# --- brand end card (1080x900) ---
im = Image.new("RGB", (1080, 900), SKY); d = ImageDraw.Draw(im)
def ctext(y, t, f, fill):
    d.text(((1080 - d.textlength(t, font=f)) / 2, y), t, font=f, fill=fill)
ctext(250, "Doktor H₂O", font("Black", 120), NAVY)
d.rounded_rectangle([250, 440, 830, 540], 50, fill=NAVY)
ctext(455, "@suvyektiv", font("ExtraBold", 66), (255, 255, 255))
ctext(590, "Instagram  ·  YouTube", font("SemiBold", 42), ACC)
ctext(720, "Qaysi faktni bilmoqchisiz? Kommentda yozing!", font("SemiBold", 38), NAVY)
im.save("g_brand.png")

# --- end badge: glass card with name + username (placed at x=160,y=250 on 1080x1920) ---
BW, BH = 760, 260
mask = Image.new("L", (BW, BH), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, BW - 1, BH - 1], 48, fill=255)
mask.save("g_badge_mask.png")
b = Image.new("RGBA", (BW, BH), (0, 0, 0, 0)); d = ImageDraw.Draw(b)
d.rounded_rectangle([0, 0, BW - 1, BH - 1], 48, fill=(11, 31, 51, 70), outline=(255, 255, 255, 170), width=3)
def bt(y, t, f):
    d.text(((BW - d.textlength(t, font=f)) / 2 + 2, y + 3), t, font=f, fill=(0, 0, 0, 90))
    d.text(((BW - d.textlength(t, font=f)) / 2, y), t, font=f, fill=(255, 255, 255, 255))
bt(38, "Doktor H₂O", font("Black", 92))
bt(158, "@suvyektiv", font("SemiBold", 58))
b.save("g_badge.png")
