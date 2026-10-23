"""Serious cinematic documentary bed (84 BPM, D minor): string pad, low pulse, sparse piano motif, soft low hits.
Generated from scratch. usage: music_cine.py seconds out.wav"""
import sys, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
SR = 48000; DUR = float(sys.argv[1]); n = int(SR * DUR); b = 60 / 90
L = np.zeros(n); R = np.zeros(n); rng = np.random.default_rng(4)
def m(k): return 440 * 2 ** ((k - 69) / 12)
def put(s, t, g, pan=0.0):
    i = int(t * SR)
    if i < 0: s = s[-i:]; i = 0
    if i >= n: return
    s = s[: n - i] * g; L[i:i + len(s)] += s * (1 - pan); R[i:i + len(s)] += s * (1 + pan)
def lp(x, f): return sosfilt(butter(2, f, 'lp', fs=SR, output='sos'), x)
def pad(notes, d):
    t = np.arange(int(SR * d)) / SR; e = np.minimum(1, t / 1.2) * np.minimum(1, (d - t) / 1.2)
    s = sum(2 * ((t * m(k) * (1 + dt)) % 1) - 1 for k in notes for dt in (-0.003, 0, 0.003))
    return lp(s, 900) * e / (3 * len(notes))
def pulse(k, d):
    t = np.arange(int(SR * d)) / SR; e = np.minimum(1, t / 0.005) * np.exp(-t * 9)
    return lp(2 * ((t * m(k)) % 1) - 1, 500) * e
def piano(k, d=2.5):
    t = np.arange(int(SR * d)) / SR; e = np.minimum(1, t / 0.004) * np.exp(-t * 1.6)
    return (np.sin(2 * np.pi * m(k) * t) + 0.35 * np.sin(4 * np.pi * m(k) * t) * np.exp(-t * 3) + 0.12 * np.sin(6 * np.pi * m(k) * t) * np.exp(-t * 5)) * e
def hit():
    t = np.arange(int(SR * 1.2)) / SR
    return (np.sin(2 * np.pi * (45 + 40 * np.exp(-t * 18)) * t) * np.exp(-t * 4) + lp(rng.standard_normal(len(t)), 300) * np.exp(-t * 10) * 0.3)
PROG = [([52, 59, 64, 67], 40), ([48, 55, 60, 64], 36), ([50, 57, 62, 66], 38), ([47, 54, 59, 63], 35)]   # Em C D B
MOT = [76, 74, 71, 74, 76, 79, 78, 74]
bars = int(DUR / (4 * b)) + 1
for bar in range(bars):
    t0 = bar * 4 * b; ch, bs = PROG[bar % 4]
    put(pad(ch, 4 * b + 1.2), t0 - 0.3, 0.55)
    if bar >= 1:
        for e8 in range(8): put(pulse(bs, b / 2), t0 + e8 * b / 2, 0.22 if e8 % 2 == 0 else 0.14)
    if bar >= 2:
        for j in range(2): put(piano(MOT[(bar * 2 + j) % len(MOT)]), t0 + j * 2 * b, 0.12, 0.2 if j else -0.2)
    if bar >= 3 and bar % 2 == 1: put(hit(), t0, 0.45)
# clock tick on every beat (time running out)
def tick():
    tt = np.arange(int(SR * 0.04)) / SR
    return sosfilt(butter(2, [2500, 6000], 'bp', fs=SR, output='sos'), rng.standard_normal(len(tt))) * np.exp(-tt * 160)
for q in range(int(DUR / b) + 1): put(tick(), q * b, 0.12 if q % 2 == 0 else 0.07, 0.3 if q % 2 else -0.3)
out = np.stack([L, R]); out = np.tanh(out * 1.4)
t = np.arange(n) / SR; out *= np.clip(t / 1.5, 0, 1) * np.clip((DUR - t) / 2.0, 0, 1)
out /= np.abs(out).max() * 1.12
wavfile.write(sys.argv[2], SR, (out.T * 32767).astype(np.int16)); print("ok")
