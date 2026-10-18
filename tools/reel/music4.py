"""Part 4 bed: warm, hopeful pluck arpeggio (kalimba-like) over a soft pad. Generated from scratch. Writes music.wav."""
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR, DUR = 48000, 77.3
N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(11)
hz = lambda n: 440.0 * 2 ** ((n - 69) / 12)

BPM = 92
beat = 60 / BPM
bar = beat * 4
# D major, uplifting: Dmaj9 – Bm7 – Gmaj7 – A(add9)   (one bar each, 2 bars per chord)
CH = [[50, 57, 61, 64, 66], [47, 54, 57, 62, 66], [43, 50, 54, 59, 62], [45, 52, 57, 59, 64]]
out = np.zeros((2, N))

# soft pad
for i in range(int(DUR / (2 * bar)) + 2):
    s = i * 2 * bar - 0.6
    env = np.clip((t - s) / 1.6, 0, 1) * np.clip((s + 2 * bar + 1.4 - t) / 1.6, 0, 1)
    env = np.sin(env * np.pi / 2) ** 2
    if env.max() == 0: continue
    for j, n in enumerate(CH[i % 4][:4]):
        for side, det in ((0, -1.1), (1, 1.1)):
            f = hz(n) + det; ph = rng.uniform(0, 6.28)
            out[side] += (np.sin(2 * np.pi * f * t + ph) + 0.25 * np.sin(4 * np.pi * f * t + ph)) * env * (0.5 if j == 0 else 0.28)

# kalimba-like plucks: 8th-note arpeggio, one octave up
def pluck(f, start, amp, pan):
    i0 = int(start * SR); L = int(1.6 * SR)
    if i0 >= N: return
    L = min(L, N - i0); tt = np.arange(L) / SR
    env = np.exp(-tt * 4.2) * np.clip(tt / 0.004, 0, 1)
    sig = (np.sin(2 * np.pi * f * tt) + 0.45 * np.sin(2 * np.pi * f * 2.0 * tt) * np.exp(-tt * 9)
           + 0.2 * np.sin(2 * np.pi * f * 5.4 * tt) * np.exp(-tt * 22)) * env * amp
    out[0, i0:i0 + L] += sig * (1 - pan); out[1, i0:i0 + L] += sig * pan

pattern = [0, 2, 4, 3, 1, 3, 4, 2]
start_plucks = 2 * bar  # pad alone for the first 2 bars
k = 0; tcur = start_plucks
while tcur < DUR - 1.5:
    ci = int(tcur // (2 * bar)) % 4
    n = CH[ci][pattern[k % 8]] + 12
    pluck(hz(n), tcur + rng.normal(0, 0.006), 0.42 * (1.0 if k % 2 == 0 else 0.75), 0.35 + 0.3 * ((k * 3) % 5) / 4)
    k += 1; tcur += beat / 2

# gentle bass on each chord change
for i in range(int(DUR / (2 * bar)) + 1):
    s = i * 2 * bar
    if s > DUR - 1: break
    i0 = int(s * SR); L = min(int(2 * bar * SR), N - i0); tt = np.arange(L) / SR
    f = hz(CH[i % 4][0] - 12)
    b = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 0.9) * np.clip(tt / 0.02, 0, 1) * 0.55
    out[:, i0:i0 + L] += b

# light water-noise bed
noise = sosfilt(butter(2, [250, 1200], btype="band", fs=SR, output="sos"), rng.standard_normal((2, N)))
out += noise * 0.35 * (0.6 + 0.4 * np.sin(2 * np.pi * 0.06 * t))

out = sosfilt(butter(2, 5200, btype="low", fs=SR, output="sos"), out)
rev = np.zeros_like(out)
for d, g in ((0.029, .42), (0.047, .38), (0.083, .32), (0.131, .26), (0.197, .2), (0.29, .15)):
    kk = int(d * SR); rev[:, kk:] += out[:, :-kk] * g
out = out + rev * 0.55
out[1] = np.roll(out[1], int(0.011 * SR))

fade = np.clip(t / 1.2, 0, 1) * np.clip((DUR - t) / 2.0, 0, 1)
out *= fade
out /= np.max(np.abs(out)) + 1e-9
wavfile.write("music.wav", SR, (out.T * 0.9 * 32767).astype(np.int16))
print("ok")
