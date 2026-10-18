"""Word timings for the narration, from measured pauses + syllable weighting.
Writes data.js with WORDS and CHUNKS for the renderer."""
import json, re

# (start, end, spoken text) — phrase boundaries measured with ffmpeg silencedetect
PHRASES = [
    (0.68, 2.83, "Uyingizda suv filtri bormi?"),
    (3.15, 8.85, "Uning ichida, ehtimol, sochingizdan oʻn minglab marta ingichka teshikli parda ishlayapti desam ishonaszmi?"),
    (9.14, 12.25, "Oldingi qismda aytilganidek eng murakkab zarrachalar"),
    (12.80, 18.13, "bilan membrana kurashadi, yaʼni juda mayda teshikli pardalar orqali ushlab qolinadi."),
    (18.53, 25.49, "Mikrofiltratsiya (MF) loyqa va bakteriyalarni toʻxtatadi. Ultrafiltratsiya (UF) undan ham mayda, hatto viruslarni ham ushlaydi."),
    (26.32, 30.86, "Teskari osmos (ya'ni Reverse Osmosis) esa suvdagi tuzni ham oʻtkazmaydi,"),
    (31.13, 33.36, "dengiz suvi aynan shunday chuchuklashtiriladi."),
    (34.14, 42.54, "Bu usulni ham o'ziga yarasha minusi bor: Membrana ishlashi uchun katta bosim, yaʼni koʻp elektr kerak, membrana esa vaqt oʻtib kirlanib qoladi."),
    (43.89, 44.78, "Misol uchun,"),
    (45.04, 50.21, "uydagi teskari osmos filtrlari ham 1 litr toza suv uchun taxminan 5 litr suvni"),
    (50.60, 52.14, "kanalizatsiyaga oqizib yuboradi."),
    (52.86, 53.56, "Hozirgicha,"),
    (54.59, 58.16, "biz iste'mol qilayotgan suv qanday jarayonlardan o'tib kelayotgani haqida"),
    (58.58, 61.88, "ozgina bo'lsa ham tanishtira olgan bo'lsam unda xursandman,"),
    (62.42, 64.63, "shunday ekan suvni qadriga yeting,"),
    (64.97, 67.43, "va har doimgidek bizni kuzatishda davom eting,"),
    (67.71, 73.43, "suv haqida eng sodda tilda tushuntirilgan faktlar va ma'lumotlarni yetkazishga harakat qilamiz."),
    (73.78, 76.60, "Keyingi videolarda ko'rishguncha xayr, salomat bo'ling."),
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
