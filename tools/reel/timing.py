"""Word timings for the narration, from measured pauses + syllable weighting.
Writes data.js with WORDS and CHUNKS for the renderer."""
import json, re

# (start, end, spoken text) — phrase boundaries measured with ffmpeg silencedetect
PHRASES = [
    (1.16, 4.12, "Har safar kranni ochganingizda xlor hidini sezganmisiz?"),
    (4.34, 5.57, "Bu yomon belgi emas,"),
    (5.69, 8.50, "aslida u suvni yoʻlda «qoʻriqlab kelayotgan himoyachi» xolos."),
    (9.51, 14.72, "«Biologik tozalashdan keyin ham suvda juda mayda zarrachalar qoladi» deb oldingi videoda aytilgandi."),
    (15.30, 18.43, "Ular bu jarayondan soʻng ham, choʻkmasdan suzib yuraveradi."),
    (18.90, 22.46, "Shunda suvga alyuminiy yoki temir tuzi qoʻshiladi va aralashtiradi."),
    (22.97, 24.97, "Bu holatda zarrachalar bir-biriga yopishib"),
    (25.36, 28.71, "(yaʼni flokulyatsiya orqali), kattalashadi va suv tubga choʻkadi."),
    (29.39, 31.02, "Buni koagulyatsiya deb atashadi."),
    (31.39, 31.91, "Oxirida"),
    (32.35, 36.03, "xlor qolgan mikroblar bilan kurashib, ularni yoʻq qiladi."),
    (36.76, 38.67, "Bu kabi tozalashning minusi ham bor:"),
    (39.07, 40.86, "kimyoviy reagentlar ancha qimmat"),
    (41.58, 43.62, "va koʻp chiqindi loyqa chiqaradi."),
    (44.00, 47.35, "Ushbu holatni faqatgina membranalar orqali daf qilish mumkin."),
    (47.68, 49.68, "Keyingi qism aynan shu haqida boʻladi."),
]

VOW = re.compile(r"[aeiouAEIOU]")

def weight(w):
    core = re.sub(r"[^\wʻʼ'-]", "", w)
    return max(1, len(VOW.findall(core))) + 0.35 * len(core) / 4

words = []
for pi, (s, e, text) in enumerate(PHRASES):
    toks = text.split()
    ws = [weight(t) for t in toks]
    tot = sum(ws); t = s
    for tok, wt in zip(toks, ws):
        d = (e - s) * wt / tot
        words.append({"w": re.sub(r"[«»()]", "", tok), "s": round(t, 3), "e": round(t + d, 3), "p": pi})
        t += d

# chunks: max 3 words, max ~20 chars, never across phrases or after punctuation
chunks, cur = [], []
def flush():
    if cur:
        chunks.append({"i0": cur[0], "i1": cur[-1]})
        cur.clear()
for i, w in enumerate(words):
    if cur and (words[cur[0]]["p"] != w["p"] or len(cur) >= 3 or
                sum(len(words[j]["w"]) + 1 for j in cur) + len(w["w"]) > 20):
        flush()
    cur.append(i)
    if re.search(r"[,.?:!)]$", w["w"]) or w["w"].endswith("»"):
        flush()
flush()
for c in chunks:
    c["s"] = words[c["i0"]]["s"]
for k, c in enumerate(chunks):
    nxt = chunks[k + 1]["s"] if k + 1 < len(chunks) else 99
    c["e"] = min(nxt, words[c["i1"]]["e"] + 0.45)
# strip trailing punctuation for display except ? ! kept off too (part 2 style keeps final "." on last chunk)
for w in words:
    w["d"] = w["w"].rstrip(",:")
open("data.js", "w", encoding="utf-8").write(
    "const WORDS=" + json.dumps(words, ensure_ascii=False) + ";\nconst CHUNKS=" + json.dumps(chunks) + ";\n")
for c in chunks:
    print(f'{c["s"]:6.2f}-{c["e"]:6.2f}  ' + " ".join(words[j]["d"] for j in range(c["i0"], c["i1"] + 1)))
