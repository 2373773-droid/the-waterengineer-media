"""'Process' bed v2 (ticking-clock documentary): 120 BPM clock ticks, plucked piano ostinato (D minor), sub pulses,
sustained cello-like drone; tension builds through the case, a hit + lift to D major-ish at the solution. From scratch."""
import sys, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
SR = 48000; DUR = 66.0; n = int(SR * DUR); b = 60 / 104
L = np.zeros(n); R = np.zeros(n); rng = np.random.default_rng(7)
M = dict(plant=6.0, h2s=13.5, nose=22.5, turn=29.0, case=34.5, fix=51.0, verdict=55.0, cta=59.5)
f = lambda k: 440 * 2 ** ((k - 66) / 12)
def put(s, t, g, pan=0.0):
    i = int(t * SR)
    if i >= n: return
    s = s[: n - i] * g; L[i:i + len(s)] += s * (1 - pan); R[i:i + len(s)] += s * (1 + pan)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], 'bp', fs=SR, output='sos'), x)
def lp(x, c): return sosfilt(butter(2, c, 'lp', fs=SR, output='sos'), x)
def tick(hi=True):
    t = np.arange(int(SR * 0.05)) / SR; e = np.exp(-t * 160)
    return bp(rng.standard_normal(len(t)), 2500 if hi else 1500, 7000 if hi else 4000) * e
def piano(k, d=1.2):
    t = np.arange(int(SR * d)) / SR; x = 0
    for h, a in ((1, 1), (2, .45), (3, .22), (4, .12), (5, .06)):
        x = x + a * np.sin(2 * np.pi * f(k) * h * t * (1 + 0.0004 * h * h)) * np.exp(-t * (2.5 + 1.6 * h))
    return x * np.minimum(1, t / 0.003)
def sub(k, d):
    t = np.arange(int(SR * d)) / SR; return np.sin(2 * np.pi * f(k) * t) * np.exp(-t * 3) * np.minimum(1, t / 0.01)
def drone(k, d):
    t = np.arange(int(SR * d)) / SR
    x = sum(np.sin(2 * np.pi * f(k) * h * t + 0.3 * np.sin(2 * np.pi * 5 * t)) / h for h in range(1, 7))
    return lp(x, 900) * np.minimum(1, t / 1.5) * np.minimum(1, (d - t) / 1.5)
def hit():
    t = np.arange(int(SR * 2.5)) / SR
    return (np.sin(2 * np.pi * np.cumsum(38 + 60 * np.exp(-t * 18)) / SR) * np.exp(-t * 2.2)
            + 0.4 * lp(rng.standard_normal(len(t)), 1800) * np.exp(-t * 5))
MIN = [(50, [62, 65, 69, 72, 69, 65, 62, 65]), (46, [58, 62, 65, 70, 65, 62, 58, 62]),
       (43, [55, 58, 62, 67, 62, 58, 55, 58]), (45, [57, 61, 64, 69, 64, 61, 57, 61])]   # Dm Bb Gm A
MAJ = [(50, [62, 66, 69, 74, 69, 66, 62, 66]), (47, [59, 62, 66, 71, 66, 62, 59, 62]),
       (43, [55, 59, 62, 67, 62, 59, 55, 59]), (45, [57, 61, 64, 69, 64, 61, 57, 61])]   # D Bm G A
bar = 4 * b
for bi in range(int(DUR / bar) + 1):
    t0 = bi * bar; prog = MAJ if t0 >= M["fix"] - 0.01 else MIN; bs, arp = prog[bi % 4]
    tens = min(1, t0 / M["fix"])
    for q in range(8):                                     # ticks on 8ths, accent on beats
        put(tick(q % 2 == 0), t0 + q * b / 2, 0.10 if q % 2 == 0 else 0.05, 0.25)
    if t0 >= M["plant"] - 0.01:
        for q, k in enumerate(arp):                        # 8th-note piano ostinato
            put(piano(k + (12 if t0 >= M["case"] - 0.01 else 0)), t0 + q * b / 2, 0.13 + 0.06 * tens, -0.3 if q % 2 else 0.3)
    if t0 >= M["h2s"] - 0.01 and t0 < M["cta"]:
        for q in (0, 1.5, 2, 3.5): put(sub(bs - 12, 0.6), t0 + q * b, 0.5)
    if t0 >= M["nose"] - 0.01: put(drone(bs, bar + 1.2), t0 - 0.4, 0.09 + 0.05 * tens)
    if M["case"] - 0.01 <= t0 < M["fix"]:                 # double-time ticks = urgency
        for q in range(16): put(tick(False), t0 + q * b / 4 + b / 8, 0.035, -0.4)
# silence-then-hit into the turn and the solution
for k in (M["turn"], M["fix"]): put(hit(), k, 0.55)
rt = np.arange(int(SR * 3)) / SR
put(bp(rng.standard_normal(len(rt)), 300, 5000) * (rt / 3) ** 2.5, M["fix"] - 3, 0.12)
out = np.stack([L, R]); out = np.tanh(out * 1.6)
t = np.arange(n) / SR; out *= np.clip(t / 0.3, 0, 1) * np.clip((DUR - t) / 2.5, 0, 1)
out /= np.abs(out).max() * 1.12
wavfile.write(sys.argv[1], SR, (out.T * 32767).astype(np.int16)); print("ok")
