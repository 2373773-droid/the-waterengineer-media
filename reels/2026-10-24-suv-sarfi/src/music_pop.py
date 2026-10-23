"""Upbeat, modern bed (118 BPM): four-on-the-floor soft kick, off-beat hats, claps, side-chained chord stabs,
plucked arpeggio, sub bass. Generated from scratch (no samples, no licence issues). usage: music_pop.py seconds out.wav"""
import sys, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
SR = 48000; DUR = float(sys.argv[1]); OUT = sys.argv[2]
BPM = 118; b = 60 / BPM; n = int(SR * DUR)
L = np.zeros(n); R = np.zeros(n); rng = np.random.default_rng(21)
def m(k): return 440 * 2 ** ((k - 69) / 12)
def put(sig, t, g=1.0, pan=0.0):
    i = int(t * SR)
    if i >= n: return
    s = sig[: n - i] * g; L[i:i + len(s)] += s * (1 - pan); R[i:i + len(s)] += s * (1 + pan)
def env(d, a=0.005, r=6.0):
    t = np.arange(int(SR * d)) / SR; return np.minimum(1, t / a) * np.exp(-t * r), t
def kick():
    e, t = env(0.32, 0.001, 11); return np.sin(2 * np.pi * np.cumsum(48 + 110 * np.exp(-t * 32)) / SR) * e
def hat(open_=False):
    e, t = env(0.18 if open_ else 0.05, 0.001, 18 if open_ else 70)
    return sosfilt(butter(4, 8000, 'hp', fs=SR, output='sos'), rng.standard_normal(len(t))) * e
def clap():
    e, t = env(0.22, 0.002, 16); x = sosfilt(butter(2, [900, 3500], 'bp', fs=SR, output='sos'), rng.standard_normal(len(t)))
    for d in (0.0, 0.011, 0.022): x[int(d * SR):] += x[: len(x) - int(d * SR)] * 0.4
    return x * e
def saw_chord(notes, d):
    e, t = env(d, 0.01, 3.2); s = sum(2 * ((t * m(k) * (1 + dt)) % 1) - 1 for k in notes for dt in (-0.004, 0.004))
    return sosfilt(butter(2, 2200, 'lp', fs=SR, output='sos'), s) * e / len(notes)
def pluck(k, d=0.25):
    e, t = env(d, 0.002, 14); return (np.sin(2 * np.pi * m(k) * t) + 0.4 * np.sin(4 * np.pi * m(k) * t)) * e
def sub(k, d):
    e, t = env(d, 0.01, 2.5); return np.sin(2 * np.pi * m(k) * t) * e
PROG = [([57, 60, 64, 67], 45), ([53, 57, 60, 64], 41), ([48, 52, 55, 59], 36), ([55, 59, 62, 66], 43)]  # Am9 Fmaj7 Cmaj7 G
ARP = [0, 2, 1, 3, 2, 1, 3, 2]
bars = int(DUR / (4 * b)) + 1
for bar in range(bars):
    t0 = bar * 4 * b; ch, bs = PROG[bar % 4]; intro = bar < 1
    for q in range(4):
        tq = t0 + q * b
        if not intro: put(kick(), tq, 0.55)
        put(hat(True), tq + b / 2, 0.07, -0.3)
        put(hat(), tq + b / 4, 0.035, 0.3); put(hat(), tq + 3 * b / 4, 0.035, 0.3)
        if q in (1, 3) and not intro: put(clap(), tq, 0.22, 0.1)
        put(saw_chord(ch, b * 0.45), tq + b / 2, 0.16)               # off-beat stabs (pump feel)
        put(sub(bs, b * 0.9), tq, 0.30 if not intro else 0)
    for s8 in range(8):
        put(pluck(ch[ARP[s8]] + 12, 0.22), t0 + s8 * b / 2 + b / 4, 0.07, 0.35 if s8 % 2 else -0.35)
out = np.stack([L, R])
out = np.tanh(out * 1.3)
t = np.arange(n) / SR; out *= np.clip(t / 0.4, 0, 1) * np.clip((DUR - t) / 1.5, 0, 1)
out /= np.abs(out).max() * 1.1
wavfile.write(OUT, SR, (out.T * 32767).astype(np.int16)); print("ok")
