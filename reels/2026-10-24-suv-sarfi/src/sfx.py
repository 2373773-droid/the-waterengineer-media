"""Transition SFX: whoosh (whip), riser-swoosh (zoom), impact+shimmer (flash). usage: sfx(events, dur) -> stereo float array"""
import numpy as np
from scipy.signal import butter, sosfilt
SR = 48000
rng = np.random.default_rng(9)
def _bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], 'bp', fs=SR, output='sos'), x)
def whoosh(d=0.45, up=False):
    n = int(SR * d); t = np.arange(n) / SR; x = rng.standard_normal(n)
    env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
    out = np.zeros(n); blk = 512
    for i in range(0, n, blk):                       # sweeping band-pass
        u = i / n; fc = (300 + 3500 * u) if up else (3800 - 3000 * abs(u - 0.5) * 2)
        out[i:i + blk] = _bp(x[i:i + blk], max(80, fc * 0.5), min(20000, fc * 1.6))
    return out * env * 0.9
def impact(d=0.6):
    n = int(SR * d); t = np.arange(n) / SR
    thump = np.sin(2 * np.pi * (60 + 80 * np.exp(-t * 25)) * t) * np.exp(-t * 9)
    sh = _bp(rng.standard_normal(n), 4000, 12000) * np.exp(-t * 7) * 0.35
    return thump * 0.9 + sh
def render(events, dur):
    out = np.zeros((2, int(SR * dur)))
    for t0, kind in events:
        s = {"whip": whoosh(0.42), "zoom": whoosh(0.5, up=True), "flash": impact()}[kind]
        i = int(SR * max(0, t0 - (0.21 if kind != "flash" else 0.02)))
        s = s[: out.shape[1] - i]
        pan = 0.25 if kind == "whip" else 0
        out[0, i:i + len(s)] += s * (1 - pan); out[1, i:i + len(s)] += s * (1 + pan)
    return out / max(1e-6, np.abs(out).max()) * 0.5
