"""Procedural steam: writes an 8-bit alpha mask video (gray) at 1080x1920 to stdout-ffmpeg.
usage: steam.py out.mkv duration fade_in_start
Emitter = rim of the pot (full-screen coords x 180-420, y 1245)."""
import sys, subprocess, numpy as np
from scipy.ndimage import gaussian_filter

out, dur, t_on, t_off = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
W, H, FPS = 1080, 1920, 30
S = 4                      # render at 1/4 res, upscale (steam is soft anyway)
w, h = W // S, H // S
rng = np.random.default_rng(7)
X0, X1, Y0 = 215, 385, 1236
def fbm(hh, ww, seed):
    r = np.random.default_rng(seed); n = np.zeros((hh, ww), np.float32)
    for sc, wt in ((10, .5), (5, .3), (2.5, .2)):
        n += wt * gaussian_filter(r.standard_normal((hh, ww)).astype(np.float32), (sc * 1.8, sc * 0.8), mode='wrap')
    n = (n - n.mean()) / n.std(); return n
NZ = fbm(h * 2, w, 3)
yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)

parts = []   # [birth, x, y, vx, vy, life, phase, size0]
proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray",
                         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "ffv1", out],
                        stdin=subprocess.PIPE)
N = int(dur * FPS)
pre = 2.0  # pre-roll so steam is already established when it fades in? no: we want it to *start* rising
PRE = int(max(0, -t_on) * FPS)
for f in range(-PRE, N):
    t = f / FPS
    if t_on <= t <= t_off:
        k = min(1.0, (t - t_on) / 0.8)          # emission ramps up
        for _ in range(rng.poisson(4 * k)):
            parts.append([t, rng.uniform(X0, X1), Y0 + rng.uniform(-4, 8),
                          rng.normal(0, 10), -rng.uniform(70, 120),
                          rng.uniform(2.6, 3.8), rng.uniform(0, 6.28), rng.uniform(28, 40)])
    canvas = np.zeros((h, w), np.float32)
    alive = []
    for p in parts:
        a = t - p[0]
        if a > p[5]:
            continue
        alive.append(p)
        u = a / p[5]
        x = p[1] + p[3] * a + 28 * np.sin(1.6 * a + p[6]) * u + 40 * u * u * np.sin(p[6])
        y = p[2] + p[4] * a * (1 - 0.25 * u)
        sig = (p[7] * 0.7 + 60 * u) / S
        amp = 0.04 * min(1, u / 0.015) * (1 - u) ** 1.6
        cx, cy = x / S, y / S
        r = int(3 * sig) + 1
        x0, x1 = max(0, int(cx) - r), min(w, int(cx) + r)
        y0, y1 = max(0, int(cy) - r), min(h, int(cy) + r)
        if x0 >= x1 or y0 >= y1:
            continue
        g = np.exp(-(((xx[y0:y1, x0:x1] - cx) ** 2) + ((yy[y0:y1, x0:x1] - cy) ** 2) * 0.8) / (2 * sig * sig))
        canvas[y0:y1, x0:x1] += amp * g
    parts = alive
    canvas = gaussian_filter(canvas, 1.5)
    off = int(t * 40 / S) % (h * 2)
    nz = np.roll(NZ, -off, axis=0)[:h]
    canvas *= np.clip(0.85 + 0.25 * nz, 0.4, 2) * (1 + 2.5 * np.exp(-np.clip(Y0 / S - yy, 0, None) / 20))
    canvas = 0.42 * (1 - np.exp(-canvas * 2.5))           # soft saturation
    # don't draw steam inside/below the rim (pot body)
    cut = int((Y0 + 4) / S); canvas[cut:, :] = 0
    if f < 0:
        continue
    big = np.kron(canvas, np.ones((S, S), np.float32))
    big = gaussian_filter(big, 5)
    proc.stdin.write((np.clip(big, 0, 1) * 255).astype(np.uint8).tobytes())
proc.stdin.close(); proc.wait()
