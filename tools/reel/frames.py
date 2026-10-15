"""Render frames of reel.html. Usage:
  python3 frames.py stills 0.5 5 12 ...   -> stills/t_<t>.png + sheet.png
  python3 frames.py video out.mp4         -> silent 30fps video piped to ffmpeg
"""
import sys, subprocess, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).parent.resolve()
END, FPS = 51.3, 30

def page_ctx(pw):
    b = pw.chromium.launch(args=["--allow-file-access-from-files"])
    pg = b.new_page(viewport={"width": 1080, "height": 1920})
    pg.goto(f"file://{ROOT}/reel.html")
    pg.evaluate("window.ready")
    errs = []
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append(str(e)))
    return b, pg, errs

mode = sys.argv[1]
with sync_playwright() as pw:
    b, pg, errs = page_ctx(pw)
    if mode == "stills":
        out = ROOT / "stills"; out.mkdir(exist_ok=True)
        ts = [float(x) for x in sys.argv[2:]]
        for t in ts:
            pg.evaluate(f"render({t})")
            pg.locator("canvas").screenshot(path=str(out / f"t_{t:05.2f}.png"))
        from PIL import Image
        ims = [Image.open(out / f"t_{t:05.2f}.png").resize((270, 480)) for t in ts]
        cols = 5; rows = (len(ims) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * 280 + 10, rows * 490 + 10), "white")
        for i, im in enumerate(ims):
            sheet.paste(im, (10 + (i % cols) * 280, 10 + (i // cols) * 490))
        sheet.save(ROOT / "sheet.png")
    else:
        n = int(END * FPS)
        ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                               "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", sys.argv[2]], stdin=subprocess.PIPE)
        for i in range(n):
            pg.evaluate(f"render({i / FPS})")
            ff.stdin.write(pg.screenshot(type="jpeg", quality=93))
            if i % 150 == 0: print("frame", i, "/", n, flush=True)
        ff.stdin.close(); ff.wait()
    print("errors:", errs[:5])
    b.close()
