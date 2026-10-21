"""Shared timeline: which parts of the raw take are kept, and orig->new time mapping."""
START, END = 1.60, 65.85
# pauses (orig seconds) longer than 0.4 s, from silencedetect -32 dB
GAPS = [(5.69, 6.55), (9.07, 10.06), (12.96, 13.94), (22.03, 22.60), (27.13, 27.60),
        (29.28, 30.23), (31.60, 32.87), (35.46, 35.98), (41.59, 42.43), (48.43, 48.98),
        (51.58, 52.23), (56.94, 57.43)]
# 3.60-4.22 is kept whole on purpose: the B&W hook needs a little time for the steam
PAD_OUT, PAD_IN = 0.14, 0.10

def keep_segments():
    segs, a = [], START
    for s, e in GAPS:
        segs.append((a, s + PAD_OUT)); a = e - PAD_IN
    segs.append((a, END))
    return segs

SEGS = keep_segments()

def new(t):
    acc = 0.0
    for a, b in SEGS:
        if t < a:
            return acc
        if t <= b:
            return acc + t - a
        acc += b - a
    return acc

TOTAL = new(END)
# Javohir's section points (orig, seconds:frames @30fps): 03:29 17:03 27:18 32:26 45:29 54:21
CUTS_ORIG = [3 + 29/30, 17 + 3/30, 27 + 18/30, 32 + 26/30, 45 + 29/30, 54 + 21/30]
CUTS = [new(t) for t in CUTS_ORIG]

if __name__ == "__main__":
    print(SEGS); print("total", round(TOTAL, 2)); print("cuts", [round(c, 2) for c in CUTS])
