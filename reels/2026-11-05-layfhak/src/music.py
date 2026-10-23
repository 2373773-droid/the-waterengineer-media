"""'Process' bed (100 BPM, A minor → C major at the solution): a 16th-note sequencer arpeggio whose filter slowly
opens, with layers entering on the reel's chapter marks (bass, soft kick, pad, hats), peak at the deficit/well
chapters, resolving at 'Yechim' and thinning out for the CTA. Generated from scratch. usage: music_process.py out.wav"""
import sys, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
SR = 48000; DUR = 57.0; n = int(SR * DUR); b = 60 / 112; s16 = b / 4
L = np.zeros(n); R = np.zeros(n); rng = np.random.default_rng(12)
MARK = dict(lines=5.5, gap=13.0, percap=20.5, glacier=29.0, well=36.0, fix=50.0, cta=50.0)
def m(k): return 440 * 2 ** ((k - 69) / 12)
def put(s, t, g, pan=0.0):
    i = int(t * SR)
    if i < 0: s = s[-i:]; i = 0
    if i >= n: return
    s = s[: n - i] * g; L[i:i + len(s)] += s * (1 - pan); R[i:i + len(s)] += s * (1 + pan)
def env(d, a=0.003, r=8):
    t = np.arange(int(SR * d)) / SR; return np.minimum(1, t / a) * np.exp(-t * r), t
def lp(x, f): return sosfilt(butter(2, max(80, min(f, 16000)), 'lp', fs=SR, output='sos'), x)
def arp_note(k, t0):
    e, t = env(s16 * 1.6, 0.002, 11)
    x = 2 * ((t * m(k)) % 1) - 1 + 0.5 * (2 * ((t * m(k) * 1.005) % 1) - 1)
    cut = 500 + 4500 * (t0 / DUR) ** 1.3                      # the 'process': filter opens over the whole reel
    return lp(x, cut) * e
def bass(k, d):
    e, t = env(d, 0.01, 2.2); return (np.sin(2 * np.pi * m(k) * t) + 0.3 * np.sin(4 * np.pi * m(k) * t)) * e
def kick():
    e, t = env(0.3, 0.001, 12); return np.sin(2 * np.pi * np.cumsum(46 + 90 * np.exp(-t * 30)) / SR) * e
def hat():
    e, t = env(0.04, 0.001, 90); return sosfilt(butter(4, 7500, 'hp', fs=SR, output='sos'), rng.standard_normal(len(t))) * e
def pad(notes, d):
    t = np.arange(int(SR * d)) / SR; e = np.minimum(1, t / 1.0) * np.minimum(1, (d - t) / 1.0)
    return lp(sum(2 * ((t * m(k) * (1 + dt)) % 1) - 1 for k in notes for dt in (-0.004, 0.004)), 1100) * e / (2 * len(notes))
MINOR = [([57, 60, 64, 69], 45), ([53, 57, 60, 65], 41), ([55, 59, 62, 67], 43), ([52, 56, 59, 64], 40)]   # Am F G E
MAJOR = [([60, 64, 67, 72], 48), ([55, 59, 62, 67], 43), ([57, 60, 64, 69], 45), ([53, 57, 60, 65], 41)]   # C G Am F
PAT = [0, 1, 2, 3, 2, 1, 2, 3, 0, 2, 1, 3, 2, 3, 1, 2]
bar = 4 * b
for bi in range(int(DUR / bar) + 1):
    t0 = bi * bar
    prog = MAJOR
    ch, bs = prog[bi % 4]
    lvl = 0.10 + 0.10 * min(1, t0 / MARK["well"])             # arp grows louder until the peak
    if t0 >= MARK["cta"]: lvl *= 0.7
    for k16 in range(16):
        put(arp_note(ch[PAT[k16]] + 12, t0), t0 + k16 * s16, lvl, 0.35 if k16 % 2 else -0.35)
    if t0 >= MARK["lines"] - 0.1: put(bass(bs, bar), t0, 0.28)
    if MARK["gap"] - 0.1 <= t0 < MARK["cta"]:
        for q in range(4): put(kick(), t0 + q * b, 0.45 if t0 < MARK["fix"] else 0.35)
    if t0 >= MARK["percap"] - 0.1: put(pad(ch, bar + 0.6), t0 - 0.2, 0.42)
    if MARK["glacier"] - 0.1 <= t0 < MARK["cta"]:
        for e8 in range(8): put(hat(), t0 + e8 * b / 2 + b / 4, 0.05, 0.2)
# soft riser into the solution
rt = np.arange(int(SR * 2.5)) / SR
riser = sosfilt(butter(2, [400, 6000], 'bp', fs=SR, output='sos'), rng.standard_normal(len(rt))) * (rt / 2.5) ** 2
put(riser, MARK["fix"] - 2.5, 0.12)
out = np.stack([L, R]); out = np.tanh(out * 1.5)
t = np.arange(n) / SR; out *= np.clip(t / 0.8, 0, 1) * np.clip((DUR - t) / 2.0, 0, 1)
out /= np.abs(out).max() * 1.12
wavfile.write(sys.argv[1], SR, (out.T * 32767).astype(np.int16)); print("ok")
