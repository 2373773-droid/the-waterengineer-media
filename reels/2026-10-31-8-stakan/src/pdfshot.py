import subprocess, re, json
from html import unescape
PW = 2160
targets = {1: ["Drink at least eight glasses of water a day.", "rigorous proof for this counsel appears to be lacking."],
           3: ["1945 the Food and Nutrition Board", "A suitable allowance of water for adults is 2.5 liters daily",
               "Most of this quantity is contained in prepared foods."]}
out = {}
for pg, phr in targets.items():
    subprocess.run(["pdftoppm", "-f", str(pg), "-l", str(pg), "-png", "-scale-to-x", str(PW), "-scale-to-y", "-1", "valtin.pdf", f"scr/v{pg}"], check=True)
    x = subprocess.run(["pdftotext", "-f", str(pg), "-l", str(pg), "-bbox", "valtin.pdf", "-"], capture_output=True, text=True).stdout
    pw = float(re.search(r'<page width="([\d.]+)"', x).group(1)); s = PW / pw
    words = [(unescape(m.group(5)), *map(float, m.group(1, 2, 3, 4))) for m in re.finditer(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', x)]
    toks = [w[0] for w in words]
    for p in phr:
        pt = p.replace("“", "").replace("”", "").split()
        hit = None
        for i in range(len(toks)):
            seq = [t.strip("“”\"") for t in toks[i:i + len(pt)]]
            if [q.strip("“”\"") for q in pt] == seq: hit = i; break
        if hit is None: print("MISS", pg, p); continue
        ws = words[hit:hit + len(pt)]; lines = []
        for w in ws:   # merge words into line rects
            if lines and abs(lines[-1][1] - w[2]) < 3: lines[-1] = [lines[-1][0], lines[-1][1], max(lines[-1][2], w[3]), max(lines[-1][3], w[4])]
            else: lines.append([w[1], w[2], w[3], w[4]])
        out[f"{pg}:{p}"] = [[a * s, b * s, c * s, d * s] for a, b, c, d in lines]
        print(pg, p[:40], len(lines))
json.dump(out, open("scr/valtin_rects.json", "w"), indent=1)
