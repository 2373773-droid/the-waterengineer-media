"""Soft ambient 'underwater' pad, generated from scratch (no samples). Writes music.wav."""
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR, DUR = 48000, 77.3
t = np.arange(int(SR * DUR)) / SR
rng = np.random.default_rng(3)

def note(n):  # MIDI -> Hz
    return 440.0 * 2 ** ((n - 69) / 12)

# A minor-ish dreamy progression: Am9, Fmaj7, Cmaj7, G6 (6.4 s each, loops)
CH = [[45, 52, 59, 60, 67], [41, 48, 52, 57, 64], [48, 55, 59, 64, 71], [43, 50, 52, 59, 62]]
seg = 6.4
out = np.zeros((2, t.size))
for i in range(int(DUR / seg) + 2):
    start = i * seg - 1.2
    env = np.clip((t - start) / 2.2, 0, 1) * np.clip((start + seg + 2.4 - t) / 2.2, 0, 1)
    env = np.sin(env * np.pi / 2) ** 2
    if env.max() == 0: continue
    for j, n in enumerate(CH[i % 4]):
        f = note(n)
        for side, det in ((0, -0.9), (1, 0.9)):
            ph = rng.uniform(0, 6.28)
            tone = (np.sin(2 * np.pi * (f + det) * t + ph) + 0.35 * np.sin(2 * np.pi * 2 * (f + det) * t + ph)
                    + 0.12 * np.sin(2 * np.pi * 3 * (f + det) * t))
            trem = 0.85 + 0.15 * np.sin(2 * np.pi * (0.11 + 0.03 * j) * t + ph)
            out[side] += tone * env * trem * (0.9 if j == 0 else 0.55)

# filtered noise "water" bed
noise = rng.standard_normal((2, t.size))
sos = butter(2, [180, 900], btype="band", fs=SR, output="sos")
water = sosfilt(sos, noise) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t))
out += water * 0.9

# gentle low-pass and simple reverb
sos = butter(2, 2200, btype="low", fs=SR, output="sos")
out = sosfilt(sos, out)
rev = np.zeros_like(out)
for d, g in ((0.037, .45), (0.053, .4), (0.071, .35), (0.113, .3), (0.167, .25), (0.241, .2)):
    k = int(d * SR); rev[:, k:] += out[:, :-k] * g
out = out + rev * 0.6

# fades
fade = np.clip(t / 1.5, 0, 1) * np.clip((DUR - t) / 1.8, 0, 1)
out *= fade
out /= np.max(np.abs(out)) + 1e-9
wavfile.write("music.wav", SR, (out.T * 0.9 * 32767).astype(np.int16))
print("ok", out.shape)
